@echo off
REM 快速启动脚本 - Windows版本

echo =========================================
echo   加密智能摄像头 - 快速启动脚本
echo =========================================
echo.

REM 检查Python
echo [1/5] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python
    pause
    exit /b 1
)
echo 成功: Python已安装
echo.

REM 创建虚拟环境
echo [2/5] 安装依赖...
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -q --upgrade pip
pip install -q -r requirements.txt

if errorlevel 1 (
    echo 依赖安装失败
    pause
    exit /b 1
)
echo 成功: 依赖安装完成
echo.

REM 生成证书
echo [3/5] 生成TLS证书...
if not exist "certs\server.crt" (
    python scripts\generate_certs.py
    if errorlevel 1 (
        echo 证书生成失败
        pause
        exit /b 1
    )
    echo 成功: 证书生成完成
) else (
    echo 证书已存在
)
echo.

REM 获取IP
echo [4/5] 获取网络信息...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set LOCAL_IP=%%a
set LOCAL_IP=%LOCAL_IP:~1%
echo 本机IP: %LOCAL_IP%
echo.

REM 启动服务器
echo [5/5] 启动服务器...
echo.
echo =========================================
echo 服务器即将启动！
echo =========================================
echo.
echo 访问方式：
echo   - 本地访问: https://localhost:8443
echo   - 局域网访问: https://%LOCAL_IP%:8443
echo.
echo 按 Ctrl+C 停止服务器
echo =========================================
echo.

python server\camera_server.py

pause

