from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from EV_Central.models.Base import Base

class Driver(Base):
    __tablename__ = 'DRIVER'

    id: Mapped[str] = mapped_column(String(9), primary_key=True)
    supplies: Mapped[list["Supply"]] = relationship(back_populates="driver")