#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密智能摄像头服务器端 - 树莓派版本
功能：采集摄像头图像，生成MJPEG流，通过TLS加密传输
"""

import io
import ssl
import time
import logging
import threading
from flask import Flask, Response
from datetime import datetime
from picamera2 import Picamera2
from PIL import Image

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== 配置参数 ====================
# 服务器配置
SERVER_HOST = '0.0.0.0'  # 监听所有网络接口
SERVER_PORT = 8443       # HTTPS默认端口（8443用于开发）
CAMERA_RESOLUTION = (640, 480)  # 摄像头分辨率
CAMERA_FRAMERATE = 30    # 帧率
JPEG_QUALITY = 85        # JPEG质量（1-100）

# TLS证书路径
CERT_FILE = 'certs/server.crt'  # 服务器证书
KEY_FILE = 'certs/server.key'   # 私钥文件

# ==================== 摄像头类 ====================
class Camera:
    """
    树莓派摄像头管理类
    负责图像采集和帧缓存
    """
    def __init__(self):
        self.frame = None  # 当前帧
        self.lock = threading.Lock()  # 线程锁，确保线程安全
        self.is_running = False
        self.capture_thread = None
        
        # 初始化树莓派摄像头
        logger.info("初始化 PiCamera2 摄像头...")
        self.camera = Picamera2()
        
        # 配置摄像头
        config = self.camera.create_still_configuration(
            main={"size": CAMERA_RESOLUTION}
        )
        self.camera.configure(config)
        logger.info(f"摄像头配置完成 - 分辨率: {CAMERA_RESOLUTION[0]}x{CAMERA_RESOLUTION[1]}")
    
    def start(self):
        """启动摄像头采集线程"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 启动树莓派摄像头
        self.camera.start()
        logger.info("摄像头已启动")
        
        # 启动采集线程
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        logger.info("摄像头采集线程已启动")
    
    def stop(self):
        """停止摄像头采集"""
        self.is_running = False
        
        # 等待采集线程结束
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        
        # 停止摄像头
        try:
            self.camera.stop()
            logger.info("摄像头已停止")
        except Exception as e:
            logger.error(f"停止摄像头时出错: {e}")
    
    def _capture_loop(self):
        """摄像头采集循环（在独立线程中运行）"""
        while self.is_running:
            try:
                frame_data = self._capture_frame()
                if frame_data:
                    with self.lock:
                        self.frame = frame_data
                time.sleep(1.0 / CAMERA_FRAMERATE)  # 控制帧率
            except Exception as e:
                logger.error(f"采集帧错误: {e}")
                time.sleep(0.5)
    
    def _capture_frame(self):
        """
        采集单帧图像并转换为JPEG格式
        返回：JPEG格式的字节数据
        """
        try:
            # 捕获图像数组
            image_array = self.camera.capture_array()
            
            # 转换为PIL Image
            image = Image.fromarray(image_array)
            
            # 转换为JPEG
            stream = io.BytesIO()
            image.save(stream, format='JPEG', quality=JPEG_QUALITY)
            return stream.getvalue()
                
        except Exception as e:
            logger.error(f"捕获帧失败: {e}")
            return None
    
    def get_frame(self):
        """获取当前帧（线程安全）"""
        with self.lock:
            return self.frame

# ==================== Flask Web 应用 ====================
app = Flask(__name__)
camera = Camera()

