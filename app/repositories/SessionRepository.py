from ..models import Session, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_
from ..models import Session
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class SessionRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_user_by_email_or_matric(
        self, email: str = None, matric: str = None
    ):
        stmt = select(User).filter(or_(User.email == email, User.user_matric == matric))
        result = await self.db_session.execute(stmt)
        user = result.scalars().first()

        return user
    
    async def get_user_session_by_token(self, session_token):
        stmt = (
            select(Session)
            .options(selectinload(Session.user))
            .filter(
                and_(
                    Session.token == session_token, Session.expires_at >= datetime.now()
                )
            )
        )

        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def get_user_session_by_matric(self, user_matric: str):
        stmt = select(Session).filter(
            and_(Session.user_id == user_matric, Session.is_expired == False)
        )
        result = await self.db_session.execute(stmt)

        return result.scalars().first()

    async def create_new_session(self, session_token, EXPIRES_AT, user_matric: str):

        new_session = Session(
            user_id=user_matric,
            token=session_token,
            expires_at=EXPIRES_AT,
        )

        self.db_session.add(new_session)
        await self.db_session.commit()
        await self.db_session.refresh(new_session)
        return new_session.token

    async def deactivate_session(self, session_token):
        stmt = select(Session).filter(Session.token == session_token)
        result = await self.db_session.execute(stmt)
        existing_session = result.scalars().first()

        await self.db_session.delete(existing_session)

        await self.db_session.commit()
