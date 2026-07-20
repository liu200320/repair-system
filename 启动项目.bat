@echo off
chcp 65001 >nul
title 维修记录系统 - 启动中...

echo ================================================
echo   维修记录管理系统 - 一键启动脚本
echo ================================================
echo.

:: -------- 路径配置（如有变动请修改这里）--------
set PROJECT_DIR=D:\维修记录web项目
set MYSQL_BIN=D:\phpstudy_pro\Extensions\MySQL8.0.12\bin
set BACKEND_PORT=8000
set FRONTEND_PORT=5173
:: -----------------------------------------------

:: 检查 MySQL 是否在运行
echo [1/3] 检查 MySQL 服务...
tasklist /FI "IMAGENAME eq mysqld.exe" 2>nul | find /I "mysqld.exe" >nul
if %errorlevel% equ 0 (
    echo        MySQL 已在运行 ✓
) else (
    echo        MySQL 未运行，尝试启动...
    start "" "%MYSQL_BIN%\mysqld.exe"
    timeout /t 3 /nobreak >nul
    tasklist /FI "IMAGENAME eq mysqld.exe" 2>nul | find /I "mysqld.exe" >nul
    if %errorlevel% neq 0 (
        echo [错误] MySQL 启动失败，请手动启动 phpstudy 中的 MySQL 服务！
        pause
        exit /b 1
    )
    echo        MySQL 启动成功 ✓
)
echo.

:: 启动后端
echo [2/3] 启动后端服务 (端口 %BACKEND_PORT%)...
netstat -ano 2>nul | find ":%BACKEND_PORT% " | find "LISTEN" >nul
if %errorlevel% equ 0 (
    echo        后端已在运行 ✓
) else (
    start "维修系统 - 后端" cmd /k "cd /d %PROJECT_DIR%\backend && echo 后端启动中... && python -m uvicorn main:app --host 0.0.0.0 --port %BACKEND_PORT% && pause"
    echo        后端窗口已打开，等待就绪...
    timeout /t 3 /nobreak >nul
)
echo.

:: 启动前端
echo [3/3] 启动前端服务 (端口 %FRONTEND_PORT%)...
netstat -ano 2>nul | find ":%FRONTEND_PORT% " | find "LISTEN" >nul
if %errorlevel% equ 0 (
    echo        前端已在运行 ✓
) else (
    start "维修系统 - 前端" cmd /k "cd /d %PROJECT_DIR%\frontend && echo 前端启动中... && npm run dev && pause"
    echo        前端窗口已打开，等待就绪...
    timeout /t 5 /nobreak >nul
)
echo.

:: 打开浏览器
echo ================================================
echo   启动完成！
echo.
echo   前端地址: http://localhost:%FRONTEND_PORT%
echo   API 文档: http://localhost:%BACKEND_PORT%/docs
echo ================================================
echo.
start "" "http://localhost:%FRONTEND_PORT%"

echo 按任意键退出此窗口（服务继续在各自窗口运行）
pause >nul
