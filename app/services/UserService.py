from sqlalchemy import select

from ..auth.sessions.SessionHandler import SessionHandler
from ..schemas.UserSchema import UserCreateModel
from ..repositories.UserRepository import UserRepository

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

    async def get_user_by_email_or_matric(self, email: str = None, matric: str = None):
        user = await self.repository.get_user_by_email_or_matric(email, matric)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {"user_username": user.username,
                "user_matric": user.user_matric,
                "user_email": user.email,
                "user_role": user.role,
                }

    async def create_new_user(self, user_data: UserCreateModel):

        existing_user = await self.repository.get_user_by_email_or_matric(
            email=user_data.email, matric=user_data.user_matric
        )

        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        try:
            hashed_password = bcrypt_context.hash(user_data.password)
            user_create_message = await self.repository.create_new_user(
                user_data, hashed_password
            )
        except:
            raise HTTPException(status_code=500, detail="Internal Server Error")

        return user_create_message

    

    