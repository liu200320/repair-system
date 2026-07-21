"""create access_locations table and seed data"""

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None

LOCATIONS = [
    "学校大门口",
    "冻精站大门口",
    "种畜推广中心大门口",
]


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("access_locations"):
        op.create_table(
            "access_locations",
            sa.Column("id",         sa.Integer(),    primary_key=True, autoincrement=True),
            sa.Column("name",       sa.String(200),  unique=True, nullable=False, index=True, comment="门禁地点名称"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    count = bind.execute(sa.text("SELECT COUNT(*) FROM access_locations")).scalar()
    if count == 0:
        bind.execute(
            sa.text("INSERT INTO access_locations (name) VALUES (:name)"),
            [{"name": loc} for loc in LOCATIONS],
        )


def downgrade() -> None:
    op.drop_table("access_locations")