def generate_mjpeg_stream():
    """
    生成MJPEG流
    MJPEG格式：连续的JPEG图像，使用multipart/x-mixed-replace边界分隔
    """
    while True:
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue
        
        # MJPEG格式：每帧前面加HTTP multipart头
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """主页 - 显示视频流"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>加密智能摄像头</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                padding: 30px;
                max-width: 800px;
                width: 100%;
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 10px;
            }
            .info {
                text-align: center;
                color: #666;
                margin-bottom: 20px;
                font-size: 14px;
            }
            .status {
                background: #e8f5e9;
                border-left: 4px solid #4caf50;
                padding: 10px;
                margin-bottom: 20px;
                border-radius: 4px;
            }
            .status-dot {
                display: inline-block;
                width: 10px;
                height: 10px;
                background: #4caf50;
                border-radius: 50%;
                margin-right: 8px;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .video-container {
                position: relative;
                width: 100%;
                background: #000;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            }
            img {
                width: 100%;
                height: auto;
                display: block;
            }
            .encryption-badge {
                position: absolute;
                top: 10px;
                right: 10px;
                background: rgba(76, 175, 80, 0.9);
                color: white;
                padding: 8px 15px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                display: flex;
                align-items: center;
            }
            .lock-icon {
                margin-right: 5px;
            }
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .info-card {
                background: #f5f5f5;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }
            .info-card h3 {
                margin: 0 0 5px 0;
                color: #667eea;
                font-size: 14px;
            }
            .info-card p {
                margin: 0;
                color: #333;
                font-size: 18px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔒 加密智能摄像头系统</h1>
            <div class="info">基于 TLS 1.3 加密传输 | MJPEG 流式传输</div>
            
            <div class="status">
                <span class="status-dot"></span>
                <strong>连接状态：</strong>安全连接已建立（HTTPS）
            </div>
            
            <div class="video-container">
                <img src="/video_feed" alt="视频流">
                <div class="encryption-badge">
                    <span class="lock-icon">🔒</span>
                    TLS 加密
                </div>
            </div>
            
            <div class="info-grid">
                <div class="info-card">
                    <h3>分辨率</h3>
                    <p>640×480</p>
                </div>
                <div class="info-card">
                    <h3>帧率</h3>
                    <p>30 FPS</p>
                </div>
                <div class="info-card">
                    <h3>加密协议</h3>
                    <p>TLS 1.3</p>
                </div>
            </div>
        </div>
        
        <script>
            // 显示实时时间
            setInterval(() => {
                console.log('Stream active:', new Date().toLocaleTimeString());
            }, 5000);
        </script>
    </body>
    </html>
    """
    return html

@app.route('/video_feed')
def video_feed():
    """视频流端点 - 返回MJPEG流"""
    return Response(
        generate_mjpeg_stream(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/status')
def status():
    """状态接口 - 返回服务器状态信息"""
    return {
        'status': 'running',
        'camera_type': 'PiCamera2',
        'resolution': CAMERA_RESOLUTION,
        'framerate': CAMERA_FRAMERATE,
        'jpeg_quality': JPEG_QUALITY,
        'encryption': 'TLS',
        'timestamp': datetime.now().isoformat()
    }

# ==================== 主程序 ====================
def create_ssl_context():
    """
    创建SSL上下文
    配置TLS加密参数
    """
    # 创建SSL上下文，使用TLS协议
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    # 加载证书和私钥
    try:
        context.load_cert_chain(CERT_FILE, KEY_FILE)
        logger.info(f"成功加载证书: {CERT_FILE}")
    except FileNotFoundError:
        logger.error("证书文件不存在！请先运行 generate_certs.py 生成证书")
        raise
    
    # 配置TLS版本（只允许TLS 1.2及以上，更安全）
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    
    # 配置加密套件（使用强加密算法）
    context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
    
    logger.info("SSL上下文配置完成")
    return context

def main():
    """主函数"""
    try:
        # 启动摄像头
        logger.info("启动摄像头...")
        camera.start()
        
        # 创建SSL上下文
        logger.info("配置TLS加密...")
        ssl_context = create_ssl_context()
        
        # 启动Flask服务器
        logger.info(f"启动HTTPS服务器 - https://{SERVER_HOST}:{SERVER_PORT}")
        logger.info("=" * 60)
        logger.info("服务器已启动！访问方式：")
        logger.info(f"  - 本地访问：https://localhost:{SERVER_PORT}")
        logger.info(f"  - 局域网访问：https://<树莓派IP>:{SERVER_PORT}")
        logger.info("注意：首次访问时浏览器会提示证书不受信任，这是正常的（自签名证书）")
        logger.info("=" * 60)
        
        # 运行Flask应用（使用SSL）
        app.run(
            host=SERVER_HOST,
            port=SERVER_PORT,
            ssl_context=ssl_context,
            threaded=True,  # 多线程处理请求
            debug=False     # 生产环境关闭调试模式
        )
        
    except KeyboardInterrupt:
        logger.info("\n正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器错误: {e}", exc_info=True)
    finally:
        camera.stop()
        logger.info("服务器已关闭")

if __name__ == '__main__':
    main()

