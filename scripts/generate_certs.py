# 这个脚本实现了完整的自签名SSL/TLS证书生成功能：
# 核心功能：

# 生成2048位RSA私钥
# 创建自签名X.509证书
# 配置证书信息（国家、组织、域名等）
# 添加SAN（Subject Alternative Name）扩展
# 设置365天有效期
# 以PEM格式保存证书和私钥

# 安全特性：
# 私钥文件权限设置为600（仅所有者可读写）
# 支持localhost和127.0.0.1访问
# 包含基本约束和密钥用途扩展
# 使用SHA256签名算法


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TLS证书生成脚本
自动生成自签名SSL/TLS证书，用于HTTPS加密通信
"""

import os
import sys
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# 证书输出目录
CERT_DIR = "certs"
CERT_FILE = os.path.join(CERT_DIR, "server.crt")
KEY_FILE = os.path.join(CERT_DIR, "server.key")

# 证书配置
CERT_CONFIG = {
    'country': 'CN',              # 国家代码
    'state': 'Beijing',           # 省份
    'locality': 'Beijing',        # 城市
    'organization': 'Security Team',  # 组织名称
    'common_name': 'localhost',   # 通用名称（域名或IP）
    'validity_days': 365,         # 有效期（天）
    'key_size': 2048,             # RSA密钥长度（位）
}

def create_cert_directory():
    """创建证书目录"""
    if not os.path.exists(CERT_DIR):
        os.makedirs(CERT_DIR)
        print(f"✓ 创建目录: {CERT_DIR}")
    else:
        print(f"✓ 目录已存在: {CERT_DIR}")

def generate_private_key():
    """
    生成RSA私钥
    使用2048位密钥长度（安全性和性能的平衡）
    """
    print(f"\n[1/4] 生成 RSA 私钥 ({CERT_CONFIG['key_size']} 位)...")
    
    private_key = rsa.generate_private_key(
        public_exponent=65537,  # 标准公钥指数
        key_size=CERT_CONFIG['key_size'],
        backend=default_backend()
    )
    
    print("✓ 私钥生成成功")
    return private_key

def generate_certificate(private_key):
    """
    生成自签名X.509证书
    
    参数:
        private_key: RSA私钥对象
    
    返回:
        证书对象
    """
    print("\n[2/4] 生成自签名证书...")
    
    # 证书主体信息
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, CERT_CONFIG['country']),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, CERT_CONFIG['state']),
        x509.NameAttribute(NameOID.LOCALITY_NAME, CERT_CONFIG['locality']),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, CERT_CONFIG['organization']),
        x509.NameAttribute(NameOID.COMMON_NAME, CERT_CONFIG['common_name']),
    ])
    
    # 构建证书
    cert_builder = x509.CertificateBuilder()
    
    # 设置主体和颁发者（自签名，所以相同）
    cert_builder = cert_builder.subject_name(subject)
    cert_builder = cert_builder.issuer_name(issuer)
    
    # 设置公钥
    cert_builder = cert_builder.public_key(private_key.public_key())
    
    # 设置序列号（随机）
    cert_builder = cert_builder.serial_number(x509.random_serial_number())
    
    # 设置有效期
    not_valid_before = datetime.utcnow()
    not_valid_after = not_valid_before + timedelta(days=CERT_CONFIG['validity_days'])
    cert_builder = cert_builder.not_valid_before(not_valid_before)
    cert_builder = cert_builder.not_valid_after(not_valid_after)
    
    # 添加扩展 - Subject Alternative Name (SAN)
    # 这很重要！现代浏览器要求证书包含SAN
    san_list = [
        x509.DNSName('localhost'),
        x509.DNSName('*.local'),
        x509.IPAddress(b'\x7f\x00\x00\x01'),  # 127.0.0.1
    ]
    
    # 可选：添加树莓派的局域网IP（需要手动修改）
    # san_list.append(x509.IPAddress(b'\xc0\xa8\x01\x64'))  # 192.168.1.100
    
    cert_builder = cert_builder.add_extension(
        x509.SubjectAlternativeName(san_list),
        critical=False,
    )
    
    # 添加基本约束（标识为CA证书）
    cert_builder = cert_builder.add_extension(
        x509.BasicConstraints(ca=True, path_length=0),
        critical=True,
    )
    
    # 添加密钥用途
    cert_builder = cert_builder.add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            key_cert_sign=True,
            crl_sign=False,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    )
    
    # 使用私钥签名证书（SHA256算法）
    certificate = cert_builder.sign(
        private_key=private_key,
        algorithm=hashes.SHA256(),
        backend=default_backend()
    )
    
    print("✓ 证书生成成功")
    print(f"  - 有效期: {CERT_CONFIG['validity_days']} 天")
    print(f"  - 开始日期: {not_valid_before.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"  - 结束日期: {not_valid_after.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    return certificate

def save_private_key(private_key, filename):
    """
    保存私钥到文件
    使用PEM格式，不加密（用于服务器自动启动）
    """
    print(f"\n[3/4] 保存私钥到文件: {filename}")
    
    with open(filename, 'wb') as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()  # 不加密
                # 生产环境可以使用密码加密：
                # encryption_algorithm=serialization.BestAvailableEncryption(b'password')
            )
        )
    
    # 设置文件权限（仅所有者可读写）
    os.chmod(filename, 0o600)
    print("✓ 私钥保存成功")
    print("  ⚠️  警告：私钥文件未加密，请妥善保管！")

def save_certificate(certificate, filename):
    """
    保存证书到文件
    使用PEM格式
    """
    print(f"\n[4/4] 保存证书到文件: {filename}")
    
    with open(filename, 'wb') as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))
    
    print("✓ 证书保存成功")

def display_certificate_info(certificate):
    """显示证书详细信息"""
    print("\n" + "=" * 60)
    print("证书信息：")
    print("=" * 60)
    
    # 主体信息
    subject = certificate.subject
    print(f"主体 (Subject):")
    for attr in subject:
        print(f"  - {attr.oid._name}: {attr.value}")
    
    # 序列号
    print(f"\n序列号: {certificate.serial_number}")
    
    # 有效期
    print(f"\n有效期:")
    print(f"  - 开始: {certificate.not_valid_before_utc}")
    print(f"  - 结束: {certificate.not_valid_after_utc}")
    
    # 签名算法
    print(f"\n签名算法: {certificate.signature_algorithm_oid._name}")
    
    # SAN扩展
    try:
        san = certificate.extensions.get_extension_for_oid(
            ExtensionOID.SUBJECT_ALTERNATIVE_NAME
        )
        print(f"\n备用名称 (SAN):")
        for name in san.value:
            print(f"  - {name}")
    except x509.ExtensionNotFound:
        pass
    
    print("=" * 60)

def check_existing_certs():
    """检查是否已存在证书"""
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        print("\n⚠️  警告：证书文件已存在！")
        print(f"  - {CERT_FILE}")
        print(f"  - {KEY_FILE}")
        
        response = input("\n是否覆盖现有证书？(y/N): ").strip().lower()
        if response != 'y':
            print("操作已取消")
            sys.exit(0)
        print()

def main():
    """主函数"""
    print("=" * 60)
    print("TLS/SSL 证书生成工具")
    print("用途：为加密智能摄像头项目生成自签名证书")
    print("=" * 60)
    
    try:
        # 检查现有证书
        check_existing_certs()
        
        # 创建证书目录
        create_cert_directory()
        
        # 生成私钥
        private_key = generate_private_key()
        
        # 生成证书
        certificate = generate_certificate(private_key)
        
        # 保存私钥
        save_private_key(private_key, KEY_FILE)
        
        # 保存证书
        save_certificate(certificate, CERT_FILE)
        
        # 显示证书信息
        display_certificate_info(certificate)
        
        # 成功提示
        print("\n✅ 证书生成完成！")
        print("\n使用说明：")
        print("1. 服务器端会自动使用这些证书")
        print("2. 客户端首次访问时，浏览器会提示\"不安全\"（自签名证书）")
        print("3. 点击\"高级\" -> \"继续访问\"即可")
        print("4. 生产环境建议使用由CA签发的正式证书")
        print("\n文件位置：")
        print(f"  - 证书: {os.path.abspath(CERT_FILE)}")
        print(f"  - 私钥: {os.path.abspath(KEY_FILE)}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

