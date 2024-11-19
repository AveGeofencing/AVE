from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database.database import Base


class Geofence(Base):
    __tablename__ = "Geofences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fence_code: Mapped[str] = mapped_column(String(15), unique=True)
    name: Mapped[str] = mapped_column(String(60))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    radius: Mapped[float] = mapped_column(Float)
    fence_type: Mapped[str] = mapped_column(String(60))
    start_time: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True))
    end_time: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True))
    status: Mapped[str] = mapped_column(String(60))
    time_created: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True))

    # foreign key
    creator_matric: Mapped[str] = mapped_column(String(50), ForeignKey("Users.user_matric"))

    creator = relationship("User", back_populates="geofences")
