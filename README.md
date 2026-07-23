# 维修记录 Web 系统

> 云南农业职业技术学院安防设备维修、耗材管理及巡检记录平台  
> 技术栈：Vue 3 + Vite + Element Plus + ECharts ／ FastAPI + MySQL

---

## 功能模块

| 模块 | 功能 |
|------|------|
| 🔐 用户认证 | JWT 登录、角色权限（admin / viewer）、主动登出（旧 token 立即失效）、登录防暴力破解（10次/分钟/IP） |
| 📋 维修记录 | CRUD、工单编号自动生成（R开头）、状态跟踪、单条/时间段批量导出 Word |
| 📸 照片上传 | 维修前 / 维修中 / 维修后三阶段拍照，前端压缩，自动生成缩略图 |
| 🔧 耗材管理 | 耗材使用记录 CRUD、明细行项、照片上传、Word 导出 |
| 🌐 网络巡检 | 网络基础设施日常巡检 CRUD（N开头单号）、照片上传、单条/时间段批量导出 Word |
| 🚧 门禁巡检 | 门禁日常巡检 CRUD（A开头单号）、照片上传、单条/时间段批量导出 Word |
| 📊 统计看板 | 状态汇总、30 天趋势图、维修量 Top10 点位（ECharts） |
| 📍 点位管理 | 三合一：维修点位 / 网络巡检点位 / 门禁点位 各自增删改查（管理员） |
| 👥 用户管理 | 新增 / 禁用用户、重置密码（管理员） |

---

## 快速开始（本地开发）

### 前提

- Python 3.10+
- Node.js 20+
- MySQL 8.0（本地已运行）

### 1. 配置后端环境

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入 MySQL 连接信息和必要密钥
```

`.env` 关键字段：

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=repair_db
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# 必须设置，否则启动报错
# 生成命令：python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your_random_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=480

# 首次启动建库时创建初始管理员（数据库已有用户时此项不生效）
# 生成命令：python -c "import secrets; print(secrets.token_urlsafe(16))"
ADMIN_INIT_PASSWORD=your_strong_admin_password

# CORS 允许来源（本地开发保持默认）
ALLOWED_ORIGINS=http://localhost:5173

# 导出文件自动清理保留天数
EXPORT_RETENTION_DAYS=7
```

### 2. 安装依赖并启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

首次启动自动建表并写入预置地点数据。接口文档：http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端访问：http://localhost:5173

---

## 生产部署（Linux + PM2 + Nginx，推荐）

详细步骤见 [LINUX部署教程.md](LINUX部署教程.md)

更新已有部署见：
- [v1.4更新部署教程.md](v1.4更新部署教程.md)
- [v1.5安全加固部署教程.md](v1.5安全加固部署教程.md)（本次安全更新）

---

## 项目结构

```
维修记录web项目/
├── frontend/                  # Vue 3 前端
│   └── src/
│       ├── api/               # Axios 请求封装（各模块独立文件）
│       ├── router/            # Vue Router（含导航守卫）
│       ├── stores/            # Pinia 状态管理
│       └── views/             # 各功能页面（见下表）
├── backend/                   # FastAPI 后端
│   ├── alembic/               # 数据库迁移（Alembic）
│   │   └── versions/          # 001~006 迁移版本文件
│   ├── app/
│   │   ├── api/v1/            # 路由层（8个模块）
│   │   ├── core/              # config / database / security / limiter
│   │   ├── models/            # SQLAlchemy 数据模型（11张表）
│   │   ├── schemas/           # Pydantic 验证模型
│   │   └── services/          # 业务逻辑 / Word 导出 / 图片处理
│   ├── uploads/               # 图片 + 导出文件存储
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── database/
│   └── repair_db.sql          # 数据库 DDL（备份用）
├── nginx/
│   └── repair-system-site.conf# Linux 裸机 Nginx 配置
├── docker-compose.yml
├── LINUX部署教程.md            # 初次部署教程
├── v1.4更新部署教程.md         # v1.4 更新部署教程
├── v1.5安全加固部署教程.md     # v1.7 安全加固更新部署教程
└── README.md
```

### 前端页面

