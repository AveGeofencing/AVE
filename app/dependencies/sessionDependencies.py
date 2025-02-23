from typing import Annotated
from fastapi import Depends, Request, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth.sessions.SessionHandler import SessionHandler
from ..database.database import get_db_session

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_session_id(db_session: DBSessionDep, request: Request, response: Response, user_matric = None):
    session_token = request.cookies.get("session_token")

    sessionHandler = SessionHandler(db_session)
    if session_token is None:
        if sessionHandler.get_user_session_by_matric(user_matric):
            response.set_cookie(
                key="session_token",
                value=session_token,
                httponly=True,
                secure=True,  # Set to True for HTTPS
                max_age=24 * 60 * 60,
            )
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
