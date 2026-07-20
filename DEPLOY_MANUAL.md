# 维修记录系统 — Linux 手动部署完整教程

> 适用：Ubuntu 20.04 / 22.04 LTS（阿里云、腾讯云、华为云均可）  
> 方式：不使用 Docker，全部手动安装，适合新手

---

## 准备工作

### 需要什么

- 一台 Linux 服务器（1核2GB 起步，推荐 2核4GB）
- 服务器的 IP 地址、root 用户密码
- 本机安装 **FileZilla**（用于上传文件，免费）  
  下载地址：https://filezilla-project.org/download.php

---

## 第一步：连接服务器

### 方式一：Windows 用 CMD 连接

按 `Win + R` 输入 `cmd` 回车，然后输入：

```
ssh root@你的服务器IP
```

提示 `Are you sure...` 输入 `yes` 回车，再输入服务器密码。

### 方式二：用 PuTTY（可视化工具）

1. 下载：https://www.putty.org/
2. 打开 PuTTY → 填写 IP → 端口22 → 点 Open → 输入 root + 密码

---

## 第二步：服务器安装基础环境

连接服务器后，逐条运行以下命令：

### 2.1 更新系统

```bash
apt update && apt upgrade -y
```

> 这一步可能需要几分钟，等待完成。

### 2.2 安装常用工具

```bash
apt install -y curl wget git unzip vim net-tools
```

### 2.3 安装 Python 3.10

Ubuntu 20.04 自带 Python3，但版本可能不够。安装3.10：

```bash
# 添加源
add-apt-repository ppa:deadsnakes/ppa -y
apt update

# 安装 Python 3.10 及工具
apt install -y python3.10 python3.10-venv python3.10-dev python3-pip

# 验证
python3.10 --version
# 应显示：Python 3.10.x
```

### 2.4 安装 Node.js 18

```bash
# 官方安装脚本
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# 验证
node --version    # 应显示 v18.x.x
npm --version     # 应显示 9.x.x 或以上
```

### 2.5 安装 MySQL 8.0

```bash
# 安装 MySQL
apt install -y mysql-server

# 启动并设置开机自启
systemctl start mysql
systemctl enable mysql

# 验证
systemctl status mysql
# 看到 Active: active (running) 表示成功
```

初始化 MySQL 安全设置：

```bash
mysql_secure_installation
```

按提示操作：
- `VALIDATE PASSWORD component?` → 输入 `n` 回车（跳过密码复杂度）
- `New password:` → 输入你想设置的密码（如 `Repair@2026`）
- `Re-enter new password:` → 再次输入密码
- 后续所有提示 → 全部输入 `y` 回车

### 2.6 安装 Nginx

```bash
apt install -y nginx

# 启动并设置开机自启
systemctl start nginx
systemctl enable nginx

# 验证（浏览器访问你的 IP，看到 Nginx 欢迎页表示成功）
systemctl status nginx
```

### 2.7 安装 PM2（管理后端进程）

```bash
npm install -g pm2
pm2 --version    # 验证安装
```

### 2.8 安装中文字体（水印需要）

```bash
apt install -y fonts-wqy-zenhei fonts-wqy-microhei
```

---

## 第三步：上传项目文件

### 使用 FileZilla 上传

1. 打开 FileZilla
2. 顶部填写：
   - 主机：`你的服务器IP`
   - 用户名：`root`
   - 密码：`服务器密码`
   - 端口：`22`
3. 点击「快速连接」
4. 右侧（服务器端）导航到 `/opt/` 目录
5. 右键 → 新建目录 → 输入 `repair-system`
6. 左侧（本机）找到 `D:\维修记录web项目`
7. **全选所有文件和文件夹** → 拖到右侧 `/opt/repair-system/`
8. 等待上传完成（根据网速需要几分钟）

> ⚠️ `backend/uploads/` 目录如果有很多图片会很慢，可以先不传，部署后再传。

### 验证上传

回到服务器 SSH 窗口：

```bash
ls /opt/repair-system/
# 应看到：backend  database  docker-compose.yml  frontend  nginx  README.md 等
```

---

## 第四步：导入数据库

```bash
# 登录 MySQL（输入刚才设置的密码）
mysql -u root -p

# 在 MySQL 内执行（导入数据库文件）
source /opt/repair-system/database/repair_db.sql

# 验证
USE repair_db;
SHOW TABLES;
SELECT COUNT(*) FROM monitor_points;
# 应显示 222

# 退出
EXIT;
```

---

## 第五步：部署后端

### 5.1 进入后端目录

```bash
cd /opt/repair-system/backend
```

### 5.2 创建并激活 Python 虚拟环境

```bash
python3.10 -m venv venv
source venv/bin/activate

# 激活后命令行前面会出现 (venv) 字样
```

### 5.3 安装 Python 依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt

