from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base, Form


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    form_id: Mapped[int] = mapped_column(ForeignKey(Form.id, ondelete="CASCADE"))
    data: Mapped[dict] = mapped_column(JSON)

    form: Mapped[Form] = relationship(Form, lazy="joined")
