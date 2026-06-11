from sqlalchemy import ForeignKey, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from EV_Central.models.Base import Base

class Supply(Base):
    __tablename__ = 'SUPPLY'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    price: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    consumption: Mapped[int | None]
    is_done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    cp_id: Mapped[str | None] = mapped_column(ForeignKey("CP.id", ondelete="SET NULL"), nullable=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("DRIVER.id"), nullable=False)
    cp: Mapped["CP"] = relationship(back_populates="supplies")
    driver: Mapped["Driver"] = relationship(back_populates="supplies")
    