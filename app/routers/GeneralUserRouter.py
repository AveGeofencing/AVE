from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.APIKeys import get_api_key

from ..services import UserService
from ..database.database import get_db_session
from ..schemas.UserSchema import UserCreateModel

GeneralUserRouter = APIRouter(prefix="/user", tags=["General User"])
DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
api_key_dependency = Annotated[str, Depends(get_api_key)]


@GeneralUserRouter.post("/create_user")
async def create_new_user(user: UserCreateModel, session: DBSessionDep, _: api_key_dependency):
    user_service = UserService(session)
    created_message = await user_service.create_new_user(user)

    return created_message
