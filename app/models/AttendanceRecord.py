from sqlalchemy import (
    TIMESTAMP,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import mapped_column, Mapped
from app.database.database import Base


class AttendanceRecord(Base):
    __tablename__ = "AttendanceRecords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_matric: Mapped[str] = mapped_column(String(50), ForeignKey("Users.user_matric"))
    fence_code: Mapped[str] = mapped_column(String(15), ForeignKey("Geofences.fence_code"))
    geofence_name: Mapped[str] = mapped_column(String(60))
    timestamp: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True))
    matric_fence_code: Mapped[str] = mapped_column(String(60))
