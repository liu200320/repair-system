# 维修记录系统 — GitHub 部署完整教程

> 适用：完全零基础小白  
> 服务器系统：Ubuntu 20.04 / 22.04 LTS（阿里云、腾讯云、华为云均可）  
> 部署方式：GitHub 拉取代码 + 手动部署（不用 Docker）

---

## 整体流程图

```
你的电脑（Windows）                    GitHub                    Linux 服务器
      |                                   |                           |
  1. 注册 GitHub 账号                     |                           |
  2. 创建仓库                             |                           |
  3. 推送代码 ──────────────────────────> |                           |
                                          |  4. 服务器安装环境         |
                                          |  5. 从 GitHub 拉取代码 <──|
                                          |  6. 配置并启动服务         |
                                          |  7. 浏览器访问成功！        |
```

---

## 第一阶段：在 Windows 上把代码推送到 GitHub

### 第 1 步：注册 GitHub 账号

1. 打开浏览器，访问 https://github.com
2. 点击右上角 **Sign up**
3. 填写邮箱、密码、用户名，完成注册
4. 登录 GitHub

### 第 2 步：安装 Git（如果已安装可跳过）

1. 访问 https://git-scm.com/download/win
2. 下载并安装（一路点 Next 即可）
3. 安装完成后，在 Windows 搜索栏搜索 **Git Bash**，能打开说明安装成功

### 第 3 步：配置 Git 身份（每台电脑只需做一次）

打开 **Git Bash** 或 **CMD**，运行：

```bash
git config --global user.name "你的名字"
git config --global user.email "你注册GitHub用的邮箱"
```

### 第 4 步：在 GitHub 创建仓库

1. 登录 GitHub，点击右上角 **+** → **New repository**
2. 填写：
   - **Repository name**：`repair-system`（仓库名，可自定义）
   - **Description**：维修记录管理系统（可选）
   - **Private** ✅（选私有，代码不公开）
3. **不要勾选** "Add a README file"（因为本地已有代码）
4. 点击 **Create repository**
5. 页面会显示仓库地址，类似：
   ```
   https://github.com/你的用户名/repair-system.git
   ```
   **复制这个地址备用**

### 第 5 步：推送代码到 GitHub

打开 **CMD 命令提示符**，切换到项目目录：

```bash
cd D:\维修记录web项目
```

依次执行以下命令：

```bash
# 查看当前 git 状态
git status

# 添加所有文件（.gitignore 会自动排除不需要的文件）
git add .

# 提交代码（-m 后面是提交说明）
git commit -m "初始版本：准备部署"

# 关联 GitHub 远程仓库（将下面的地址换成你第4步复制的地址）
git remote add origin https://github.com/你的用户名/repair-system.git

# 推送代码到 GitHub
git push -u origin master
```

> ⚠️ **推送时会弹出登录窗口**，输入你的 GitHub 账号和密码登录即可。  
> 如果提示"Support for password authentication was removed"，需要用 Token，见下方说明。

#### 解决密码认证问题（如果 push 失败）

1. GitHub 右上角头像 → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. 点击 **Generate new token (classic)**
3. Note 填写 `deploy`，Expiration 选 **No expiration**，勾选 **repo** 权限
4. 点击 **Generate token**，**立即复制 token**（只显示一次！）
5. 重新 push 时，密码那里粘贴这个 token

### 第 6 步：验证推送成功

刷新 GitHub 仓库页面，能看到你的文件就说明推送成功了。

---

## 第二阶段：在 Linux 服务器上部署

### 第 7 步：登录服务器

在 Windows CMD 中：

```bash
ssh root@你的服务器IP
```

首次连接提示 `Are you sure you want to continue connecting?` 输入 `yes` 回车，再输入服务器密码。

> 💡 **推荐使用 MobaXterm**（免费好用的 SSH 工具）：https://mobaxterm.mobatek.net/download.html  
> 打开 → Session → SSH → 填写 IP、用户名 root → OK → 输入密码

---

### 第 8 步：安装系统环境

**以下命令全部在 Linux 服务器上执行，逐条粘贴运行：**

#### 8.1 更新系统

```bash
apt update && apt upgrade -y
```

#### 8.2 安装基础工具

```bash
apt install -y curl wget git unzip vim net-tools
```

#### 8.3 安装 Python 3.10

