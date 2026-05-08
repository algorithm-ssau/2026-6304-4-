# from sqlalchemy import ForeignKey
# from sqlalchemy.orm import Mapped, mapped_column
# from database.database import Base


# class ApiPolling(Base):
#     __tablename__ = "api_pollings"

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
#     user_id: Mapped[int] = mapped_column(ForeignKey())
#     thread_id: Mapped[int] = mapped_column()
