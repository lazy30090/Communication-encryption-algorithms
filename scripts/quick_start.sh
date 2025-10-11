#!/bin/bash
# 快速启动脚本 - 一键部署加密智能摄像头

echo "========================================="
echo "  加密智能摄像头 - 快速启动脚本"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查Python版本
echo -e "${YELLOW}[1/5] 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到Python3${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"

# 安装依赖
echo ""
echo -e "${YELLOW}[2/5] 安装依赖...${NC}"
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
else
    echo -e "${RED}✗ 依赖安装失败${NC}"
    exit 1
fi

# 生成证书
echo ""
echo -e "${YELLOW}[3/5] 生成TLS证书...${NC}"
if [ ! -f "certs/server.crt" ] || [ ! -f "certs/server.key" ]; then
    python3 scripts/generate_certs.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 证书生成成功${NC}"
    else
        echo -e "${RED}✗ 证书生成失败${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ 证书已存在${NC}"
fi

# 获取IP地址
echo ""
echo -e "${YELLOW}[4/5] 获取网络信息...${NC}"
if command -v hostname &> /dev/null; then
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    echo -e "${GREEN}✓ 本机IP: ${LOCAL_IP}${NC}"
else
    LOCAL_IP="localhost"
    echo -e "${YELLOW}! 无法获取IP地址，使用: localhost${NC}"
fi

# 启动服务器
echo ""
echo -e "${YELLOW}[5/5] 启动服务器...${NC}"
echo ""
echo "========================================="
echo -e "${GREEN}服务器即将启动！${NC}"
echo "========================================="
echo ""
echo "访问方式："
echo "  - 本地访问: https://localhost:8443"
if [ "$LOCAL_IP" != "localhost" ]; then
    echo "  - 局域网访问: https://${LOCAL_IP}:8443"
fi
echo ""
echo "按 Ctrl+C 停止服务器"
echo "========================================="
echo ""

# 启动
python3 server/camera_server.py

