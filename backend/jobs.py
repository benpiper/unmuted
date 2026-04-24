"""Async job queue for long-running tasks without external broker."""

import asyncio
import os
import uuid
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Callable

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job lifecycle states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """Represents a long-running job with progress tracking."""
    job_id: str
    status: JobStatus = JobStatus.PENDING
    progress: int = 0
    result: Optional[Any] = None
    error: Optional[str] = None
    _cancelled: bool = field(default=False, repr=False)

    def cancel(self):
        """Mark job for cancellation."""
        self._cancelled = True

    def is_cancelled(self) -> bool:
        """Check if job has been cancelled."""
        return self._cancelled


class JobManager:
    """
    In-process job queue using ThreadPoolExecutor.
    Stores job state in-memory without requiring external broker.
    """

    def __init__(self, max_workers: int = 2):
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        logger.info(f"JobManager initialized with max_workers={max_workers}")

    def create_job(self) -> Job:
        """Create a new job and track it."""
        job = Job(job_id=str(uuid.uuid4()))
        with self._lock:
            self._jobs[job.job_id] = job
        logger.debug(f"Created job {job.job_id}")
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Retrieve job by ID."""
        return self._jobs.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """Mark job for cancellation if it's pending or running."""
        job = self._jobs.get(job_id)
        if job and job.status in (JobStatus.PENDING, JobStatus.RUNNING):
            job.cancel()
            logger.info(f"Job {job_id} marked for cancellation")
            return True
        return False

    async def submit(self, job: Job, fn: Callable, *args) -> None:
        """
        Submit a function to run asynchronously in thread pool.
        Function receives job as first argument for progress updates.

        Args:
            job: Job instance to track
            fn: Callable(job, *args) to execute
            args: Additional arguments to pass to fn
        """
        loop = asyncio.get_running_loop()
        job.status = JobStatus.RUNNING
        logger.info(f"Job {job.job_id} submitted to executor")

        def _run():
            try:
                result = fn(job, *args)
                if not job.is_cancelled():
                    job.progress = 100
                    job.status = JobStatus.COMPLETE
                    job.result = result
                    logger.info(f"Job {job.job_id} completed successfully")
                else:
                    job.status = JobStatus.CANCELLED
                    logger.info(f"Job {job.job_id} was cancelled")
            except Exception as e:
                logger.error(
                    f"Job {job.job_id} failed: {str(e)}",
                    exc_info=True,
                    extra={"job_id": job.job_id},
                )
                job.status = JobStatus.FAILED
                job.error = str(e)

        loop.run_in_executor(self._executor, _run)

    def shutdown(self):
        """Shutdown the thread pool executor."""
        logger.info("Shutting down JobManager executor")
        self._executor.shutdown(wait=False)


job_manager = JobManager(max_workers=int(os.getenv("MAX_JOB_WORKERS", "2")))
