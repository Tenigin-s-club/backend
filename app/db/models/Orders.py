from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from app.db.configuration import Base


class Table_Orders(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[str] = mapped_column(ForeignKey("users.id"))
    wait: Mapped[bool] = mapped_column(default=False)
    train_id: Mapped[int]
    wagon_id: Mapped[int]
    seat_ids: Mapped[int]