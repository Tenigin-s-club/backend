"""some fixes (pls help me)

Revision ID: 372c516dd270
Revises: aeed714159d1
Create Date: 2024-10-27 10:09:06.126030

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '372c516dd270'
down_revision: Union[str, None] = 'aeed714159d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wait', sa.Column('train_id', sa.Integer(), nullable=False))
    op.drop_column('wait', 'start_point')
    op.drop_column('wait', 'end_point')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wait', sa.Column('end_point', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('wait', sa.Column('start_point', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('wait', 'train_id')
    # ### end Alembic commands ###