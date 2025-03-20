import logging
from typing import Optional, Dict, Any, Union
from zoneinfo import ZoneInfo
from datetime import timedelta, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks, HTTPException
from passlib.context import CryptContext
from pydantic import EmailStr
from jose import JWTError, jwt

from .EmailService import send_email
from ..repositories import (
    PasswordResetTokenRepository,
    SessionRepository,
    UserRepository,
)
from ..schemas import UserCreateModel
from ..utils.config import settings
from ..utils.constants import (
    PASSWORD_RESET_TOKEN_EXPIRY_MINUTES,
    EMAIL_SUBJECTS,
    PASSWORD_MIN_LENGTH,
)

# Create a password context for hashing
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger("uvicorn")


# Custom exception classes
class UserServiceError(Exception):
    """Base exception for UserService errors"""

    pass


class UserAlreadyExistsError(UserServiceError):
    """Raised when attempting to create a user that already exists"""

    pass


class UserNotFoundError(UserServiceError):
    """Raised when a user is not found"""

    pass


class TokenError(UserServiceError):
    """Raised when there is an issue with a token"""

    pass



class UserService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: Optional[UserRepository] = None,
        password_reset_token_repository: Optional[PasswordResetTokenRepository] = None,
        session_repository: Optional[SessionRepository] = None,
    ):
        self.session = session
        self.user_repository = user_repository or UserRepository(session)
        self.password_reset_token_repository = (
            password_reset_token_repository or PasswordResetTokenRepository(session)
        )
        self.session_repository = session_repository or SessionRepository(session)

    async def create_new_user(self, user_data: UserCreateModel) -> Dict[str, str]:
        """Create a new user account"""
        try:
            existing_user = await self.user_repository.get_user_by_email_or_matric(
                email=user_data.email, matric=user_data.user_matric
            )

            if existing_user:
                raise UserAlreadyExistsError(
                    "User with this email or matric number already exists"
                )

            # Validate password
            if len(user_data.password) < PASSWORD_MIN_LENGTH:
                raise ValueError(
                    f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
                )

            hashed_password = bcrypt_context.hash(user_data.password)
            #Store user temporarily, with 'verified?' being false- awaiting implementation

            #Generate 6 digit code and store code and database while sending a message that code has been sent 
            # to the frontend


            return await self.user_repository.create_new_user(
                user_data, hashed_password
            )

        except UserAlreadyExistsError as e:
            logger.warning(
                f"Attempt to create duplicate user: {user_data.email}/{user_data.user_matric}"
            )
            raise HTTPException(status_code=400, detail=str(e))
        except ValueError as e:
            logger.warning(f"Invalid user data: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error creating new user: {user_data.email}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Something went wrong, contact admin."
            )


    async def verify_registration_code(self, code: int):
        #Check if code exist in database againsts user email and it has not expired
        code = ...
        if(code is None or "expired"):
            return "Code has expired. Resend to get a new code"
        
        if(code is "Verified"):
            return "mark as verified"

    async def get_user_by_email_or_matric(
        self, email: str = None, matric: str = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieve user information by email or matric number"""
        if not email and not matric:
            raise HTTPException(
                status_code=400, detail="Email or matric number must be provided"
            )

        try:
            user = await self.user_repository.get_user_by_email_or_matric(email, matric)
            if user is None:
                return None

            return {
                "user_username": user.username,
                "user_matric": user.user_matric,
                "user_email": user.email,
                "user_role": user.role,
                "user_attendances": user.attendances,
            }

        except Exception as e:
            logger.error(
                f"Error fetching user by email/matric: {email} or {matric}", exc_info=True
            )
            raise HTTPException(
                status_code=500, detail="Something went wrong, contact admin."
            )

    async def get_user_records(
        self, user_matric: str, course_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve user attendance records, optionally filtered by course"""
        try:
            user = await self.user_repository.get_user_by_email_or_matric(
                matric=user_matric
            )

            if not user:
                raise UserNotFoundError(f"User with matric {user_matric} not found")

            if not user.attendances:
                return {"attendance": []}

            if course_title is None:
                return {"attendance": user.attendances}

            filtered_attendances = [
                attendance
                for attendance in user.attendances
                if attendance.course_title == course_title
            ]
            return {"attendance": filtered_attendances}

        except UserNotFoundError as e:
            logger.warning(str(e))
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(
                f"Error fetching records for user {user_matric}", exc_info=True
            )
            raise HTTPException(
                status_code=500, detail="Something went wrong, contact admin."
            )

    async def _generate_password_reset_token(
        self,
        email: EmailStr,
        username: str,
        user_matric: str,
        expires_delta: timedelta = timedelta(
            minutes=PASSWORD_RESET_TOKEN_EXPIRY_MINUTES
        ),
    ) -> str:
        """Generate a JWT token for password reset"""
        try:
            # Invalidate any existing tokens
            existing_token = (
                await self.password_reset_token_repository.get_token_by_matric(
                    user_matric
                )
            )
            if existing_token:
                await self.password_reset_token_repository.set_token_is_used(
                    user_matric=user_matric
                )

            # Prepare token data
            expires = datetime.now(tz=ZoneInfo("UTC")) + expires_delta
            token_data = {
                "sub": email,
                "username": username,
                "user_matric": user_matric,
                "exp": expires,
            }

            # Create JWT token
            token = jwt.encode(
                token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
            )

            # Store token in database
            await self.password_reset_token_repository.add_token(
                user_id=user_matric, token=token, expires_at=expires
            )

            return token

        except Exception as e:
            logger.error(
                f"Error generating password reset token for {email}", exc_info=True
            )
            raise TokenError(f"Failed to generate reset token: {str(e)}")

    async def _decode_password_reset_token(self, token: str) -> Dict[str, str]:
        """Validate and decode a password reset token"""
        try:
            # Verify token exists and is valid
            existing_token = await self.password_reset_token_repository.get_token(token)

            if not existing_token:
                raise TokenError("Token not found")

            if existing_token.is_used:
                raise TokenError("Token has already been used")

            # Decode JWT
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

            # Extract token data
            email = payload.get("sub")
            username = payload.get("username")
            user_matric = payload.get("user_matric")

            if not all([email, username, user_matric]):
                raise TokenError("Invalid token data")

            # Mark token as used
            await self.password_reset_token_repository.set_token_is_used(token)

            return {
                "email": email,
                "username": username,
                "user_matric": user_matric,
            }

        except JWTError:
            # If JWT is invalid, deactivate the token
            await self.password_reset_token_repository.deactivate_token(token)
            raise TokenError("Invalid or expired token")
        except TokenError as e:
            logger.error(f"Error decoding token({str(e)})")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid link. Please request a new password reset link.",
            )
        except Exception as e:
            logger.error(f"Error decoding token: {token[:10]}...", exc_info=True)
            raise HTTPException(status_code=500, detail="Something went wrong")

    def _get_password_reset_email_template(self, username: str, reset_link: str) -> str:
        """Generate HTML template for password reset email"""
        return f"""
            <html>
            <body>
                <h3>
                    Hi {username},
                </h3>
                <p>
                    We received a request to reset your password. Click the link below to reset it: <br>{reset_link}

                    <br><br> This link will expire in {PASSWORD_RESET_TOKEN_EXPIRY_MINUTES} minutes.
                    <br>If you didn't request this, you can safely ignore this email.

                    <br><br><br>
                    Thanks,<br>
                    Ave Geofencing.
                </p>
            </body> 
            </html>
            """

    def _get_password_changed_email_template(self, username: str) -> str:
        """Generate HTML template for password changed confirmation email"""
        return f"""
            <html>
                <body> 
                    <h3>
                        Hi {username},
                    </h3>
                    <p>
                        Your password has just been changed. <br>If you didn't change your password and you think your account has been compromised, report to help.

                        <br><br>Thanks,<br>
                        Ave Geofencing.
                    </p>
                </body>
            </html>
            """

    async def send_reset_password_email(
        self, user_email: str, background_tasks: BackgroundTasks
    ) -> Dict[str, str]:
        """Send password reset email to user"""
        try:
            user = await self.get_user_by_email_or_matric(email=user_email)
            if user is None:
                # Return success even if user doesn't exist for security reasons
                return {
                    "message": "If a user with this email exists, a reset link has been sent"
                }

            # Generate token and reset link
            token = await self._generate_password_reset_token(
                email=user["user_email"],
                username=user["user_username"],
                user_matric=user["user_matric"],
            )

            reset_link = f"{settings.BASE_URL}user/student/reset_password?token={token}"

            # Generate email body
            body = self._get_password_reset_email_template(
                username=user["user_username"], reset_link=reset_link
            )

            # Send email as background task
            background_tasks.add_task(
                send_email,
                subject=EMAIL_SUBJECTS["PASSWORD_RESET"],
                recipients=[user["user_email"]],
                body=body,
            )

            return {
                "message": "If a user with this email exists, a reset link has been sent"
            }

        except TokenError as e:
            logger.error(f"Token generation error for {user_email}: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to generate reset token"
            )
        except Exception as e:
            logger.error(
                f"Error sending password reset email to {user_email}: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=500, detail="Something went wrong, contact admin"
            )

    async def change_password(
        self, new_password: str, token: str, background_tasks: BackgroundTasks
    ) -> Dict[str, str]:
        """Change user password using reset token"""
        if not new_password or len(new_password) < PASSWORD_MIN_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Password must be at least {PASSWORD_MIN_LENGTH} characters",
            )

        try:
            # Verify and decode token
            user = await self._decode_password_reset_token(token)

            # Hash and update password
            new_hashed_password = bcrypt_context.hash(new_password)
            change_password_message = await self.user_repository.change_user_password(
                user_email=user["email"], new_hashed_password=new_hashed_password
            )

            # Deactivate all user sessions for security
            await self.session_repository.deactivate_all_user_sessions(
                user["user_matric"]
            )

            # Send confirmation email
            body = self._get_password_changed_email_template(username=user["username"])

            background_tasks.add_task(
                send_email,
                subject=EMAIL_SUBJECTS["PASSWORD_CHANGED"],
                recipients=[user["email"]],
                body=body,
            )

            return change_password_message

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error changing password with token {token[:10]}...", exc_info=True
            )
            raise HTTPException(status_code=500, detail="Something went wrong")
