"""Added is_verified field to user model

Revision ID: 860d0267c93d
Revises: 87ee69cd4a5c
Create Date: 2025-03-20 21:51:24.190407

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '860d0267c93d'
down_revision: Union[str, None] = '87ee69cd4a5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_email_verified', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_email_verified')
    # ### end Alembic commands ###
