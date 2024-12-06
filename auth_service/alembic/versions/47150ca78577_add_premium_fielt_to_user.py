"""add_premium_fielt_to_user

Revision ID: 47150ca78577
Revises: f5370991295b
Create Date: 2024-11-28 20:26:07.556594

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "47150ca78577"
down_revision: Union[str, None] = "f5370991295b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "user_social_accounts", ["id"])
    op.add_column("users", sa.Column(
        "is_premium", sa.Boolean(), nullable=True))
    op.alter_column(
        "users", "email", existing_type=sa.VARCHAR(length=255), nullable=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "users", "email", existing_type=sa.VARCHAR(length=255), nullable=True
    )
    op.drop_column("users", "is_premium")
    op.drop_constraint(None, "user_social_accounts", type_="unique")
    # ### end Alembic commands ###