| 文件 | 说明 |
|------|------|
| `Login.vue` | 登录页 |
| `Dashboard.vue` | 统计看板（ECharts） |
| `RepairList.vue` | 维修记录列表（分页 + 筛选 + 批量导出） |
| `RepairForm.vue` | 新建 / 编辑维修记录 + 照片上传 |
| `RepairDetail.vue` | 维修记录详情 |
| `ConsumableList.vue` | 耗材使用记录列表 + 批量导出 |
| `ConsumableForm.vue` | 新建 / 编辑耗材记录 + 照片上传 |
| `NetworkInspectionList.vue` | 网络巡检列表 + 批量导出 |
| `NetworkInspectionForm.vue` | 新建 / 编辑网络巡检记录 + 照片上传 |
| `AccessInspectionList.vue` | 门禁巡检列表 + 批量导出 |
| `AccessInspectionForm.vue` | 新建 / 编辑门禁巡检记录 + 照片上传 |
| `LocationManager.vue` | 点位管理（三标签：维修/网络/门禁） |
| `UserManager.vue` | 用户管理（管理员） |

---

## 数据库结构

数据库名：`repair_db`（MySQL 8.0，utf8mb4）

| 表名 | 说明 |
|------|------|
| `users` | 用户（含 token_version，支持主动登出） |
| `repair_records` | 维修工单（R开头单号） |
| `repair_photos` | 维修照片（before/during/after 三阶段） |
| `monitor_points` | 维修点位库 |
| `consumable_records` | 耗材使用记录（C开头单号） |
| `consumable_items` | 耗材明细行项 |
| `consumable_photos` | 耗材照片 |
| `network_locations` | 网络巡检预置地点（21个，可增删） |
| `network_inspection_records` | 网络基础设施巡检记录（N开头单号） |
| `network_inspection_photos` | 网络巡检照片 |
| `access_locations` | 门禁预置地点（3个，可增删） |
| `access_inspection_records` | 门禁日常巡检记录（A开头单号） |
| `access_inspection_photos` | 门禁巡检照片 |

> 所有表在首次启动时由 `create_all` 自动创建，预置地点数据由启动脚本自动写入，无需手动建表。

---

## 权限说明

| 操作 | admin | viewer |
|------|:-----:|:------:|
| 查看所有记录 | ✅ | ✅ |
| 新建 / 编辑记录 | ✅ | ✅ |
| 上传照片 | ✅ | ✅ |
| 导出 Word | ✅ | ✅ |
| 删除记录 | ✅ | ❌ |
| 用户管理 | ✅ | ❌ |
| 点位管理 | ✅ | ✅ |

---

## 更新记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-23 | v1.7 | 安全加固：登录防暴力破解（slowapi 10次/分钟/IP）；管理员初始密码改为环境变量注入；文件上传改分块读取防内存耗尽；导出日期参数严格校验防路径遍历；密码复杂度提升（8位+字母+数字）；健康检查不再暴露版本号 |
| 2026-07-22 | v1.6 | 前端UI重构：顶部横栏改为左侧固定Sidebar（桌面可收起至图标模式，移动端汉堡菜单+遮罩）；全局设计token（CSS变量统一管理颜色/圆角/阴影）；Dashboard统计卡片改用EP图标；列表操作列收为「详情+更多▼」下拉；登录页移除明文默认密码提示 |
| 2026-07-21 | v1.5 | 新增门禁日常巡检模块（CRUD+照片+单条/批量导出）；点位管理升级为三标签页（维修/网络/门禁）；导出样式优化（单页紧凑排版） |
| 2026-07-21 | v1.4 | 新增网络基础设施日常巡检模块；安全加固（JWT主动吊销、SECRET_KEY强制配置、CORS可配置）；导出文件定期清理；前端依赖版本锁定 |
| 2026-07-19 | v1.3 | 新增耗材管理模块（CRUD + 照片上传 + Word 导出） |
| 2026-07-xx | v1.2 | 新增统计看板（ECharts 图表） |
| 2026-07-xx | v1.1 | 新增用户管理、点位管理、JWT 认证 |
| 2026-07-xx | v1.0 | 初版：维修记录 CRUD + 照片上传 + Word 导出 |
