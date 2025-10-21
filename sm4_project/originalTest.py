# 适配SM4加密项目的测试代码（与队友测试逻辑一致，便于对接）
from SM4_Encryptor import SM4Encryptor  # 导入你的核心类
import os

# 1. 定义测试数据（与队友保持一致）
plaintext = "Hello，pybind11! This Is much cleaner."  # 待加密明文
secret_key = b"0123456789abcdef"  # 16字节密钥（符合SM4要求）

# 2. 生成随机IV（SM4-CTR模式必需，每次测试生成新的）
iv = os.urandom(16)  # 16字节随机初始化向量

# 3. 打印原始信息（便于硬件模块调试）
print(f"明文: {plaintext}")
print(f"明文 bytes: {plaintext.encode('utf-8')}")
print(f"密钥: {secret_key.decode('utf-8')}")  # 密钥字符串形式
print(f"IV (16字节): {iv.hex()}")  # IV以十六进制展示（硬件可能更易处理）

# 4. 初始化加密器并加密
encryptor = SM4Encryptor(key=secret_key, iv=iv)
encrypted_bytes = encryptor.encrypt(data=plaintext.encode('utf-8'))  # 加密字节流

# 5. 打印加密结果
print(f"加密后 bytes: {encrypted_bytes}")
print(f"加密后 (hex): {encrypted_bytes.hex()}")  # 十六进制格式（便于传输展示）

# 6. 解密（使用相同密钥和IV）
decryptor = SM4Encryptor(key=secret_key, iv=iv)  # 解密需相同IV
decrypted_bytes = decryptor.decrypt(data=encrypted_bytes)
decrypted = decrypted_bytes.decode("utf-8")  # 转换为字符串

# 7. 打印解密结果并验证
print(f"解密后: {decrypted}")
assert decrypted == plaintext, "SM4解密结果与明文不一致！"
print("SM4测试通过：解密结果正确，与明文一致")