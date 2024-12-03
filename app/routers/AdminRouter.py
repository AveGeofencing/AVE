from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, HTTPException, Request

from app.auth.sessions.SessionHandler import SessionHandler
from ..services import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from ..database import get_db_session
from ..dependencies.sessionDependencies import authenticate_admin_user

AdminRouter = APIRouter(
    prefix = "/users/admin",
    tags=["Users/Admin"]
)

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
authenticate_admin = Annotated[dict, Depends(authenticate_admin_user)]

@AdminRouter.get("/{email}")
async def get_user_by_email(email:str, session: DBSessionDep, _: authenticate_admin):
    # print(user_data)
    userService = UserService(session)
    return await userService.get_user_by_email_or_matric(email)
