from typing import Annotated
from fastapi import Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth.sessions.SessionHandler import SessionHandler
from ..database.database import get_db_session

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_session_id(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token is None:
        raise HTTPException(status_code=401, detail="Session has expired. Log in again")

    return session_token


async def authenticate_user_by_session_token(
    session: DBSessionDep, session_token: str = Depends(get_session_id)
):
    if not session_token:
        raise HTTPException(status_code=401, detail="No session token provided")

    sessionHandler = SessionHandler(session)
    user_data = await sessionHandler.get_user_by_session(session_token)

    return user_data


async def authenticate_student_user(
    user_data: dict = Depends(authenticate_user_by_session_token),
):
    if not user_data:
        return "No user data provided"

    if user_data["role"] != "student":
        raise HTTPException(
            status_code=401, detail="Endpoint can only be accessed by students"
        )

    return user_data


async def authenticate_admin_user(
    user_data: dict = Depends(authenticate_user_by_session_token),
):
    if not user_data:
        return "No user data provided"
    if user_data["role"] != "admin":
        raise HTTPException(
            status_code=401, detail="Endpoint can only be accessed by admins"
        )

    return user_data
