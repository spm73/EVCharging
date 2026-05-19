from sqlalchemy import String, Numeric, Enum, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from decimal import Decimal
from enum import Enum

class CPStatus(Enum):
    ACTIVE = 'Active'
    STOPPED = 'Stopped'
    SUPPLYING = 'Supplying'
    BROKEN_DOWN = 'Broken Down'
    DISCONNECTED = 'Disconnected'
    
class Base(DeclarativeBase):
    pass

class CP(Base):
    __tablename__ = 'CP'
    
    id: Mapped[str] = mapped_column(String(6), primary_key=True)
    location: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    status: Mapped[CPStatus] = mapped_column(Enum(CPStatus), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    