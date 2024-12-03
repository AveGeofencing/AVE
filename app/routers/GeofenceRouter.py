from datetime import datetime
from typing import Annotated, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import GeofenceCreateModel
from ..database import get_db_session
from ..dependencies.sessionDependencies import authenticate_admin_user
from ..services.GeofenceService import GeofenceService

GeofenceRouter = APIRouter(prefix="/geofences", tags=["Geofences"])
DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
authenticate_admin = Annotated[dict, Depends(authenticate_admin_user)]


@GeofenceRouter.post("/create_geofence")
async def create_geofence(
    geofence: GeofenceCreateModel, session: DBSessionDep, admin: authenticate_admin
):
    geofenceService = GeofenceService(session)
    return await geofenceService.create_geofence(geofence.name, admin["user_matric"], geofence)

@GeofenceRouter.get("/get_geofence")
async def get_geofence_details(
    course_title: str, date: datetime, session: DBSessionDep, _: authenticate_admin
):
    """Returns details of geofence for a given course title"""
    geofenceService = GeofenceService(session)
    geofence = await geofenceService.get_geofence(course_title, date)
    return {"geofence": geofence}

@GeofenceRouter.get("/get_geofences")
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
