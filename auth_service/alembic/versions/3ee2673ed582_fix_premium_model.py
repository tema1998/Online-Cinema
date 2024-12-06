"""fix_premium_model

Revision ID: 3ee2673ed582
Revises: 0cefbac042d1
Create Date: 2024-11-30 18:22:38.453731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3ee2673ed582'
down_revision: Union[str, None] = '0cefbac042d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('premium_data',
                    sa.Column('user_id', sa.UUID(), nullable=True),
                    sa.Column('premium_id', sa.UUID(), nullable=False),
                    sa.Column('valid_until', sa.DateTime(), nullable=False),
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.drop_table('premiums')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('premiums',
                    sa.Column('parent_id', sa.UUID(),
                              autoincrement=False, nullable=True),
                    sa.Column('valid_until', postgresql.TIMESTAMP(),
                              autoincrement=False, nullable=False),
                    sa.Column('id', sa.UUID(),
                              autoincrement=False, nullable=False),
                    sa.Column('created_at', postgresql.TIMESTAMP(),
                              autoincrement=False, nullable=False),
                    sa.Column('updated_at', postgresql.TIMESTAMP(),
                              autoincrement=False, nullable=False),
                    sa.ForeignKeyConstraint(
                        ['parent_id'], ['users.id'], name='premiums_parent_id_fkey'),
                    sa.PrimaryKeyConstraint('id', name='premiums_pkey')
                    )
    op.drop_table('premium_data')
    # ### end Alembic commands ###
