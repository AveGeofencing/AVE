from typing import Annotated
from fastapi import APIRouter, HTTPException, Request

from app.auth.sessions.SessionHandler import SessionHandler
from ..services import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, BackgroundTasks
from ..database import get_db_session
from ..dependencies.sessionDependencies import authenticate_admin_user, authenticate_student_user
StudentRouter = APIRouter(
    prefix = "/user/student",
    tags=["Users/Student"]
)

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
authenticate_student = Annotated[dict, Depends(authenticate_student_user)]
authenticate_admin = Annotated[dict, Depends(authenticate_admin_user)]

@StudentRouter.post("/forgot_password")
async def forgot_password(session: DBSessionDep, student_email: str, background_tasks: BackgroundTasks):
    userService = UserService(session)
    await userService.send_reset_password_email(user_email = student_email, background_tasks = background_tasks)
    return {"message": "Password reset email has been sent successfully"}


@StudentRouter.post("/reset_password")
async def reset_password(new_password, token:str, session: DBSessionDep, background_tasks: BackgroundTasks):

    userService= UserService(session)
    message = await userService.change_password(new_password, token, background_tasks)
    return message