from typing import Annotated
from fastapi import APIRouter, HTTPException, Request

from app.auth.sessions.SessionHandler import SessionHandler
from ..services import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from ..database import get_db_session
from ..dependencies.sessionDependencies import authenticate_admin_user, authenticate_student_user

StudentRouter = APIRouter(
    prefix = "/user/student",
    tags=["Users/Student"]
)

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
authenticate_student = Annotated[dict, Depends(authenticate_student_user)]


