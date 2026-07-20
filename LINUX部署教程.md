# 维修记录系统 — Linux 服务器部署教程

> 适用系统：Ubuntu 20.04 / 22.04 LTS  
> 部署方式：从 GitHub 拉取代码，手动部署（不用 Docker）  
> 最后更新：2026-07-20

---

## 整体流程

```
Windows 本地 ──推送代码──> GitHub ──克隆代码──> Linux 服务器
                                                    │
                                          安装环境 + 配置服务
                                                    │
                                          浏览器访问成功 🎉
```

---

## 第一阶段：服务器环境安装

### 第 1 步：SSH 登录服务器

```bash
ssh root@你的服务器IP
```

首次连接提示 `Are you sure...` 输入 `yes`，再输入服务器密码。

---

### 第 2 步：更新系统

```bash
apt update && apt upgrade -y
```

---

### 第 3 步：安装基础工具

```bash
apt install -y curl wget git unzip vim net-tools
```

---

### 第 4 步：安装 Python 3.10

```bash
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.10 python3.10-venv python3.10-dev python3-pip
```

验证：

```bash
python3.10 --version
# 应显示 Python 3.10.x
```

---

### 第 5 步：安装 Node.js 20

> ⚠️ 必须安装 Node.js **20**，不能用 18（前端 Vite 8 需要 Node 20+）

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
```

验证：

```bash
node --version   # 应显示 v20.x.x
npm --version    # 应显示 10.x.x
```

---

### 第 6 步：安装 MySQL 8.0

```bash
apt install -y mysql-server
systemctl start mysql
systemctl enable mysql
```

**修改 root 认证方式**（Ubuntu 默认使用 socket 认证，需改为密码认证）：

```bash
sudo mysql
```

进入 MySQL 后执行：

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Repair@2026';
FLUSH PRIVILEGES;
EXIT;
```

> 🔒 密码 `Repair@2026` 请记住，后续配置会用到

验证密码登录是否正常：

```bash
mysql -u root -p'Repair@2026' -e "SELECT 1;"
```

---

### 第 7 步：安装 Nginx

```bash
apt install -y nginx
systemctl start nginx
systemctl enable nginx
```

---

### 第 8 步：安装 PM2 和中文字体

```bash
npm install -g pm2
apt install -y fonts-wqy-zenhei fonts-wqy-microhei
```

---

## 第二阶段：部署项目

### 第 9 步：从 GitHub 克隆项目

```bash
cd /opt
git clone https://liu200320@github.com/liu200320/repair-system.git
```

提示输入密码时，填入 GitHub **Personal Access Token**（不是登录密码）。

> 如何生成 Token：GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token，勾选 repo 权限

进入项目目录验证：

```bash
cd repair-system && ls
# 应看到 backend  frontend  database  nginx 等目录
```

---

### 第 10 步：导入数据库

```bash
sudo mysql
```

```sql
source /opt/repair-system/database/repair_db.sql
USE repair_db;
SHOW TABLES;
SELECT COUNT(*) FROM monitor_points;
-- 应显示 222
EXIT;
```

---

### 第 11 步：部署后端

#### 11.1 创建 Python 虚拟环境

```bash
cd /opt/repair-system/backend
python3.10 -m venv venv
source venv/bin/activate
```

> 命令行前出现 `(venv)` 字样说明激活成功

#### 11.2 安装 Python 依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 11.3 创建配置文件

逐条执行（第一条用 `>`，后续用 `>>`）：

```bash
echo "DB_HOST=localhost" > /opt/repair-system/backend/.env
echo "DB_PORT=3306" >> /opt/repair-system/backend/.env
echo "DB_USER=root" >> /opt/repair-system/backend/.env
echo "DB_PASSWORD=Repair@2026" >> /opt/repair-system/backend/.env
echo "DB_NAME=repair_db" >> /opt/repair-system/backend/.env
echo "UPLOAD_DIR=uploads" >> /opt/repair-system/backend/.env
echo "MAX_FILE_SIZE=10485760" >> /opt/repair-system/backend/.env
```

验证内容：

```bash
cat /opt/repair-system/backend/.env
```

#### 11.4 创建上传目录

```bash
mkdir -p /opt/repair-system/backend/uploads/exports
chmod 755 /opt/repair-system/backend/uploads
```

#### 11.5 退出虚拟环境

```bash
deactivate
```

#### 11.6 用 PM2 启动后端

```bash
pm2 start "/opt/repair-system/backend/venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000" --name repair-api --cwd /opt/repair-system/backend
```

