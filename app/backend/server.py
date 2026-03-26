import uuid
from collections.abc import AsyncGenerator

from backend.models import NoteModel, RegionModel
from fastapi import APIRouter, Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

engine: AsyncEngine = create_async_engine("sqlite+aiosqlite:///my_database.db")
session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with session_maker() as session:
        yield session


app = FastAPI()

router = APIRouter()


class Note(BaseModel):
    title: str
    description: str
    metadata: dict | None = None


@router.post("/notes")
async def create_note(req: Note, db_session: AsyncSession = Depends(get_async_session)):
    db_session.add(NoteModel(id=str(uuid.uuid4()), text=req.title))
    await db_session.commit()
    return req


@router.get("/notes")
async def get_notes(db_session: AsyncSession = Depends(get_async_session)):
    notes = list(await db_session.scalars(select(NoteModel)))
    return notes


@router.get("/regions")
async def get_regions(db_session: AsyncSession = Depends(get_async_session)):
    regions = list(await db_session.scalars(select(RegionModel)))
    return regions


app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, reload=True)
