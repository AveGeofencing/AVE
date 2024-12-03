from datetime import datetime
from sqlalchemy import (
    TIMESTAMP,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.database import Base


class AttendanceRecord(Base):
    __tablename__ = "attendancerecords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_matric: Mapped[str] = mapped_column(String(50), ForeignKey("users.user_matric"))
    fence_code: Mapped[str] = mapped_column(String(15), ForeignKey("geofences.fence_code"))
    geofence_name: Mapped[str] = mapped_column(String(60))
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    matric_fence_code: Mapped[str] = mapped_column(String(60))

    user = relationship("User", back_populates="attendances")
    geofence = relationship("Geofence", back_populates="student_attendances")