```bash
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.10 python3.10-venv python3.10-dev python3-pip

# 验证（应显示 Python 3.10.x）
python3.10 --version
```

#### 8.4 安装 Node.js 18

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# 验证
node --version    # 应显示 v18.x.x
npm --version     # 应显示 9.x.x 或以上
```

#### 8.5 安装 MySQL 8.0

```bash
apt install -y mysql-server
systemctl start mysql
systemctl enable mysql

# 验证（看到 Active: active (running) 表示成功）
systemctl status mysql
```

初始化 MySQL 安全设置：

```bash
mysql_secure_installation
```

按提示操作：
- `VALIDATE PASSWORD component?` → 输入 `n` 回车
- `New password:` → 输入密码，例如 `Repair@2026`（**记住这个密码！**）
- `Re-enter new password:` → 再次输入相同密码
- 后续所有提示 → 全部输入 `y` 回车

#### 8.6 安装 Nginx

```bash
apt install -y nginx
systemctl start nginx
systemctl enable nginx

# 验证
systemctl status nginx
```

#### 8.7 安装 PM2（管理后端进程）

```bash
npm install -g pm2
pm2 --version    # 验证安装
```

#### 8.8 安装中文字体（水印功能需要）

```bash
apt install -y fonts-wqy-zenhei fonts-wqy-microhei
```

---

### 第 9 步：从 GitHub 克隆项目

```bash
# 进入 /opt 目录（存放项目的位置）
cd /opt

# 从 GitHub 克隆项目（换成你自己的仓库地址）
git clone https://github.com/你的用户名/repair-system.git

# 进入项目目录
cd repair-system

# 验证文件都在
ls
# 应看到：backend  frontend  database  nginx  docker-compose.yml 等
```

> ⚠️ 如果仓库是 **Private（私有）** 的，克隆时需要输入 GitHub 账号和 Token（同第6步的 Token）

---

### 第 10 步：导入数据库

```bash
# 登录 MySQL（输入第8.5步设置的密码）
mysql -u root -p

# 在 MySQL 提示符内执行（注意：source 命令用全路径）
source /opt/repair-system/database/repair_db.sql

# 验证导入成功
USE repair_db;
SHOW TABLES;
SELECT COUNT(*) FROM monitor_points;
# 应显示 222

# 退出 MySQL
EXIT;
```

---

### 第 11 步：部署后端

#### 11.1 进入后端目录

```bash
cd /opt/repair-system/backend
```

#### 11.2 创建 Python 虚拟环境

```bash
python3.10 -m venv venv
source venv/bin/activate
# 激活后命令行前面会出现 (venv) 字样
```

#### 11.3 安装 Python 依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
# 这步需要几分钟，耐心等待
```

#### 11.4 创建配置文件

```bash
# 查看是否有 .env.example
ls -la | grep .env

# 创建 .env 文件
nano .env
```

在编辑器中输入以下内容（**将密码替换为你在第8.5步设置的**）：

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Repair@2026
DB_NAME=repair_db
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

按 `Ctrl+X` → 输入 `Y` → 回车，保存退出。

#### 11.5 创建上传目录

```bash
mkdir -p uploads/exports
chmod 755 uploads
```

#### 11.6 退出虚拟环境

```bash
deactivate
```

#### 11.7 用 PM2 启动后端

```bash
pm2 start "/opt/repair-system/backend/venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000" \
  --name repair-api \
  --cwd /opt/repair-system/backend

# 验证后端是否启动成功
curl http://127.0.0.1:8000/health
# 应返回：{"status":"ok","version":"2.0.0"}
```

#### 11.8 设置 PM2 开机自启

```bash
pm2 save
pm2 startup
# 复制输出的那条以 sudo 开头的命令，粘贴回车执行
```

---

### 第 12 步：构建并部署前端

#### 12.1 安装依赖并构建

```bash
cd /opt/repair-system/frontend
npm install
npm run build

# 构建完成后验证
ls dist/
# 应看到：index.html  assets/
```

#### 12.2 部署到 Nginx 目录

```bash
mkdir -p /var/www/repair-system
cp -r dist/* /var/www/repair-system/
chown -R www-data:www-data /var/www/repair-system
```

---

### 第 13 步：配置 Nginx

#### 13.1 创建站点配置

```bash
nano /etc/nginx/sites-available/repair-system
```

