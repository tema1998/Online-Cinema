"""fix_order_status_field

Revision ID: 95db63871bcf
Revises: d8fc3903dce8
Create Date: 2024-11-21 16:06:04.794213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95db63871bcf'
down_revision: Union[str, None] = 'd8fc3903dce8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('order_status', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'order_status')
    # ### end Alembic commands ###