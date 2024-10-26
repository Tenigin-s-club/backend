from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4

from app.db.configuration import Base


class Wait(Base):
    __tablename__ = "wait"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    start_point: Mapped[str]
    end_point: Mapped[str]