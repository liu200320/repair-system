# 维修记录 Web 系统

> 技术栈：Vue3 + Vite + Element Plus ／ FastAPI + MySQL

## 快速开始（本地开发）

### 1. 配置数据库连接

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入你的 MySQL 连接信息
```

### 2. 启动后端

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

首次启动会自动创建 `repair_db` 数据库的表结构。

接口文档访问：http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend
npm run dev
```

前端访问：http://localhost:5173

---

## 生产部署（Docker）

### 前提：Linux 服务器已安装 Docker + Docker Compose

```bash
# 1. 构建前端静态文件
cd frontend
npm run build

# 2. 配置生产环境变量
cp backend/.env.example .env
# 编辑 .env 修改 DB_PASSWORD 等

# 3. 一键启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

访问：http://你的服务器IP

---

## 项目结构

```
维修记录web项目/
├── frontend/                # Vue3 前端
│   └── src/
│       ├── api/             # Axios 请求封装
│       ├── components/      # PhotoUploader 照片上传组件
│       ├── router/          # Vue Router
│       ├── stores/          # Pinia 状态管理
│       └── views/           # 列表、表单、详情页
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/          # repair / upload / export 路由
│   │   ├── core/            # config / database
│   │   ├── models/          # SQLAlchemy 数据模型
│   │   ├── schemas/         # Pydantic 验证模型
│   │   └── services/        # 业务逻辑 / Word 导出
│   ├── uploads/             # 图片存储目录
│   └── main.py
├── nginx/nginx.conf         # Nginx 配置
├── docker-compose.yml
└── README.md
```

## 主要功能

- ✅ 维修记录 CRUD（日期、点位、描述、状态）
- ✅ 手机相机拍照 / 相册选图上传
- ✅ 维修前 / 维修中 / 维修后照片分组展示
- ✅ 导出 Word 文档（含所有照片和基本信息）
- ✅ 按日期、点位、状态筛选查询
- ✅ Docker 一键部署到 Linux
