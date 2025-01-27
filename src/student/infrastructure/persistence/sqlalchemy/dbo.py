from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.db.pg_sqlalchemy.connection import BaseSqlModel


class StudentDbo(BaseSqlModel):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fisrt_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    identity_kind: Mapped[str] = mapped_column()
    identity_code: Mapped[str] = mapped_column()
    age: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column()

    __table_args__ = (
        UniqueConstraint("identity_kind", "identity_code", name="uq_identity_idx"),
    )
