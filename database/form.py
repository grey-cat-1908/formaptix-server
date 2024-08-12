from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base, User


class Form(Base):
    __tablename__ = "forms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    owner_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    data: Mapped[dict] = mapped_column(JSON)
