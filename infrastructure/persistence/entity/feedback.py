from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from infrastructure.persistence.db_session import SqlAlchemyBase
from infrastructure.persistence.entity.sending import Sending


class Feedback(SqlAlchemyBase):
    __tablename__ = 'feedbacks'

    distributor_id: Mapped[int] = mapped_column(primary_key=True)
    sending_id: Mapped[int] = mapped_column(ForeignKey(Sending.distributor_id))
