from sqlalchemy import String, Numeric, Enum, Float, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from EV_Central.models.Base import Base
from EV_Central.models.CPStatus import CPStatus

class CP(Base):
    __tablename__ = 'CP'
    
    id: Mapped[str] = mapped_column(String(6), primary_key=True)
    location: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    status: Mapped[CPStatus] = mapped_column(Enum(CPStatus), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    cipher_key: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    
    supplies: Mapped[list["Supply"]] = relationship(back_populates="cp")