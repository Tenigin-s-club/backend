"""empty message

Revision ID: fa6431643943
Revises: b3fb740f615e
Create Date: 2024-10-26 23:38:22.660583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa6431643943'
down_revision: Union[str, None] = 'b3fb740f615e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('type_wagon', sa.String(), nullable=False))
    op.add_column('orders', sa.Column('type_shelf', sa.String(), nullable=False))
    op.add_column('orders', sa.Column('number_wagon', sa.Integer(), nullable=False))
    op.add_column('orders', sa.Column('number_seat', sa.Integer(), nullable=False))
    op.add_column('orders', sa.Column('stops', sa.ARRAY(sa.String()), nullable=True))
    op.drop_column('orders', 'favorite')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('favorite', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('orders', 'stops')
    op.drop_column('orders', 'number_seat')
    op.drop_column('orders', 'number_wagon')
    op.drop_column('orders', 'type_shelf')
    op.drop_column('orders', 'type_wagon')
    # ### end Alembic commands ###