# 这步需要几分钟，等待所有包安装完成
```

### 5.4 创建配置文件

```bash
cp .env.example .env
vim .env
```

在 vim 里按 `i` 进入编辑模式，修改内容为：

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Repair@2026
DB_NAME=repair_db
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

修改完按 `Esc`，然后输入 `:wq` 回车保存退出。

> 如果不熟悉 vim，可以用 nano 代替：`nano .env`，修改完按 `Ctrl+X` → `Y` → 回车保存。

### 5.5 创建上传目录

```bash
mkdir -p uploads/exports
chmod 755 uploads
```

### 5.6 退出虚拟环境

```bash
deactivate
```

### 5.7 用 PM2 启动后端

```bash
pm2 start "/opt/repair-system/backend/venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000" \
  --name repair-api \
  --cwd /opt/repair-system/backend

# 验证后端是否启动
curl http://127.0.0.1:8000/health
# 应返回：{"status":"ok","version":"2.0.0"}
```

### 5.8 设置 PM2 开机自启

```bash
pm2 save
pm2 startup
# 复制输出的那条命令，粘贴回车执行（每台服务器命令略有不同）
```

---

## 第六步：构建并部署前端

### 6.1 安装前端依赖

```bash
cd /opt/repair-system/frontend
npm install
```

### 6.2 构建前端

```bash
npm run build

# 构建完成后会生成 dist/ 目录
ls dist/
# 应看到：index.html  assets/
```

### 6.3 复制到 Nginx 目录

```bash
mkdir -p /var/www/repair-system
cp -r dist/* /var/www/repair-system/
chown -R www-data:www-data /var/www/repair-system
```

---

## 第七步：配置 Nginx

### 7.1 创建站点配置

```bash
vim /etc/nginx/sites-available/repair-system
```

按 `i` 进入编辑，粘贴以下内容（**把`你的服务器IP`替换为实际IP**）：

```nginx
server {
    listen 80;
    server_name 你的服务器IP;
    charset utf-8;

    # 前端静态文件
    root /var/www/repair-system;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
        expires 1d;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 120s;
        client_max_body_size 20M;
    }

    # 上传的图片
    location /uploads/ {
        proxy_pass http://127.0.0.1:8000;
        expires 7d;
    }
}
```

按 `Esc` → 输入 `:wq` → 回车保存。

### 7.2 启用站点

```bash
# 启用配置
ln -s /etc/nginx/sites-available/repair-system /etc/nginx/sites-enabled/

# 检查配置语法
nginx -t
# 应显示：syntax is ok / test is successful

# 重新加载 Nginx
systemctl reload nginx
```

---

## 第八步：开放防火墙端口

```bash
# 开放 80（HTTP）和 22（SSH）端口
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# 查看状态
ufw status
```

如果服务器在阿里云/腾讯云，还需要在**控制台**的「安全组」里开放 80 端口：
- 阿里云：控制台 → 云服务器ECS → 安全组 → 入方向 → 添加规则 → 端口80/HTTP
- 腾讯云：控制台 → 云服务器 → 安全组 → 添加规则 → HTTP 80

---

## 第九步：验证部署

```bash
# 1. 检查后端是否正常
curl http://127.0.0.1:8000/health
# 应返回：{"status":"ok","version":"2.0.0"}

# 2. 检查 Nginx 是否正常
curl http://localhost/
# 应返回 HTML 内容

# 3. 查看所有服务状态
pm2 list              # 后端进程
systemctl status nginx # Nginx
systemctl status mysql # MySQL
```

**浏览器访问 `http://你的服务器IP`**，看到登录页面即表示部署成功！

默认账号：`admin` / `admin123`（**登录后请立即修改密码**）

---

## 常见问题

### 问：浏览器显示 502 Bad Gateway

说明后端没启动。检查：

```bash
pm2 list              # 看 repair-api 状态是否 online
pm2 logs repair-api   # 查看报错信息
```

常见原因：
- `.env` 里数据库密码填错了
- MySQL 没启动：`systemctl start mysql`

### 问：访问提示 403 Forbidden

```bash
# 检查前端文件权限
ls -la /var/www/repair-system/
chown -R www-data:www-data /var/www/repair-system/
chmod -R 755 /var/www/repair-system/
```

### 问：图片上传失败

```bash
# 检查上传目录权限
ls -la /opt/repair-system/backend/uploads/
chmod 755 /opt/repair-system/backend/uploads/
```

### 问：重启服务器后系统不可用

```bash
# 手动重启所有服务
systemctl start mysql
systemctl start nginx
pm2 resurrect    # 恢复 PM2 进程

# 如果 pm2 resurrect 不管用：
cd /opt/repair-system/backend
pm2 start "/opt/repair-system/backend/venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000" --name repair-api --cwd /opt/repair-system/backend
```

---

## 以后更新代码

```bash
# 1. 上传新文件（FileZilla 直接覆盖）

# 2. 重启后端
pm2 restart repair-api

# 3. 如果前端有改动，在本机重新 build 后上传 dist/ 目录
# 然后在服务器执行：
cp -r /opt/repair-system/frontend/dist/* /var/www/repair-system/
```

---

## 快速重启命令备忘

```bash
pm2 restart repair-api          # 重启后端
pm2 logs repair-api             # 查看后端日志
systemctl reload nginx          # 重载 Nginx（不中断服务）
systemctl restart nginx         # 完全重启 Nginx
systemctl restart mysql         # 重启 MySQL
```

---

*部署日期：2026-07-19 | 系统版本：2.0.0*
