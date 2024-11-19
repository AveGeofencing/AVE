from pydantic import BaseModel, Field
from datetime import datetime
from zoneinfo import ZoneInfo

class GeofenceCreateModel(BaseModel):
    name: str
    latitude: float
    longitude: float
    radius: float
    fence_type: str
    start_time: datetime = Field(default_factory=lambda: datetime.now(tz=ZoneInfo("Africa/Lagos")))
    end_time: datetime = Field(default_factory=lambda: datetime.now(tz=ZoneInfo("Africa/Lagos")))


    class Config:
        from_attributes = True