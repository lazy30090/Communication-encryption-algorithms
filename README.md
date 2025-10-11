# 🔒 加密智能摄像头系统

基于树莓派的加密视频流传输系统，采用 TLS 加密协议确保视频传输安全。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)

---

## 🎯 项目简介

通过树莓派摄像头采集视频，使用 MJPEG 格式流式传输，并通过 **TLS/SSL 加密**保证数据传输安全。

### 核心目标

- ✅ 实现基于 TLS 的加密视频传输
- ✅ 理解 HTTPS 和数字证书的工作原理
- ✅ 掌握网络服务的搭建和配置
- ✅ 学习流媒体传输技术（MJPEG）

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────┐
│      客户端（电脑/手机/平板）        │
│  ┌───────────────────────────────┐  │
│  │      Web浏览器访问            │  │
│  │   https://树莓派IP:8443       │  │
│  └───────────────────────────────┘  │
└──────────────▲──────────────────────┘
               │
               │  TLS 1.3 加密传输
               │  (HTTPS)
               │
┌──────────────┴──────────────────────┐
│       树莓派（服务器端）             │
│  ┌───────────────────────────────┐  │
│  │  1. 摄像头硬件模块             │  │
│  │     └─ CSI接口连接             │  │
│  │                                │  │
│  │  2. Python 服务器程序          │  │
│  │     ├─ PiCamera2 采集图像      │  │
│  │     ├─ Flask Web 框架          │  │
│  │     ├─ 生成 MJPEG 流           │  │
│  │     └─ TLS 加密层              │  │
│  │                                │  │
│  │  3. 数字证书                   │  │
│  │     ├─ 服务器证书 (.crt)       │  │
│  │     └─ 私钥 (.key)             │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### 数据流程

1. **图像采集**：摄像头 → JPEG 编码
2. **流式封装**：JPEG 帧 → MJPEG 流（multipart/x-mixed-replace）
3. **加密传输**：MJPEG 流 → TLS 加密 → HTTPS
4. **客户端接收**：浏览器/客户端 → TLS 解密 → 显示视频

---

## ✨ 技术特性

### 🔐 加密技术

| 特性 | 说明 |
|-----|------|
| **传输层加密** | TLS 1.2/1.3 协议 |
| **加密算法** | AES-256-GCM / ChaCha20-Poly1305 |
| **密钥交换** | ECDHE (椭圆曲线 Diffie-Hellman) |
| **完整性保护** | SHA-256 消息摘要 |
| **前向保密** | ✅ 支持 (PFS) |

### 📹 视频传输

- **格式**：MJPEG（Motion JPEG）
- **分辨率**：640×480（可配置）
- **帧率**：30 FPS（可配置）
- **编码质量**：JPEG 质量 85
- **传输协议**：HTTP/1.1 multipart/x-mixed-replace

### 🛠️ 技术栈

- **硬件平台**：树莓派 3B+ / 4B / 5
- **操作系统**：Raspberry Pi OS（Linux）
- **后端**：Python 3.7+ / Flask
- **摄像头**：PiCamera2（树莓派官方摄像头库）
- **加密**：Python cryptography 库
- **前端**：HTML5 + JavaScript（原生，无框架）

---

## 📚 网络服务搭建讲解

### 什么是网络服务？

**网络服务**是运行在服务器上的程序，通过网络（局域网或互联网）为客户端提供功能。在本项目中：

- **服务器端**（树莓派）：提供视频流数据
- **客户端**（电脑/手机）：请求并显示视频流

### 关键概念

#### 1️⃣ IP地址和端口

```
https://192.168.1.100:8443
  |      |           |
协议   IP地址        端口号
```

- **IP地址**：设备在网络中的唯一标识（类似门牌号）
- **端口**：同一设备上不同服务的编号（类似房间号）
  - HTTP：80端口（默认）
  - HTTPS：443端口（默认）
  - 本项目：8443端口（开发常用）

#### 2️⃣ HTTP vs HTTPS

| HTTP | HTTPS |
|------|-------|
| 明文传输 | **加密传输** |
| 易被窃听/篡改 | ✅ 防窃听、防篡改 |
| http:// | https:// |
| 80端口 | 443端口 |

**HTTPS = HTTP + TLS/SSL**

#### 3️⃣ TLS/SSL 工作流程

```
客户端                                  服务器
  │                                      │
  │─────── 1. ClientHello ───────────→  │  (请求连接)
  │                                      │
  │←────── 2. ServerHello ────────────  │  (发送证书)
  │          + 证书                      │
  │                                      │
  │─────── 3. 验证证书 ──────────────→  │  (验证身份)
  │                                      │
  │←────── 4. 协商密钥 ────────────→    │  (密钥交换)
  │                                      │
  │═══════ 5. 加密通信 ════════════→    │  (传输数据)
  │                                      │
```

#### 4️⃣ 数字证书

证书的作用：**证明服务器身份**（类似身份证）

- **CA证书**：由权威机构签发（浏览器信任）
- **自签名证书**：自己签发（本项目使用，需手动信任）

证书包含：
- 服务器公钥
- 服务器身份信息
- 有效期
- 签名

#### 5️⃣ MJPEG 流协议

MJPEG是一种简单的视频流格式：

