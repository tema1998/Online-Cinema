"""add_premium_model

Revision ID: 0cefbac042d1
Revises: 47150ca78577
Create Date: 2024-11-30 18:12:06.342648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0cefbac042d1'
down_revision: Union[str, None] = '47150ca78577'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('premiums',
    sa.Column('parent_id', sa.UUID(), nullable=True),
    sa.Column('valid_until', sa.DateTime(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.drop_column('users', 'is_premium')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_premium', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_table('premiums')
    # ### end Alembic commands ###
