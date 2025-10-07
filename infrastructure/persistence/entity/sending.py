from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from infrastructure.persistence.db_session import SqlAlchemyBase
from infrastructure.persistence.entity.message import Message


class Sending(SqlAlchemyBase):
    __tablename__ = 'sending'

    distributor_id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int]
    message_id: Mapped[int] = mapped_column(ForeignKey(Message.id))
    message: Mapped[Message] = relationship()
    is_processed: Mapped[bool]
    reminder_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey(distributor_id))
    reminder_to: Mapped[Optional["Sending"]] = relationship(remote_side=distributor_id)
