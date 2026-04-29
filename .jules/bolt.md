## 2024-04-26 - Optimize timestamp parsing in React video playback
**Learning:** React components executing inside high-frequency event handlers (like `<video onTimeUpdate>`) can suffer significant overhead from redundant string processing (like parsing timestamps `.split(':')`).
**Action:** Use `React.useMemo` to pre-calculate and cache derived data (like parsed timestamps) so that high-frequency handlers only perform fast numerical lookups.

## 2024-05-18 - Offload blocking VLM queries to threadpool in endpoints
**Learning:** FastAPI endpoints defined with `def` block the main event loop, causing severe latency for all other concurrent requests when calling external services like Vision-Language Models (VLM).
**Action:** Always define VLM-calling endpoints with `async def` and wrap the synchronous logic (including file reads and external API calls) in a local helper function executed via `await starlette.concurrency.run_in_threadpool(...)`.
