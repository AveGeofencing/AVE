from sqlalchemy import TIMESTAMP, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database.database import Base
from datetime import datetime
from zoneinfo import ZoneInfo

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("users.user_matric"), nullable=False)
    token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    # Uncomment this if needed later
    # ip_address: Mapped[str] = mapped_column(String(45), nullable=True)  # IPv4/IPv6

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        onupdate=func.now(),
        nullable=False
    )

    is_expired: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Define relationship with User model
    user = relationship("User", back_populates="sessions")