from datetime import datetime
from typing import Annotated, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import GeofenceCreateModel, AttendanceRecordModel
from ..database import get_db_session
from ..dependencies.sessionDependencies import (
    authenticate_admin_user,
    authenticate_student_user,
    authenticate_user_by_session_token,
)
from ..services import GeofenceService, UserService

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
authenticate_admin = Annotated[dict, Depends(authenticate_admin_user)]
authenticate_student = Annotated[dict, Depends(authenticate_student_user)]


def get_geofence_service(session: DBSessionDep):
    return GeofenceService(session)


GeofenceRouter = APIRouter(prefix="/geofence", tags=["Geofences"])


@GeofenceRouter.post("/create_geofence")
async def create_geofence(
    geofence: GeofenceCreateModel, session: DBSessionDep, admin: authenticate_admin
):
    geofenceService = GeofenceService(session)
    return await geofenceService.create_geofence(admin["user_matric"], geofence)


@GeofenceRouter.get("/get_geofence", dependencies=[Depends(authenticate_admin_user)])
async def get_geofence_details(
    course_title: str, date: datetime, session: DBSessionDep
):
    """Returns details of geofence for a given course title"""
    geofenceService = GeofenceService(session)
    geofence = await geofenceService.get_geofence(course_title, date)
    return {"geofence": geofence}


@GeofenceRouter.get(
    "/get_geofences", dependencies=[Depends(authenticate_user_by_session_token)]
)
async def get_geofences(session: DBSessionDep):
    """Returns all the geofences created"""
    geofenceService = GeofenceService(session)
    geofences = await geofenceService.get_all_geofences()
    return {"geofences": geofences}


@GeofenceRouter.get("/get_my_geofences")
async def get_my_geofences_created(session: DBSessionDep, admin: authenticate_admin):
    """Returns a list of all geofences created by the given admin"""
    geofenceService = GeofenceService(session)
    geofences = await geofenceService.get_all_geofences(admin["user_matric"])
    return {"geofences": geofences}


@GeofenceRouter.post("/record_attendance")
async def record_attendance(
    session: DBSessionDep,
    attendance: AttendanceRecordModel,
    student: authenticate_student,
):
    geofenceService = GeofenceService(session)
    userService = UserService(session)
    recorded_attendance_message = geofenceService.record_geofence_attendance(
        user_matric=student["user_matric"],
        attendance=attendance,
        userService=userService,
    )

    return await recorded_attendance_message


@GeofenceRouter.get("/get_attendances")
async def get_geofence_attendances(
    course_title: str, date: datetime, admin: authenticate_admin, session: DBSessionDep
):
    """Returns the attendances for a given course"""
    geofenceService = GeofenceService(session)
    attendances = await geofenceService.get_geofence_attendances(
        course_title, date, admin["user_matric"]
    )

    return {"attendance": attendances}


@GeofenceRouter.put("/deactivate")
async def deactivate_geofence(
    session: DBSessionDep, admin: authenticate_admin, geofence_name: str, date: datetime
):
    geofenceService = GeofenceService(session)
    deactivate_message = await geofenceService.deactivate_geofence(
        geofence_name, date, admin["user_matric"]
    )

    return deactivate_message
