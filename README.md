# 维修记录 Web 系统

> 云南农业职业技术学院安防设备维修与耗材管理平台  
> 技术栈：Vue 3 + Vite + Element Plus + ECharts ／ FastAPI + MySQL + Docker

---

## 功能模块

| 模块 | 功能 |
|------|------|
| 🔐 用户认证 | JWT 登录、角色权限（admin / viewer） |
| 📋 维修记录 | CRUD、工单编号自动生成、状态跟踪 |
| 📸 照片上传 | 维修前 / 维修中 / 维修后三阶段拍照，前端压缩，自动生成缩略图 |
| 📄 Word 导出 | 一键导出含照片的维修工单文档 |
| 🔧 耗材管理 | 耗材使用记录 CRUD、明细行项、照片上传、Word 导出 |
| 📊 统计看板 | 状态汇总、30 天趋势图、维修量 Top10 点位（ECharts） |
| 📍 点位管理 | 维修点位库增删改查（管理员） |
| 👥 用户管理 | 新增 / 禁用用户、重置密码（管理员） |

---

## 快速开始（本地开发）

### 前提

- Python 3.10+
- Node.js 18+
- MySQL 8.0（本地已运行）
- Windows 用户可直接双击 `启动项目.bat`

### 1. 配置后端环境

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入 MySQL 连接信息
```

`.env` 关键字段：

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=repair_db
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760   # 10 MB
```

### 2. 安装依赖并启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

首次启动自动建表（`repair_db`）。接口文档：http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端访问：http://localhost:5173

---

## 生产部署（Docker，推荐）

### 前提：Linux 服务器已安装 Docker + Docker Compose

```bash
# 1. 构建前端静态文件
cd frontend
npm run build

# 2. 配置生产环境变量
cp backend/.env.example .env
# 编辑 .env，修改 DB_PASSWORD 等生产参数

# 3. 一键启动（db + backend + nginx 三服务）
docker-compose up -d

# 查看日志
docker-compose logs -f
```

访问：`http://你的服务器IP`

> 详细步骤见 [DEPLOY.md](DEPLOY.md) | 手动部署见 [DEPLOY_MANUAL.md](DEPLOY_MANUAL.md)

---

## 项目结构

```
维修记录web项目/
├── frontend/                  # Vue 3 前端
│   └── src/
│       ├── api/               # Axios 请求封装（auth / repair / consumable / stats）
│       ├── components/        # PhotoUploader 照片上传组件
│       ├── router/            # Vue Router（含导航守卫）
│       ├── stores/            # Pinia 状态管理（auth / repair）
│       └── views/             # 各功能页面（见下表）
├── backend/                   # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/            # 路由层（auth / repair / upload / export /
│   │   │                      #         location / monitor_point / stats / consumable）
│   │   ├── core/              # config / database / security（JWT + bcrypt）
│   │   ├── models/            # SQLAlchemy 数据模型
│   │   ├── schemas/           # Pydantic 验证模型
│   │   └── services/          # 业务逻辑 / Word 导出 / 图片处理
│   ├── uploads/               # 图片存储目录（Docker 挂载为命名卷）
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── database/
│   └── repair_db.sql          # 完整数据库 DDL（备份 / 初始化用）
├── nginx/
│   ├── nginx.conf             # Docker 用 Nginx 配置
│   └── repair-system-site.conf# 裸机 Linux 站点配置
├── docker-compose.yml
├── 启动项目.bat               # Windows 本地一键启动
├── monitor_points.csv         # 监控点位种子数据
├── DEPLOY.md                  # Docker 部署详细教程
├── DEPLOY_MANUAL.md           # 手动部署教程
└── README.md
```

### 前端页面

| 文件 | 说明 |
|------|------|
| `Login.vue` | 登录页 |
| `Dashboard.vue` | 统计看板（ECharts） |
| `RepairList.vue` | 维修记录列表（分页 + 筛选） |
| `RepairForm.vue` | 新建 / 编辑维修记录 |
| `RepairDetail.vue` | 维修记录详情 |
| `ConsumableList.vue` | 耗材使用记录列表 |
| `ConsumableForm.vue` | 新建 / 编辑耗材记录 |
| `LocationManager.vue` | 点位管理（管理员） |
| `UserManager.vue` | 用户管理（管理员） |

---

## 数据库结构

数据库名：`repair_db`（MySQL 8.0，utf8mb4）

| 表名 | 说明 |
|------|------|
| `users` | 用户（id, username, role: admin/viewer, is_active） |
| `repair_records` | 维修工单（record_no 格式 R20260719001） |
| `repair_photos` | 维修照片（phase: before/during/after，含缩略图） |
| `repair_locations` | 维修点位库 |
| `monitor_points` | 监控点位（只读，外部维护） |
| `consumable_records` | 耗材使用记录（record_no 格式 C20260719001） |
| `consumable_items` | 耗材明细行项（name, unit, quantity, signer） |
| `consumable_photos` | 耗材记录照片（含缩略图） |

---

## 权限说明

| 操作 | admin | viewer |
|------|:-----:|:------:|
| 查看所有记录 | ✅ | ✅ |
| 新建 / 编辑记录 | ✅ | ✅ |
| 删除维修记录 | ✅ | ❌ |
| 用户管理 | ✅ | ❌ |
| 点位管理 | ✅ | ❌ |

---

## 更新记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-19 | v1.3 | 新增耗材管理模块（CRUD + 照片上传 + Word 导出） |
| 2026-07-xx | v1.2 | 新增统计看板（ECharts 图表） |
| 2026-07-xx | v1.1 | 新增用户管理、点位管理、JWT 认证 |
| 2026-07-xx | v1.0 | 初版：维修记录 CRUD + 照片上传 + Word 导出 |
