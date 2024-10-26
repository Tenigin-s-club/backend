from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum, ARRAY, String

from app.db.configuration import Base
from uuid import UUID
from enum import Enum as BaseEnum

class OrderStatus(BaseEnum):
    RESERVE: str = "reserve"
    BUY: str = "buy"

class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), nullable=True)
    train_id: Mapped[int]
    wagon_id: Mapped[int]
    seat_ids: Mapped[int]
    departure_date: Mapped[str]
    arriving_data: Mapped[str]
    start_point: Mapped[str]
    finish_point: Mapped[str]
    type_wagon: Mapped[str]
    type_shelf: Mapped[str]
    number_wagon: Mapped[int]
    number_seat: Mapped[int]
    stops: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)

 


    
    
    
