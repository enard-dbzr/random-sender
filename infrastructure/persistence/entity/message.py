from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from infrastructure.persistence.db_session import SqlAlchemyBase


class Message(SqlAlchemyBase):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    buttons: Mapped[list[str]] = mapped_column(ARRAY(String))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String))
