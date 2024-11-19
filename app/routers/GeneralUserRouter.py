from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..services import UserService
from ..database.database import get_db_session
from ..schemas.UserSchema import UserCreateModel

GeneralUserRouter = APIRouter(prefix="/user", tags=["General User"])
DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@GeneralUserRouter.post("/create_user")
async def create_new_user(user: UserCreateModel, session: DBSessionDep):
    user_service = UserService(session)
    created_message = await user_service.create_new_user(user)

    return created_message
