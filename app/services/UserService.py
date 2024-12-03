import logging
from typing import Optional
from zoneinfo import ZoneInfo
from app.repositories import PasswordResetTokenRepository, SessionRepository
from ..schemas.UserSchema import UserCreateModel
from ..repositories.UserRepository import UserRepository
from .EmailService import send_email

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks, HTTPException
from passlib.context import CryptContext
from pydantic import EmailStr
from datetime import timedelta, datetime
from jose import JWTError, jwt
from ..utils.config import settings

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger("uvicorn")


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

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

    async def get_user_by_email_or_matric(self, email: str = None, matric: str = None):
        user = await self.repository.get_user_by_email_or_matric(email, matric)

        if user is None:
            return None

        return {
            "user_username": user.username,
            "user_matric": user.user_matric,
            "user_email": user.email,
            "user_role": user.role,
            "user_attendances": user.attendances,
        }

    async def get_user_records(self, user_matric: str, course_title: Optional[str] = None):
        user = await self.repository.get_user_by_email_or_matric(matric=user_matric)
        if course_title is None:
            try:
                if user and user.attendances:
                    return {f"attendance": user.attendances}

                raise HTTPException(
                    status_code=404, detail=f"No attendances for user: {user.user_matric}"
                )
            except Exception as e:
                logger.error(f"Something went wrong in fetching user records")
                logger.error(str(e))

                raise HTTPException(status_code=500, detail=" Internal server error")
        else:
            try:
                if user and user.attendances:
                    user_attendances = [
                        attendance for attendance in user.attendances
                        if attendance.course_title == course_title
                    ]
                    return {f"attendance": user_attendances}
                
            except Exception as e:
                logger.error(f"Something went wrong in fetching user records")
                logger.error(str(e))

                raise HTTPException(status_code=500, detail=" Internal server error")
    
    async def __generate_password_reset_token(
        self,
        email: EmailStr,
        username: str,
        user_matric: str,
        expires_delta: timedelta = timedelta(minutes=20),
    ):
        resetTokenRepo = PasswordResetTokenRepository(self.session)
        existing_token = await resetTokenRepo.get_token_by_matric(user_matric)
        if existing_token:
            await resetTokenRepo.set_token_is_used(user_matric=user_matric)

        # Data to encode as jwt
        data_to_encode = {
            "sub": email,
            "username": username,
            "user_matric": user_matric,
        }
        expires = datetime.now(tz=ZoneInfo("Africa/Lagos")) + expires_delta
        data_to_encode.update({"exp": expires})
        token = jwt.encode(
            data_to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        # Adding generated tokens to database
        resetTokenRepo = PasswordResetTokenRepository(self.session)
        await resetTokenRepo.add_token(
            user_id=user_matric, token=token, expires_at=expires
        )

        return token

    async def __decode_password_reset_token(self, token: str):
        # Make sure previously used tokens cannot be reused.
        resetTokenRepo = PasswordResetTokenRepository(self.session)
        existing_token = await resetTokenRepo.get_token(token)

        if not existing_token or existing_token.is_used:
            raise HTTPException(
                status_code=400,
                detail="Invalid link. Please request for a new password reset link.",
            )
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email = payload.get("sub")
            username = payload.get("username")
            user_matric = payload.get("user_matric")

            if not all([email, username, user_matric]):
                raise HTTPException(
                    status_code=401,
                    detail="Could not validate user",
                )

            await resetTokenRepo.set_token_is_used(token)

            return {
                "email": email,
                "username": username,
                "user_matric": user_matric,
            }
        except JWTError:
            await resetTokenRepo.deactivate_token(token)
            raise HTTPException(
                status_code=401,
                detail="Invalid link. Please request for a new password reset link.",
            )

    async def send_reset_password_email(
        self, user_email: dict, background_tasks: BackgroundTasks
    ):
        user = await self.get_user_by_email_or_matric(email=user_email)

        # go on if user exists
        token = await self.__generate_password_reset_token(
            email=user["user_email"],
            username=user["user_username"],
            user_matric=user["user_matric"],
        )
        reset_link = f"http://localhost:8000/user/student/reset_password?token={token}"
        body = f"""
            <html>
               <body>
                <h3>
                    Hi {user["user_username"]},
                </h3>
                <p>
                    We received a request to reset your password. Click the link below to reset it: <br>{reset_link}

                    <br><br> This link will expire in 20 minutes.
                    <br>If you didn't request this, you can safely ignore this email.

                    <br><br><br>
                    Thanks,<br>
                    Ave Geofencing.
                </p>
               </body> 
            </html>
            """

        background_tasks.add_task(
            send_email,
            subject="Password Reset Request",
            recipients=[user["user_email"]],
            body=body,
        )

    async def change_password(
        self, new_password, token: str, background_tasks: BackgroundTasks
    ):
        user = await self.__decode_password_reset_token(token)

        new_hashed_password = bcrypt_context.hash(new_password)
        try:
            change_password_message = await self.repository.change_user_password(
                user_email=user["email"], new_hashed_password=new_hashed_password
            )

            sessionRepository = SessionRepository(self.session)
            await sessionRepository.deactivate_all_user_sessions(user["user_matric"])

            body = f"""
                <html>
                    <body> 
                        <h3>
                            Hi {user["username"]},
                        </h3>
                        <p>
                            Your password has just been changed. <br>If you didn't change your password and you think your account has been compromised, report to help.

                            <br><br>Thanks,<br>
                            Ave Geofencing.
                        </p>
                    </body>
                </html>
                """
            background_tasks.add_task(
                send_email,
                subject="Password Changed.",
                recipients=[user["email"]],
                body=body,
            )
            return change_password_message

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error {e}")