粘贴以下内容（**将 `你的服务器IP` 替换为实际IP地址**）：

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

    # 后端 API 代理
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

按 `Ctrl+X` → `Y` → 回车保存。

#### 13.2 启用站点配置

```bash
# 启用配置
ln -s /etc/nginx/sites-available/repair-system /etc/nginx/sites-enabled/

# 检查配置语法（必须显示 ok）
nginx -t

# 重新加载 Nginx
systemctl reload nginx
```

---

### 第 14 步：开放防火墙端口

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# 查看状态
ufw status
```

> ⚠️ **云服务器还需要在控制台开放端口：**
>
> **阿里云**：控制台 → 云服务器ECS → 选中你的服务器 → 安全组 → 入方向 → 添加规则 → 协议TCP，端口80
>
> **腾讯云**：控制台 → 云服务器CVM → 安全组 → 添加规则 → HTTP 80端口
>
> **华为云**：控制台 → 弹性云服务器 → 安全组 → 入方向规则 → 添加 → TCP 80端口

---

### 第 15 步：验证部署结果

```bash
# 1. 检查后端运行状态
curl http://127.0.0.1:8000/health
# 期望返回：{"status":"ok","version":"2.0.0"}

# 2. 检查 Nginx 响应
curl http://localhost/
# 期望返回 HTML 内容（包含 <html> 标签）

# 3. 查看所有服务状态一览
pm2 list               # 后端进程 → 应显示 online
systemctl status nginx  # → 应显示 active (running)
systemctl status mysql  # → 应显示 active (running)
```

**用浏览器访问 `http://你的服务器IP`**，看到登录页即表示部署成功！🎉

- **默认账号**：`admin`
- **默认密码**：`admin123`
- **登录后请立即修改密码！**

---

## 第三阶段：后续代码更新流程

当你修改了代码，按以下步骤更新服务器：

### Windows 端：推送新代码

```bash
# 在 CMD 中，进入项目目录
cd D:\维修记录web项目

# 添加改动、提交、推送
git add .
git commit -m "更新说明：描述这次改了什么"
git push
```

### Linux 服务器端：拉取并重启

```bash
# 进入项目目录
cd /opt/repair-system

# 拉取最新代码
git pull

# 重启后端
pm2 restart repair-api

# 如果前端有改动，重新构建
cd frontend
npm run build
cp -r dist/* /var/www/repair-system/
```

---

## 常见问题排查

### 问题 1：git push 时报错 "Authentication failed"

**解决**：使用 Personal Access Token（见第6步）

### 问题 2：git clone 私有仓库失败

输入用户名时填 GitHub 账号，密码填 Token（不是 GitHub 密码）

### 问题 3：浏览器显示 502 Bad Gateway

后端没有正常启动：

```bash
pm2 list              # 看 repair-api 是否是 online 状态
pm2 logs repair-api   # 查看详细错误信息
```

常见原因：`.env` 里数据库密码填写有误，或 MySQL 没有启动

```bash
systemctl start mysql   # 启动 MySQL
pm2 restart repair-api  # 重启后端
```

### 问题 4：浏览器显示 403 Forbidden

```bash
chown -R www-data:www-data /var/www/repair-system/
chmod -R 755 /var/www/repair-system/
```

### 问题 5：图片上传失败

```bash
chmod 755 /opt/repair-system/backend/uploads/
```

### 问题 6：服务器重启后系统无法访问

```bash
systemctl start mysql
systemctl start nginx
pm2 resurrect    # 恢复所有 PM2 进程
```

### 问题 7：npm install 卡住不动（网络慢）

切换淘宝镜像源：

```bash
npm config set registry https://registry.npmmirror.com
npm install
```

### 问题 8：pip install 下载慢

切换清华镜像源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 常用维护命令速查

| 操作 | 命令 |
|------|------|
| 重启后端 | `pm2 restart repair-api` |
| 查看后端日志 | `pm2 logs repair-api` |
| 重载 Nginx（不中断服务） | `systemctl reload nginx` |
| 重启 Nginx | `systemctl restart nginx` |
| 重启 MySQL | `systemctl restart mysql` |
| 查看所有进程 | `pm2 list` |
| 查看 Nginx 错误日志 | `tail -50 /var/log/nginx/error.log` |
| 拉取最新代码 | `cd /opt/repair-system && git pull` |

---

*文档版本：1.0 | 创建日期：2026-07-20*