```http
HTTP/1.1 200 OK
Content-Type: multipart/x-mixed-replace; boundary=frame

--frame
Content-Type: image/jpeg

[JPEG图像数据1]
--frame
Content-Type: image/jpeg

[JPEG图像数据2]
--frame
...
```

每一帧都是完整的JPEG图像，连续发送形成视频流。

### 本项目的网络架构

#### 服务器端启动流程

```python
1. 加载TLS证书 (server.crt + server.key)
   ↓
2. 创建SSL上下文（配置加密参数）
   ↓
3. 启动Flask Web服务器
   ↓
4. 监听 0.0.0.0:8443（接受所有网络接口）
   ↓
5. 等待客户端连接
```

#### 客户端访问流程

```python
1. 打开浏览器，输入 https://树莓派IP:8443
   ↓
2. 建立TLS连接（握手、验证证书）
   ↓
3. 浏览器显示主页
   ↓
4. 加载 /video_feed 接口（MJPEG流）
   ↓
5. 实时显示视频
```

---

## 🚀 快速开始

### 环境要求

- **硬件**：树莓派 3B+ / 4B / 5（推荐4B或5）
- **系统**：Raspberry Pi OS（64-bit 推荐）
- **Python**：3.7 或更高版本
- **摄像头**：树莓派官方摄像头模块 v2/v3
- **存储**：16GB以上 microSD卡
- **电源**：5V 3A（树莓派4/5）或 5V 2.5A（树莓派3）

> ⚠️ **重要提示**：本项目专门为树莓派硬件设计，代码必须在树莓派上运行。在普通电脑上开发时会出现导入错误，这是正常现象。详见 [HARDWARE_SETUP.md](HARDWARE_SETUP.md)。

### 1. 准备树莓派硬件

**完整硬件部署指南请查看：[HARDWARE_SETUP.md](HARDWARE_SETUP.md)**

```bash
# 1. 连接摄像头模块到树莓派的CSI接口
# 2. 启动树莓派
# 3. 测试摄像头
libcamera-hello
```

### 2. 克隆项目到树莓派

```bash
# SSH连接到树莓派
ssh pi@raspberrypi.local

# 创建项目目录
mkdir -p ~/projects
cd ~/projects

# 克隆或上传项目文件
git clone <repository_url> camera-project
cd camera-project
```

### 3. 安装依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装系统依赖（必需）
sudo apt install -y python3-pip python3-picamera2 python3-pil

# 安装Python依赖
pip3 install -r requirements.txt

# 验证安装
python3 -c "from picamera2 import Picamera2; print('安装成功')"
```

### 4. 生成TLS证书

```bash
# 在树莓派上运行
python3 scripts/generate_certs.py
```

输出示例：
```
✓ 创建目录: certs
✓ 私钥生成成功
✓ 证书生成成功
✓ 证书文件: /home/pi/projects/camera-project/certs/server.crt
✓ 私钥文件: /home/pi/projects/camera-project/certs/server.key
```

### 5. 启动服务器

```bash
# 在树莓派上启动
python3 server/camera_server.py
```

输出示例：
```
INFO - 初始化 PiCamera2 摄像头...
INFO - 摄像头配置完成 - 分辨率: 640x480
INFO - 摄像头已启动
INFO - 成功加载证书: certs/server.crt
INFO - SSL上下文配置完成
INFO - 启动HTTPS服务器 - https://0.0.0.0:8443
============================================================
服务器已启动！访问方式：
  - 本地访问：https://localhost:8443
  - 局域网访问：https://<树莓派IP>:8443
============================================================
```

### 6. 访问服务

#### 获取树莓派IP地址

```bash
# 在树莓派上运行
hostname -I
# 输出示例: 192.168.1.100
```

#### Web浏览器访问（推荐）

1. 在电脑/手机的浏览器中访问：`https://192.168.1.100:8443`
2. **首次访问**：点击"高级" → "继续访问"（信任自签名证书）
3. 查看实时加密视频流

#### 使用独立HTML客户端（可选）

1. 用浏览器打开 `client/browser_client.html`
2. 输入服务器地址：`https://192.168.1.100:8443`
3. 点击"连接"按钮

---

## 📖 使用说明

### 服务器端

#### 修改配置

编辑 `config.py` 文件：

```python
# 修改分辨率
CameraConfig.RESOLUTION = (1280, 720)  # HD

# 修改帧率
CameraConfig.FRAMERATE = 15  # 降低帧率节省带宽

# 修改端口
ServerConfig.PORT = 443  # 使用标准HTTPS端口（需root权限）
```

#### 查看服务器IP地址

```bash
# Linux/macOS
hostname -I

# Windows (PowerShell)
ipconfig | findstr IPv4
```

#### 开机自启动（树莓派）

创建systemd服务：

```bash
sudo nano /etc/systemd/system/camera-server.service
```

内容：
```ini
[Unit]
Description=Encrypted Camera Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Communication-encryption-algorithms
ExecStart=/usr/bin/python3 server/camera_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable camera-server
sudo systemctl start camera-server
```

### 客户端

#### HTML客户端功能

- ✅ 实时视频显示
- ✅ 连接状态监控
- ✅ 帧数统计
- ✅ 运行时间显示
- ✅ 响应式设计（支持手机）
