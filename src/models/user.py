from sqlalchemy.orm import Mapped, mapped_column
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    golden_token: Mapped[str] = mapped_column()

    is_polling: Mapped[bool] = mapped_column()

