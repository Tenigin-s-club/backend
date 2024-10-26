from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.configuration import Base


class Table_Users(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    login: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    fio: Mapped[str]

    