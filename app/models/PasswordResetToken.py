from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database.database import Base


class PasswordResetToken(Base):
    __tablename__ = "PasswordResetToken"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("Users.user_matric"), nullable=False)  # Link to the user
    token: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)  # The reset token
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # Token expiration time
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)  # Whether the token has been used

    user = relationship("User", back_populates="password_reset_tokens")
