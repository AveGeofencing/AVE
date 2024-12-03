from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.APIKeys import get_api_key

from ..services import UserService
from ..database.database import get_db_session
from ..schemas.UserSchema import UserCreateModel

GeneralUserRouter = APIRouter(prefix="/users", tags=["General User"])
DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
api_key_dependency = Annotated[str, Depends(get_api_key)]


@GeneralUserRouter.post("/create_user")
async def create_new_user(user: UserCreateModel, session: DBSessionDep, _: api_key_dependency):
    user_service = UserService(session)
    created_message = await user_service.create_new_user(user)

    return created_message

@GeneralUserRouter.post("/forgot_password")
async def forgot_password(session: DBSessionDep, student_email: str, background_tasks: BackgroundTasks):
    userService = UserService(session)
    await userService.send_reset_password_email(user_email = student_email, background_tasks = background_tasks)
    return {"message": "Password reset email has been sent successfully"}


@GeneralUserRouter.post("/reset_password")
async def reset_password(new_password, token:str, session: DBSessionDep, background_tasks: BackgroundTasks):

    userService= UserService(session)
    message = await userService.change_password(new_password, token, background_tasks)
    return message