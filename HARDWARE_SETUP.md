# 🔧 树莓派硬件部署指南

本文档详细说明如何在树莓派上部署加密智能摄像头系统。

---

## 📋 硬件要求

### 必需硬件
- **树莓派**：3B+ / 4B / 5（推荐4B或5）
- **摄像头模块**：
  - 树莓派官方摄像头模块 v2 或 v3（推荐）
  - 或兼容的CSI接口摄像头
- **存储卡**：16GB以上 microSD卡（推荐Class 10或更高）
- **电源**：5V 3A USB-C电源适配器（树莓派4/5）或 5V 2.5A Micro USB（树莓派3）

### 可选硬件
- 散热片/风扇（长时间运行推荐）
- 保护外壳
- 以太网线（更稳定的网络连接）

---

## 🖥️ 系统准备

### 1. 安装操作系统

**推荐系统**：Raspberry Pi OS (64-bit) Lite 或 Desktop

**安装步骤**：

```bash
# 方法1: 使用Raspberry Pi Imager（推荐）
# 下载地址: https://www.raspberrypi.com/software/
# 1. 下载并安装 Raspberry Pi Imager
# 2. 选择操作系统: Raspberry Pi OS (64-bit)
# 3. 选择存储卡
# 4. 配置WiFi和SSH（点击齿轮图标）
# 5. 写入镜像

# 方法2: 手动烧录
# 1. 下载镜像文件
# 2. 使用 balenaEtcher 或 dd 命令写入SD卡
```

### 2. 首次启动配置

```bash
# 通过SSH连接树莓派（如果启用了SSH）
ssh pi@raspberrypi.local
# 默认密码: raspberry（建议修改）

# 或直接连接显示器和键盘

# 更新系统
sudo apt update && sudo apt upgrade -y

# 配置树莓派（可选）
sudo raspi-config
# 推荐配置:
# - 1 System Options -> S4 Hostname: 修改主机名
# - 3 Interface Options -> I1 Camera: 启用摄像头（旧版本）
# - 5 Localisation Options: 设置时区和键盘
```

### 3. 启用摄像头

```bash
# 对于树莓派4/5（使用libcamera）
# 摄像头应该自动启用，测试一下：
libcamera-hello

# 如果显示摄像头画面，说明正常工作

# 如果出错，检查连接：
vcgencmd get_camera
# 输出应该是: supported=1 detected=1

# 如果 detected=0，检查：
# 1. 摄像头排线是否正确插入（蓝色朝向以太网口）
# 2. 排线是否损坏
# 3. 重启树莓派后再试
```

---

## 📦 安装项目

### 1. 克隆项目

```bash
# 创建项目目录
mkdir -p ~/projects
cd ~/projects

# 克隆项目（如果是从git）
git clone <你的仓库地址> camera-project
cd camera-project

# 或者通过其他方式传输文件到树莓派
# 比如使用scp:
# scp -r /path/to/project pi@raspberrypi.local:~/projects/
```

### 2. 安装系统依赖

```bash
# 更新包列表
sudo apt update

# 安装必需的系统包
sudo apt install -y python3-pip python3-picamera2 python3-pil

# 验证安装
python3 -c "from picamera2 import Picamera2; print('PiCamera2 安装成功')"
```

### 3. 安装Python依赖

```bash
# 安装项目依赖
pip3 install -r requirements.txt

# 验证Flask安装
python3 -c "import flask; print('Flask版本:', flask.__version__)"

# 验证cryptography安装
python3 -c "import cryptography; print('Cryptography安装成功')"
```

### 4. 生成TLS证书

```bash
# 运行证书生成脚本
python3 scripts/generate_certs.py

# 验证证书生成
ls -lh certs/
# 应该看到 server.crt 和 server.key
```

---

## 🚀 启动服务

### 手动启动

```bash
# 进入项目目录
cd ~/projects/camera-project

# 启动服务器
python3 server/camera_server.py

# 看到以下输出说明成功：
# INFO - 初始化 PiCamera2 摄像头...
# INFO - 摄像头配置完成 - 分辨率: 640x480
# INFO - 摄像头已启动
# INFO - 启动HTTPS服务器 - https://0.0.0.0:8443
```

### 测试访问

```bash
# 1. 获取树莓派IP地址
hostname -I
# 输出示例: 192.168.1.100

# 2. 在电脑浏览器中访问
# https://192.168.1.100:8443

# 3. 首次访问会提示证书不安全
# 点击"高级" -> "继续访问"即可
```

---

## 🔧 硬件交互说明

### 摄像头工作原理

