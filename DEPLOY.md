# 维修记录系统 — Linux 部署教程

> 适用环境：Ubuntu 20.04 / 22.04 / CentOS 7+  
> 部署方式：**方案A（推荐）Docker Compose 一键部署** | **方案B 手动部署**

---

## 数据库文件说明

项目目录下的 `database/` 文件夹包含已导出的数据库文件：

```
database/
└── repair_db.sql    ← 完整数据库备份（表结构 + 初始数据）
```

**文件包含内容：**

| 表名 | 说明 | 数据量 |
|------|------|--------|
| `monitor_points` | 维修点位库（222个点位） | 222 条 |
| `users` | 系统用户（含默认管理员） | 1 条 |
| `repair_records` | 维修记录主表 | 结构 |
| `repair_photos` | 维修照片表 | 结构 |
| `repair_locations` | 备用点位表 | 结构 |

> ⚠️ 导入后默认管理员账号为 `admin` / `admin123`，**请立即登录修改密码**。

---

## 前置要求

| 项目 | 要求 |
|------|------|
| Linux 服务器 | 1核2GB 以上，推荐 2核4GB |
| 操作系统 | Ubuntu 20.04 LTS / 22.04 LTS |
| 开放端口 | 80（Web）、22（SSH） |
| 本机 | 已安装 Node.js、Python、Git |

---

## 第一步：准备代码

### 方式一：Git（推荐）

在本机先初始化 Git 仓库并推送：

```bash
# 本机执行
cd D:\维修记录web项目
git init
git add .
git commit -m "init"
# 推送到 GitHub / Gitee（自行创建仓库后替换地址）
git remote add origin https://github.com/yourname/repair-system.git
git push -u origin main
```

在服务器上拉取：

```bash
# 服务器执行
git clone https://github.com/yourname/repair-system.git /opt/repair-system
cd /opt/repair-system
```

### 方式二：SCP 直接传输

```bash
# 本机执行（Windows PowerShell / Git Bash）
scp -r "D:\维修记录web项目" root@你的服务器IP:/opt/repair-system
```

---

## 方案A：Docker Compose 一键部署（推荐）

### 1. 安装 Docker 和 Docker Compose

```bash
# Ubuntu
sudo apt update
sudo apt install -y docker.io docker-compose-plugin

# 启动 Docker 并设置开机自启
sudo systemctl enable docker
sudo systemctl start docker

# 验证安装
docker --version
docker compose version
```

### 2. 构建前端静态文件（本机执行）

```bash
# 本机执行
cd D:\维修记录web项目\frontend
npm run build
```

构建完成后 `frontend/dist/` 目录会生成静态文件。将整个项目（含 dist）传到服务器。

### 3. 配置环境变量

```bash
# 服务器执行
cd /opt/repair-system
cp backend/.env.example .env

# 编辑 .env，修改数据库密码
nano .env
```

`.env` 内容示例：

```ini
DB_HOST=db
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的强密码（至少12位）
DB_NAME=repair_db
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

> ⚠️ **安全提示**：生产环境请使用强密码，不要用 `root` 或 `123456`。

### 3. 配置环境变量

```bash
# 服务器执行
cd /opt/repair-system
cp backend/.env.example backend/.env

# 编辑 .env，修改数据库密码
nano backend/.env
```

`.env` 内容示例：

```ini
DB_HOST=db
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的强密码（至少12位）
DB_NAME=repair_db
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

> ⚠️ **安全提示**：生产环境请使用强密码，不要用 `root` 或 `123456`。

### 4. 一键启动所有服务

```bash
cd /opt/repair-system

# 后台启动（MySQL + 后端 + Nginx）
docker compose up -d

# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f backend
```

### 5. 导入初始数据库（含222个维修点位）

```bash
cd /opt/repair-system

# 等待 MySQL 容器完全就绪（约10秒）
sleep 10

# 将 database/repair_db.sql 导入到容器中的 MySQL
docker compose exec -T db mysql \
  -u root -p"$(grep DB_PASSWORD backend/.env | cut -d= -f2)" \
  repair_db < database/repair_db.sql

# 验证导入结果
docker compose exec db mysql \
  -u root -p"$(grep DB_PASSWORD backend/.env | cut -d= -f2)" \
  -e "SELECT COUNT(*) AS monitor_points_count FROM repair_db.monitor_points;"
```

期望输出：`222`

### 6. 验证部署

```bash
# 检查服务是否正常
curl http://localhost/health
# 期望返回：{"status":"ok","version":"1.0.0"}
```

浏览器访问 `http://你的服务器IP` 即可使用。

### 常用管理命令

```bash
# 重启所有服务
docker compose restart

# 重启单个服务
docker compose restart backend

# 停止所有服务
docker compose down

# 查看实时日志
docker compose logs -f

# 更新代码后重新部署
git pull
cd frontend && npm run build && cd ..
docker compose up -d --build
```

---

## 方案B：手动部署（不用 Docker）

### 1. 安装系统依赖

```bash
# Ubuntu
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx mysql-server nodejs npm git

# 验证
python3 --version    # 3.10+
node --version       # 18+
mysql --version
nginx -v
```

### 2. 配置 MySQL

```bash
# 启动 MySQL
sudo systemctl enable mysql
sudo systemctl start mysql

# 安全初始化（设置 root 密码）
sudo mysql_secure_installation
```

### 3. 导入数据库（含222个维修点位）

