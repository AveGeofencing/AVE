from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import and_, func
from sqlalchemy.orm import selectinload
from ..models import Geofence, AttendanceRecord

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


class GeofenceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_geofence(self, geofence: Geofence):
        new_geofence = geofence

        self.session.add(new_geofence)
        await self.session.commit()
        await self.session.refresh(new_geofence)

        return new_geofence

    async def get_all_geofences(self):
        stmt = select(Geofence)
        result = await self.session.execute(stmt)

        geofences = result.scalars().all()
        return geofences

    async def get_all_geofences_by_user(self, user_id: str):
        stmt = select(Geofence).filter(Geofence.creator_matric == user_id)
        result = await self.session.execute(stmt)
        geofence_by_user = result.scalars().all()

        return geofence_by_user

    async def get_geofence(self, course_title: str, date: datetime) -> Geofence:
        stmt = (
            select(Geofence)
            .options(selectinload(Geofence.student_attendances))
            .filter(
                and_(
                    Geofence.name == course_title,
                    func.date(Geofence.start_time) == date.date(),
                )
            )
        )

        result = await self.session.execute(stmt)
        geofence = result.scalars().one_or_none()

        return geofence

    async def get_geofence_by_fence_code(self, fence_code: str):
        stmt = (
            select(Geofence)
            .options(selectinload(Geofence.student_attendances))
            .filter(Geofence.fence_code == fence_code)
        )
        result = await self.session.execute(stmt)
        geofence = result.scalars().one_or_none()
        return geofence

    async def record_geofence_attendance(self, attendance: AttendanceRecord):
        self.session.add(attendance)
        await self.session.commit()
        await self.session.refresh(attendance)

        return attendance

    async def get_attendance_record(self, matric_fence_code: str):
        stmt = select(AttendanceRecord).filter(
            AttendanceRecord.matric_fence_code == matric_fence_code
        )
        result = await self.session.execute(stmt)
        attendance_record = result.scalars().one_or_none()

        return attendance_record
