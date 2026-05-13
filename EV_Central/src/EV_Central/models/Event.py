from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .Base import Base

class Event(Base):
    __tablename__ = 'EVENT'

    id: Mapped[int] = mapped_column(primary_key=True)
    ip: Mapped[str | None] = mapped_column(String(15))
    action: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)