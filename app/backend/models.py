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
