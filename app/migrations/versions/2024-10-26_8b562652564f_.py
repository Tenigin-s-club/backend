"""empty message

Revision ID: 8b562652564f
Revises: 883e3688e009
Create Date: 2024-10-26 01:31:59.950481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b562652564f'
down_revision: Union[str, None] = '883e3688e009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('users_team_key', 'users', type_='unique')
    op.drop_column('users', 'team')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('team', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.create_unique_constraint('users_team_key', 'users', ['team'])
    # ### end Alembic commands ###
