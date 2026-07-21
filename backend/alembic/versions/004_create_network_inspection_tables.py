"""create network_inspection_records and network_inspection_photos tables"""

import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "network_inspection_records",
        sa.Column("id",                sa.Integer(),     primary_key=True, autoincrement=True),
        sa.Column("record_no",         sa.String(50),    unique=True, nullable=False),
        sa.Column("inspect_date",      sa.String(20),    nullable=False),
        sa.Column("location",          sa.String(200),   nullable=False),
        sa.Column("inspector",         sa.String(100),   nullable=True),
        sa.Column("line_status",       sa.String(200),   nullable=True),
        sa.Column("device_status",     sa.String(200),   nullable=True),
        sa.Column("terminal_status",   sa.String(200),   nullable=True),
        sa.Column("other_device",      sa.String(200),   nullable=True),
        sa.Column("fault_description", sa.Text(),        nullable=True),
        sa.Column("repair_content",    sa.Text(),        nullable=True),
        sa.Column("created_at",        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",        sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "network_inspection_photos",
        sa.Column("id",            sa.Integer(),    primary_key=True, autoincrement=True),
        sa.Column("record_id",     sa.Integer(),    sa.ForeignKey("network_inspection_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("photo_index",   sa.Integer(),    nullable=False, default=1),
        sa.Column("filename",      sa.String(255),  nullable=False),
        sa.Column("original_name", sa.String(255),  nullable=True),
        sa.Column("filepath",      sa.String(500),  nullable=False),
        sa.Column("thumb_filename",sa.String(255),  nullable=True),
        sa.Column("created_at",    sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("network_inspection_photos")
    op.drop_table("network_inspection_records")
