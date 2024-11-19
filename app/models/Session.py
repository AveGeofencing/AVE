from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database.database import Base
from datetime import datetime
from zoneinfo import ZoneInfo

class Session(Base):
    __tablename__ = "Sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("Users.user_matric"), nullable=False)
    token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    # Uncomment this if needed later
    # ip_address: Mapped[str] = mapped_column(String(45), nullable=True)  # IPv4/IPv6

    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    is_expired: Mapped[bool] = mapped_column(
        Boolean,
        server_default="FALSE",
        nullable=False
    )
    
    # Define relationship with User model
    user = relationship("User", back_populates="sessions")