验证后端正常运行：

```bash
sleep 5 && curl http://127.0.0.1:8000/health
# 应返回：{"status":"ok","version":"2.0.0"}
```

#### 11.7 设置 PM2 开机自启

```bash
pm2 save
pm2 startup
systemctl start pm2-root
```

---

### 第 12 步：构建并部署前端

```bash
cd /opt/repair-system/frontend
npm config set registry https://registry.npmmirror.com
npm install
npm run build
```

> ⏳ 构建约需 1 分钟

验证：

```bash
ls dist/
# 应看到 index.html 和 assets/ 目录
```

部署到 Nginx 目录：

```bash
mkdir -p /var/www/repair-system
cp -r dist/* /var/www/repair-system/
chown -R www-data:www-data /var/www/repair-system
```

---

### 第 13 步：配置 Nginx

直接使用项目内的配置文件（**将 `你的域名或IP` 替换为实际值**）：

先修改配置文件中的域名：

```bash
sed -i 's/weihu.kuoci.top 38.76.190.253/你的域名 你的IP/' /opt/repair-system/nginx/repair-system-site.conf
```

然后复制并启用：

```bash
cp /opt/repair-system/nginx/repair-system-site.conf /etc/nginx/sites-available/repair-system
ln -s /etc/nginx/sites-available/repair-system /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
```

测试并重载：

```bash
nginx -t
systemctl reload nginx
```

> ✅ 必须看到 `syntax is ok` 才继续

---

### 第 14 步：开放防火墙

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

提示 `Proceed with operation (y|n)?` 输入 `y`

---

### 第 15 步：创建管理员账号

```bash
source /opt/repair-system/backend/venv/bin/activate
```

生成密码哈希（复制输出的那串 `$2b$...`）：

```bash
python3 -c "from passlib.context import CryptContext; ctx = CryptContext(schemes=['bcrypt']); print(ctx.hash('admin123'))"
```

退出虚拟环境后插入用户（将 `粘贴哈希值` 替换为上面复制的内容）：

```bash
deactivate
mysql -u root -p'Repair@2026' repair_db -e "INSERT INTO users (username, hashed_pw, full_name, role, is_active) VALUES ('admin', '粘贴哈希值', '管理员', 'admin', 1);"
```

验证：

```bash
mysql -u root -p'Repair@2026' -e "SELECT id, username, role FROM repair_db.users;"
```

---

## 第三阶段：验证部署结果

```bash
# 后端健康检查
curl http://127.0.0.1:8000/health

# 前端页面检查
curl -s http://127.0.0.1/ | grep '<div id="app">'

# 查看所有服务状态
pm2 list
systemctl is-enabled mysql nginx
systemctl status pm2-root
```

全部正常后，**浏览器访问 `http://你的域名或IP`**：

- 默认账号：`admin`
- 默认密码：`admin123`
- **登录后立即修改密码！**

---

## 后续代码更新流程

### Windows 端推送新代码

```bash
cd D:\维修记录web项目
git add .
git commit -m "更新说明"
git push github master
```

### 服务器端拉取并重启

```bash
cd /opt/repair-system
git pull

# 重启后端
pm2 restart repair-api

# 如果前端有改动，重新构建
cd frontend && npm run build && cp -r dist/* /var/www/repair-system/
```

---

## 常用维护命令

| 操作 | 命令 |
|------|------|
| 查看后端状态 | `pm2 list` |
| 查看后端日志 | `pm2 logs repair-api` |
| 重启后端 | `pm2 restart repair-api` |
| 重载 Nginx | `systemctl reload nginx` |
| 重启 MySQL | `systemctl restart mysql` |
| 拉取最新代码 | `cd /opt/repair-system && git pull` |
| 查看 Nginx 错误 | `tail -50 /var/log/nginx/error.log` |

---

## 常见问题

### 后端启动失败 (curl 连接被拒)

```bash
pm2 logs repair-api --lines 30 --nostream
```

检查日志中的具体报错，常见原因：
- 缺少 Python 包 → `source venv/bin/activate && pip install 包名`
- 数据库连接失败 → 检查 `.env` 中密码是否正确

### 浏览器显示 502 Bad Gateway

后端未运行：

```bash
pm2 list         # 查看 repair-api 是否 online
pm2 restart repair-api
```

### 重启服务器后无法访问

```bash
systemctl start mysql nginx
systemctl start pm2-root
```

---

*文档版本：2.0（根据实际部署整理）| 日期：2026-07-20*