```
树莓派硬件层次：

┌─────────────────────────────────┐
│  Python应用层 (camera_server.py)│
│         ↓                        │
│  PiCamera2 库（软件接口）        │
│         ↓                        │
│  libcamera（相机框架）           │
│         ↓                        │
│  内核驱动（Camera Driver）       │
│         ↓                        │
│  CSI接口（硬件连接）             │
│         ↓                        │
│  摄像头模块（硬件）              │
└─────────────────────────────────┘
```

### 代码如何与硬件交互

```python
# 1. 导入PiCamera2库（这是软件接口）
from picamera2 import Picamera2

# 2. 创建摄像头对象（连接到硬件）
camera = Picamera2()

# 3. 配置摄像头参数
config = camera.create_still_configuration(
    main={"size": (640, 480)}  # 设置分辨率
)
camera.configure(config)

# 4. 启动摄像头（开始硬件采集）
camera.start()

# 5. 捕获图像（从硬件读取数据）
image_array = camera.capture_array()
# 这一行代码实际上：
# - 触发摄像头传感器曝光
# - 从CSI接口读取原始数据
# - 通过GPU处理（如果需要）
# - 返回RGB图像数组

# 6. 停止摄像头
camera.stop()
```
## 🐛 常见问题排查

### 问题1: 摄像头无法检测

```bash
# 检查摄像头
libcamera-hello

# 检查连接
vcgencmd get_camera

# 如果 detected=0:
# 1. 检查排线连接（蓝色面朝向以太网口）
# 2. 确保排线完全插入
# 3. 尝试另一个CSI接口（树莓派5有两个）
# 4. 重启树莓派
```

### 问题2: 导入错误

```python
# 错误：ModuleNotFoundError: No module named 'picamera2'

# 解决：
sudo apt install -y python3-picamera2

# 如果还是不行，检查Python版本：
python3 --version  # 应该是 3.9 或更高
```

### 问题3: 权限错误

```bash
# 错误：Permission denied: '/dev/video0'

# 解决：添加用户到video组
sudo usermod -a -G video $USER

# 退出并重新登录
logout
```

### 问题4: 端口被占用

```bash
# 错误：Address already in use

# 查找占用端口的进程
sudo lsof -i :8443

# 杀死进程
sudo kill -9 <PID>

# 或者修改端口
# 编辑 server/camera_server.py:
SERVER_PORT = 9443  # 改成其他端口
```

### 问题5: 证书错误

```bash
# 错误：Certificate verify failed

# 解决：重新生成证书
rm -rf certs/*
python3 scripts/generate_certs.py
```

---

## 🌐 网络配置

### 获取树莓派IP地址

```bash
# 方法1: hostname命令
hostname -I

# 方法2: ip命令
ip addr show

# 方法3: 通过路由器查看
# 登录路由器管理界面，查看DHCP客户端列表
```

### 设置静态IP（推荐）

```bash
# 编辑dhcpcd配置
sudo nano /etc/dhcpcd.conf

# 在文件末尾添加（修改为你的网络参数）：
interface eth0  # 或 wlan0（WiFi）
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# 保存并重启网络
sudo systemctl restart dhcpcd
```

### 防火墙配置

```bash
# 如果启用了UFW防火墙
sudo ufw allow 8443/tcp
sudo ufw status
```

---

## 📱 移动设备访问

### 手机/平板访问

1. **确保设备在同一局域网**
   - 连接到与树莓派相同的WiFi

2. **打开浏览器**
   - 输入：`https://树莓派IP:8443`
   - 例如：`https://192.168.1.100:8443`

3. **信任证书**
   - iOS Safari：点击"继续"
   - Android Chrome：点击"高级" -> "继续访问"

4. **添加到主屏幕**（iOS）
   - 点击分享按钮
   - 选择"添加到主屏幕"
   - 像普通App一样使用

---

## 🔒 安全建议

### 生产环境部署

1. **修改默认密码**
```bash
passwd  # 修改pi用户密码
```

2. **禁用SSH密码登录**（使用密钥）
```bash
sudo nano /etc/ssh/sshd_config
# 设置: PasswordAuthentication no
sudo systemctl restart ssh
```

3. **添加用户认证**
   - 参考README中的认证实现

4. **使用正式证书**
   - 使用Let's Encrypt等CA签发的证书

5. **限制访问IP**
```python
# 在server/camera_server.py中添加：
@app.before_request
def limit_remote_addr():
    allowed_ips = ['192.168.1.0/24']  # 只允许局域网
    # 添加IP检查逻辑
```

---

## 📚 进一步学习

- [PiCamera2官方文档](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [树莓派摄像头指南](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [Flask部署指南](https://flask.palletsprojects.com/en/latest/deploying/)

---

## 💬 需要帮助？

如果遇到问题：
1. 检查上面的"常见问题排查"
2. 查看系统日志：`sudo journalctl -xe`
3. 查看服务日志：`sudo journalctl -u camera-server -f`
4. 提交Issue到项目仓库

---