```bash
# 直接从项目目录的 SQL 文件导入（会自动创建 repair_db 库）
sudo mysql -u root -p < /opt/repair-system/database/repair_db.sql

# 验证导入是否成功
sudo mysql -u root -p -e "
  SELECT COUNT(*) AS monitor_points FROM repair_db.monitor_points;
  SELECT username, role FROM repair_db.users;
"
```

期望结果：monitor_points = 222，users 含 admin 管理员账号。

> 如果不导入 SQL 文件，后端首次启动也会自动建表，但 **222个维修点位需要手动重新添加**。

### 3. 部署后端

```bash
cd /opt/repair-system/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建配置文件
cp .env.example .env
nano .env
# 填入 MySQL 密码和数据库信息
```

**安装 PM2 管理进程（推荐）：**

```bash
sudo npm install -g pm2

# 启动后端
pm2 start "source venv/bin/activate && python -m uvicorn main:app --host 127.0.0.1 --port 8000" \
  --name repair-api \
  --cwd /opt/repair-system/backend

# 保存进程列表，设置开机自启
pm2 save
pm2 startup
# 按照输出提示执行对应命令
```

**或者用 systemd 管理：**

```bash
sudo nano /etc/systemd/system/repair-api.service
```

写入以下内容：

```ini
[Unit]
Description=维修记录系统 API
After=network.target mysql.service

[Service]
WorkingDirectory=/opt/repair-system/backend
ExecStart=/opt/repair-system/backend/venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
User=www-data

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable repair-api
sudo systemctl start repair-api
sudo systemctl status repair-api
```

### 4. 构建并部署前端

```bash
# 本机构建（或在服务器上构建）
cd /opt/repair-system/frontend
npm install
npm run build

# 将 dist 目录交给 Nginx 管理
sudo mkdir -p /var/www/repair-system
sudo cp -r dist/* /var/www/repair-system/
sudo chown -R www-data:www-data /var/www/repair-system
```

### 5. 配置 Nginx

```bash
sudo nano /etc/nginx/sites-available/repair-system
```

写入以下内容（替换 `你的域名或IP`）：

```nginx
server {
    listen 80;
    server_name 你的域名或IP;
    charset utf-8;

    # 前端静态文件
    root /var/www/repair-system;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
        expires 1d;
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 120s;
        client_max_body_size 20M;
    }

    # 上传文件访问
    location /uploads/ {
        proxy_pass http://127.0.0.1:8000;
        expires 7d;
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/repair-system /etc/nginx/sites-enabled/
sudo nginx -t          # 检查配置语法
sudo systemctl reload nginx
```

---

## 防火墙配置

```bash
# Ubuntu UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS（如有需要）
sudo ufw enable
sudo ufw status
```

---

## HTTPS 配置（可选，有域名时强烈推荐）

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 自动申请并配置 SSL 证书（替换为你的域名和邮箱）
sudo certbot --nginx -d 你的域名.com -m your@email.com --agree-tos

# 证书自动续期（每90天一次）
sudo systemctl enable certbot.timer
```

---

## 手机访问配置

手机访问需要和服务器在同一网络，或者服务器有公网 IP。

- **局域网**：手机连接同一 Wi-Fi，访问 `http://服务器内网IP`
- **公网**：访问 `http://服务器公网IP` 或绑定域名后访问 `https://你的域名.com`

手机拍照上传功能在 **HTTPS** 下体验更佳（部分 Android 浏览器要求 HTTPS 才能调用摄像头）。

---

## 常见问题排查

### 后端无法连接 MySQL

```bash
# 检查 MySQL 是否运行
sudo systemctl status mysql

# 检查 .env 中的密码是否正确
cat /opt/repair-system/backend/.env

# 测试连接
mysql -u root -p -e "SHOW DATABASES;"
```

### 图片上传失败

```bash
# 检查 uploads 目录权限
ls -la /opt/repair-system/backend/uploads
# 如果不存在，创建并授权
mkdir -p /opt/repair-system/backend/uploads
chmod 755 /opt/repair-system/backend/uploads
```

### 502 Bad Gateway

```bash
# 检查后端是否在运行
curl http://127.0.0.1:8000/health

# 查看后端日志
# Docker 方式：
docker compose logs backend

# PM2 方式：
pm2 logs repair-api

# systemd 方式：
sudo journalctl -u repair-api -n 50
```

### 中文文件名乱码

确保系统语言环境为 UTF-8：

```bash
locale                          # 查看当前语言环境
sudo locale-gen zh_CN.UTF-8
sudo update-locale LANG=zh_CN.UTF-8
```

---

## 目录结构（服务器）

```
/opt/repair-system/
├── backend/
│   ├── .env              ← 生产环境配置（含数据库密码）
│   ├── uploads/          ← 图片存储（建议定期备份）
│   └── ...
├── database/
│   └── repair_db.sql     ← 数据库初始化文件（必须导入）
├── frontend/
│   └── dist/             ← 构建后的静态文件
├── nginx/
│   └── nginx.conf
└── docker-compose.yml
```

---

## 数据备份建议

```bash
# 备份 MySQL 数据库
mysqldump -u root -p repair_db > repair_db_$(date +%Y%m%d).sql

# 备份上传的图片
tar -czf uploads_$(date +%Y%m%d).tar.gz /opt/repair-system/backend/uploads/

# 建议添加到 crontab，每天自动备份
crontab -e
# 添加：每天凌晨2点备份
# 0 2 * * * mysqldump -u root -p密码 repair_db > /backup/repair_db_$(date +\%Y\%m\%d).sql
```

---

*本文档由维修记录系统项目自动生成 — 2026-07-19*
