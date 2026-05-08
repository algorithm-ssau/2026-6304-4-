from sqlalchemy.orm import Mapped, mapped_column
from database.database import Base

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
