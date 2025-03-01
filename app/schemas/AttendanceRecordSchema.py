from pydantic import BaseModel


class AttendanceRecordModel(BaseModel):
    lat: float
    long: float
    fence_code: str
