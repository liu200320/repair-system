"""add token_version to users"""

import sqlalchemy as sa
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("token_version", sa.Integer(), nullable=False, server_default="0", comment="每次登出后递增，使旧 token 立即失效"),
    )


def downgrade() -> None:
    op.drop_column("users", "token_version")
