import uuid
from zoneinfo import ZoneInfo
import logging

from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from ...repositories import SessionRepository
from passlib.context import CryptContext
from ...utils.config import settings

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
WANT_SINGLE_SIGNIN_FLAG = settings.WANT_SINGLE_SIGNIN

logger = logging.getLogger("uvicorn")


class SessionHandler:
    def __init__(self, db_session: AsyncSession):
        self.SESSION_TIMEOUT_MINUTES = 24 * 60
        self.sessionRepository = SessionRepository(db_session=db_session)

    async def get_user_by_session(self, session_token):
        session = await self.sessionRepository.get_user_session_by_token(session_token)

        if session and session.user:
            return {
                "user_matric": session.user.user_matric,
                "email": session.user.email,
                "username": session.user.username,
                "role": session.user.role,
            }

        return None

    async def get_user_session_by_matric(self, user_matric: str):
        existing_user_session = await self.sessionRepository.get_user_session_by_matric(
            user_matric
        )
        return existing_user_session

    async def create_new_session(self, user_matric: str):
        existing_user_session = await self.get_user_session_by_matric(user_matric)
        if existing_user_session:
            if WANT_SINGLE_SIGNIN_FLAG:
                raise HTTPException(
                    status_code=400,
                    detail=f"Already logged in. Sign out of other devices before logging in again",
                )

            return existing_user_session.token

        NOW = datetime.now(ZoneInfo("UTC"))

        EXPIRES_AT = NOW + timedelta(days=1)
        session_token = str(uuid.uuid4())  # Generate a unique session token

        token = await self.sessionRepository.create_new_session(
            session_token=session_token,
            EXPIRES_AT=EXPIRES_AT,
            user_matric=user_matric,
            created_at=NOW,
            updated_at=NOW,
        )
        return token

    async def deactivate_session(self, session_token):
        session_state = await self.sessionRepository.get_user_session_by_token(
            session_token
        )
        if session_state is None:
            raise HTTPException(status_code=404, detail="Token expired or invalid")

        if session_state.is_expired:
            raise HTTPException(status_code=401, detail="Session has expired")

        try:
            await self.sessionRepository.deactivate_session(session_token)
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail=f"Failed to deactivate session")

        return "Logged out successfully"

    async def login(self, user_matric: str, password: str, email: str = None):
        existing_user = await self.sessionRepository.get_user_by_email_or_matric(
            email=email, matric=user_matric
        )
        if not existing_user:
            raise HTTPException(
                status_code=400, detail="User not found. Please sign up"
            )
        if not bcrypt_context.verify(password, existing_user.hashed_password):
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )

        session_token = await self.create_new_session(
            user_matric=existing_user.user_matric
        )

        return {
            "message": "Successfully logged in",
            "session_token": session_token,
            "username": existing_user.username,
            "role": existing_user.role,
        }
