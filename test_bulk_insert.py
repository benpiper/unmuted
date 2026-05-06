import asyncio
import sys
sys.path.append('backend')
from database import get_db, async_session_factory, engine, Base
from models import Project, TranscriptSegment
from sqlalchemy import insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

async def test():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        project = Project(title="Test", directory_path="/tmp/test", owner_id="test_owner")
        db.add(project)
        await db.commit()

        # Add segments via bulk insert
        await db.execute(
            insert(TranscriptSegment),
            [
                {
                    "project_id": project.id,
                    "timestamp": "00:00:00",
                    "narration": "Hello",
                    "overlay": "World",
                    "order": 0
                },
                {
                    "project_id": project.id,
                    "timestamp": "00:00:01",
                    "narration": "Hello 2",
                    "overlay": "World 2",
                    "order": 1
                }
            ]
        )
        await db.commit()

        result = await db.execute(select(TranscriptSegment))
        segments = result.scalars().all()
        print(f"Found {len(segments)} segments")

if __name__ == "__main__":
    asyncio.run(test())
