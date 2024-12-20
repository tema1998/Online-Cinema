"""fix_premium_model2

Revision ID: 6ff9f10808fe
Revises: 3ee2673ed582
Create Date: 2024-11-30 18:27:16.984605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ff9f10808fe'
down_revision: Union[str, None] = '3ee2673ed582'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'premium_data', ['id'])
    op.drop_column('premium_data', 'premium_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('premium_data', sa.Column(
        'premium_id', sa.UUID(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'premium_data', type_='unique')
    # ### end Alembic commands ###
