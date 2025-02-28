from pydantic import BaseModel, Field, AwareDatetime



class GeofenceCreateModel(BaseModel):
    name: str
    latitude: float
    longitude: float
    radius: float
    fence_type: str
    start_time: AwareDatetime
    end_time: AwareDatetime

    class Config:
        from_attributes = True
