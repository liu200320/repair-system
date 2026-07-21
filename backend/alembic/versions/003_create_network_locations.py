"""create network_locations table and seed data"""

import sqlalchemy as sa
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None

LOCATIONS = [
    "鸿翼楼二楼楼梯口",
    "实训楼二楼楼梯口",
    "嘉锐楼三楼楼梯口",
    "绍年院网络机柜",
    "文清楼网络机柜",
    "文兴楼网络机柜",
    "众创空间",
    "体育工作部",
    "冻精站1楼房间",
    "蚕桑礼堂弱电间",
    "团委二楼",
    "牧歌院二栋",
    "综合楼四楼弱电间",
    "综合楼五楼弱电间",
    "学生服务中心二楼网络机柜",
    "实训中心办公楼",
    "五谷苑5栋",
    "三实牧院",
    "种畜场招待所楼梯间",
    "种畜场原医务室",
    "种畜场办公楼",
]


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("network_locations"):
        op.create_table(
            "network_locations",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(200), unique=True, nullable=False, index=True, comment="地点名称"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    # 仅在表为空时写入种子数据
    count = bind.execute(sa.text("SELECT COUNT(*) FROM network_locations")).scalar()
    if count == 0:
        bind.execute(
            sa.text("INSERT INTO network_locations (name) VALUES (:name)"),
            [{"name": loc} for loc in LOCATIONS],
        )


def downgrade() -> None:
    op.drop_table("network_locations")
