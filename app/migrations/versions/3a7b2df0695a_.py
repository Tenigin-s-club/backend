"""empty message

Revision ID: 3a7b2df0695a
Revises: 7f34641ba974
Create Date: 2024-10-26 11:53:31.981527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a7b2df0695a'
down_revision: Union[str, None] = '7f34641ba974'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('favorite', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'favorite')
    # ### end Alembic commands ###
