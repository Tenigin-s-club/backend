"""empty message

Revision ID: b434aeda20a8
Revises: 8b562652564f
Create Date: 2024-10-26 03:38:08.282977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b434aeda20a8'
down_revision: Union[str, None] = '8b562652564f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password', sa.LargeBinary(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'password')
    # ### end Alembic commands ###