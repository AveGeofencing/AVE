from datetime import datetime, timezone
import logging
import random
import string
from typing import Optional
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Geofence
from app.schemas.GeofenceSchema import GeofenceCreateModel

from ..repositories import GeofenceRepository

logger = logging.getLogger("uvicorn")


class GeofenceService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_geofence(
        self,
        course_title: str,
        creator_matric: str,
        geofence: GeofenceCreateModel,
    ):  # SINGULAR
        characters = string.ascii_letters + string.digits
        fence_code = "".join(random.choice(characters) for _ in range(6)).lower()

        geofenceRepository = GeofenceRepository(self.session)
        existing_geofence = await geofenceRepository.get_geofence(
            course_title, geofence.start_time
        )
        if existing_geofence:
            raise HTTPException(
                status_code=400,
                detail="Geofence with this name already exists for today",
            )

        start_time = geofence.start_time.replace(tzinfo=ZoneInfo("Africa/Lagos"))
        end_time = geofence.end_time.replace(tzinfo=ZoneInfo("Africa/Lagos"))

        start_time_utc = start_time.astimezone(ZoneInfo("UTC"))
        end_time_utc = end_time.astimezone(ZoneInfo("UTC"))
        NOW = datetime.now(ZoneInfo("UTC"))

        if start_time_utc >= end_time_utc:
            raise HTTPException(
                status_code=400,
                detail="Invalid duration for geofence. Please adjust duration and try again.",
            )

        if end_time_utc < datetime.now(tz=ZoneInfo("UTC")):
            raise HTTPException(
                status_code=400, detail="End time cannot be in the past."
            )

        new_geofence = Geofence(
            fence_code=fence_code,
            name=geofence.name,
            creator_matric=creator_matric,
            latitude=geofence.latitude,
            longitude=geofence.longitude,
            radius=geofence.radius,
            fence_type=geofence.fence_type,
            start_time=start_time_utc,
            end_time=end_time_utc,
            status=(
                "active"
                if start_time_utc
                <= NOW
                <= end_time_utc
                else "scheduled"
            ),
            time_created = NOW
        )

        added_geofence = await geofenceRepository.create_geofence(new_geofence)

        return {"Code": fence_code, "name": added_geofence.name}

    async def get_all_geofences(self, user_id: Optional[str] = None):  # PLURAL
        geofenceRepo = GeofenceRepository(self.session)
        if user_id is not None:
            geofences = await geofenceRepo.get_all_geofences_by_user(user_id)

        geofences = await geofenceRepo.get_all_geofences()

        if not geofences:
            raise HTTPException(status_code=404, detail="No geofences found")
        return geofences

    async def get_geofence(self, course_title: str, date: datetime):  # SINGULAR
        geofenceRepo = GeofenceRepository(self.session)
        try:
            geofence = await geofenceRepo.get_geofence(course_title, date)
            if geofence:
                print(geofence.start_time.tzinfo)
                # geofence.start_time = geofence.start_time.astimezone(ZoneInfo("Africa/Lagos"))
                # geofence.end_time = geofence.end_time.astimezone(ZoneInfo("Africa/Lagos"))
                return geofence
            else:
                raise HTTPException(status_code=404, detail="No geofence found")
        except Exception as e:
            logger.error(f"Something went wrong in fetching geofence")
            logger.error(str(e))

            raise HTTPException(
                status_code=500, detail="Internal Error. Contact admin."
            )

    async def get_geofence_attendances(
        self, course_title: str, date: datetime, user_id: str
    ):
        geofence = await self.get_geofence(course_title, date)
        if geofence.creator_matric != user_id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this geofence's attendance.",
            )

        try:
            if geofence and geofence.student_attendances:
                return geofence.student_attendances

            else:
                raise HTTPException(status_code=404, detail="No attendances yet.")

        except Exception as e:
            logger.error(f"Something went wrong in fetching geofence attendances")
            logger.error(str(e))

            raise HTTPException(
                status_code=500, detail="Internal error. Contact admin."
            )
