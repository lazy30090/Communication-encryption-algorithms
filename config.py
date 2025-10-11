#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密智能摄像头 - 配置文件
所有可配置参数集中管理
"""

import os

# ==================== 服务器配置 ====================
class ServerConfig:
    """服务器相关配置"""
    
    # 监听地址（0.0.0.0表示监听所有网络接口）
    HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    
    # 监听端口（HTTPS默认443，开发环境常用8443）
    PORT = int(os.getenv('SERVER_PORT', 8443))
    
    # 调试模式（生产环境必须设为False）
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # 多线程模式
    THREADED = True


# ==================== 摄像头配置 ====================
class CameraConfig:
    """摄像头采集参数"""
    
    # 分辨率 (宽, 高)
    # 常用分辨率:
    #   - (640, 480)   VGA
    #   - (1280, 720)  HD 720p
    #   - (1920, 1080) Full HD 1080p
    RESOLUTION = (640, 480)
    
    # 帧率 (frames per second)
    # 注意：高帧率需要更多带宽和计算资源
    FRAMERATE = 30
    
    # JPEG质量 (1-100，越高质量越好，文件越大)
    JPEG_QUALITY = 85
    
    # 摄像头设备索引（用于OpenCV）
    DEVICE_INDEX = 0


# ==================== TLS/SSL配置 ====================
class TLSConfig:
    """TLS加密配置"""
    
    # 证书文件路径
    CERT_FILE = os.getenv('TLS_CERT', 'certs/server.crt')
    
    # 私钥文件路径
    KEY_FILE = os.getenv('TLS_KEY', 'certs/server.key')
    
    # 最小TLS版本（推荐TLS 1.2或更高）
    MIN_TLS_VERSION = 'TLSv1_2'  # 可选: TLSv1_2, TLSv1_3
    
    # 加密套件（使用强加密算法）
    CIPHER_SUITES = 'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS'


# ==================== 证书生成配置 ====================
class CertificateConfig:
    """证书生成参数"""
    
    # 证书信息
    COUNTRY = 'CN'                      # 国家代码
    STATE = 'Beijing'                   # 省份
    LOCALITY = 'Beijing'                # 城市
    ORGANIZATION = 'Security Team'      # 组织名称
    COMMON_NAME = 'localhost'           # 通用名称（域名）
    
    # 密钥长度（位）
    # 2048位是安全性和性能的平衡点
    KEY_SIZE = 2048
    
    # 证书有效期（天）
    VALIDITY_DAYS = 365
    
    # Subject Alternative Names (SAN)
    # 添加额外的域名或IP地址
    SAN_DNS = ['localhost', '*.local']
    SAN_IPS = ['127.0.0.1']  # 可以添加树莓派的局域网IP，如: ['127.0.0.1', '192.168.1.100']


# ==================== 日志配置 ====================
class LoggingConfig:
    """日志记录配置"""
    
    # 日志级别
    # DEBUG: 详细的调试信息
    # INFO: 一般信息
    # WARNING: 警告信息
    # ERROR: 错误信息
    # CRITICAL: 严重错误
    LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # 日志格式
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 日志输出到文件
    LOG_TO_FILE = False
    LOG_FILE = 'logs/camera_server.log'


# ==================== 性能配置 ====================
class PerformanceConfig:
    """性能优化参数"""
    
    # 最大客户端连接数
    MAX_CONNECTIONS = 10
    
    # 帧缓冲区大小
    FRAME_BUFFER_SIZE = 1
    
    # 网络超时（秒）
    NETWORK_TIMEOUT = 30


# ==================== 安全配置 ====================
class SecurityConfig:
    """安全相关配置"""
    
    # 是否启用访问控制
    ENABLE_AUTH = False
    
    # 访问令牌（如果启用认证）
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', '')
    
    # IP白名单（空列表表示允许所有）
    IP_WHITELIST = []  # 例如: ['192.168.1.0/24', '10.0.0.0/8']
    
    # 最大请求大小（MB）
    MAX_CONTENT_LENGTH = 16


# ==================== 配置验证 ====================
def validate_config():
    """验证配置参数的有效性"""
    errors = []
    
    # 检查端口范围
    if not (1 <= ServerConfig.PORT <= 65535):
        errors.append(f"无效的端口号: {ServerConfig.PORT}")
    
    # 检查分辨率
    if len(CameraConfig.RESOLUTION) != 2:
        errors.append("分辨率必须是 (宽, 高) 格式")
    
    # 检查帧率
    if not (1 <= CameraConfig.FRAMERATE <= 120):
        errors.append(f"帧率超出合理范围: {CameraConfig.FRAMERATE}")
    
    # 检查JPEG质量
    if not (1 <= CameraConfig.JPEG_QUALITY <= 100):
        errors.append(f"JPEG质量必须在1-100之间: {CameraConfig.JPEG_QUALITY}")
    
    # 检查证书文件（如果不在生成模式）
    if not os.path.exists(TLSConfig.CERT_FILE) and ServerConfig.DEBUG:
        errors.append(f"警告: 证书文件不存在: {TLSConfig.CERT_FILE}")
    
    if errors:
        return False, errors
    
    return True, []


# ==================== 配置信息打印 ====================
def print_config():
    """打印当前配置信息（用于调试）"""
    print("=" * 60)
    print("当前配置:")
    print("=" * 60)
    print(f"[服务器]")
    print(f"  地址: {ServerConfig.HOST}:{ServerConfig.PORT}")
    print(f"  调试: {ServerConfig.DEBUG}")
    print(f"\n[摄像头]")
    print(f"  分辨率: {CameraConfig.RESOLUTION[0]}×{CameraConfig.RESOLUTION[1]}")
    print(f"  帧率: {CameraConfig.FRAMERATE} FPS")
    print(f"  JPEG质量: {CameraConfig.JPEG_QUALITY}")
    print(f"\n[TLS]")
    print(f"  证书: {TLSConfig.CERT_FILE}")
    print(f"  私钥: {TLSConfig.KEY_FILE}")
    print(f"  最小版本: {TLSConfig.MIN_TLS_VERSION}")
    print(f"\n[日志]")
    print(f"  级别: {LoggingConfig.LEVEL}")
    print("=" * 60)


# ==================== 环境变量说明 ====================
"""
支持的环境变量：

SERVER_HOST       - 服务器监听地址（默认: 0.0.0.0）
SERVER_PORT       - 服务器端口（默认: 8443）
DEBUG             - 调试模式（默认: False）
TLS_CERT          - TLS证书路径（默认: certs/server.crt）
TLS_KEY           - TLS私钥路径（默认: certs/server.key）
LOG_LEVEL         - 日志级别（默认: INFO）
ACCESS_TOKEN      - 访问令牌（可选）

使用示例:
  export SERVER_PORT=443
  export DEBUG=true
  python server/camera_server.py
"""

if __name__ == '__main__':
    # 测试配置
    print_config()
    valid, errors = validate_config()
    
    if valid:
        print("\n✅ 配置验证通过")
    else:
        print("\n❌ 配置错误:")
        for error in errors:
            print(f"  - {error}")

