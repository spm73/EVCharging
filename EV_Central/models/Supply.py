from sqlalchemy import ForeignKey, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from .Base import Base

class Supply(Base):
    __tablename__ = 'SUPPLY'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    price: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    consumption: Mapped[int | None]
    is_done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    cp_id: Mapped[str] = mapped_column(ForeignKey("CP.id"), nullable=False)
    driver_id: Mapped[str] = mapped_column(ForeignKey("DRIVER.id"), nullable=False)
    cp: Mapped["CP"] = relationship(back_populates="supplies")
    driver: Mapped["Driver"] = relationship(back_populates="supplies")
    