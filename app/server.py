from typing import AsyncGenerator
import uuid
from fastapi import Depends, FastAPI, APIRouter
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class NoteModel(Base):
    __tablename__ = "nodes"

    id: Mapped[str] = mapped_column(primary_key=True)
    x: Mapped[float] = mapped_column()
    y: Mapped[float] = mapped_column()
    color: Mapped[str] = mapped_column()
    #    title: Mapped[str] = mapped_column()
    #   description: Mapped[str] = mapped_column()
    text: Mapped[str] = mapped_column()


class LinkModel(Base):
    __tablename__ = "links"

    id: Mapped[str] = mapped_column(primary_key=True)
    note1_id: Mapped[str] = mapped_column()
    note2_id: Mapped[str] = mapped_column()


class RegionModel(Base):
    __tablename__ = "regions"

    id: Mapped[str] = mapped_column(primary_key=True)
    x: Mapped[float] = mapped_column()
    y: Mapped[float] = mapped_column()
    height: Mapped[float] = mapped_column()
    width: Mapped[float] = mapped_column()
    color: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()


engine: AsyncEngine = create_async_engine("sqlite+aiosqlite:///my_database.db")
session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
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


app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, reload=True)
