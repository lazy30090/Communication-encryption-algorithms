"""
SM4国密算法封装模块

支持字节流加密，适用于视频流等二进制数据加密
CTR模式的优点：
- 无需填充，数据长度不变
- 加解密操作相同
- 支持并行处理和随机访问（本实现是无状态的）
"""
from gmssl import sm4
from typing import Union
import struct


class SM4Encryptor:
    """SM4加密器 - 仅支持CTR模式"""

    def __init__(self, key: bytes, iv: bytes):
        """
        初始化SM4加密器（CTR模式）

        Args:
            key: 16字节密钥（128位）
            iv: 16字节初始化向量（Nonce）
                 - 建议每次加密使用不同的IV

        Raises:
            ValueError: 密钥或IV长度不正确
        """

        if len(key) != 16:
            raise ValueError(f"SM4密钥必须是16字节(128位)，但提供了 {len(key)} 字节")

        if len(iv) != 16:
            raise ValueError(f"IV必须是16字节，但提供了 {len(iv)} 字节")

        self.key = key
        self.iv = iv
        self.cipher = sm4.CryptSM4()

    def _ctr_encrypt_decrypt(self, data: bytes) -> bytes:
        """
        CTR模式加密/解密（加密和解密使用相同的操作）

        CTR模式工作原理：
        1. 将IV作为初始计数器
        2. 加密计数器得到密钥流
        3. 密钥流与明文XOR得到密文

        Args:
            data: 明文或密文

        Returns:
            密文或明文
        """
        # 将IV转换为计数器（大端序整数）
        counter = int.from_bytes(self.iv, byteorder='big')

        result = bytearray()
        # 注意：CTR模式总是使用ENCRYPT模式的ECB来生成密钥流
        self.cipher.set_key(self.key, sm4.SM4_ENCRYPT)

        # 分块处理（每块16字节）
        for i in range(0, len(data), 16):
            # 获取当前块
            block = data[i:i+16]

            # 生成计数器块（16字节）
            counter_block = counter.to_bytes(16, byteorder='big')

            # 加密计数器块得到密钥流
            keystream = self.cipher.crypt_ecb(counter_block)

            # 密钥流与数据块XOR
            # zip会停在较短的那个操作数上
            # (如果最后一块数据不足16字节)
            encrypted_block = bytes(a ^ b for a, b in zip(block, keystream))
            result.extend(encrypted_block)

            # 计数器递增
            counter = (counter + 1) & ((1 << 128) - 1) # 防止溢出

        return bytes(result)

    def encrypt(self, data: bytes) -> bytes:
        """
        加密数据（字节流）

        Args:
            data: 明文字节流

        Returns:
            密文字节流
        """
        return self._ctr_encrypt_decrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        """
        解密数据（字节流）

        Args:
            data: 密文字节流

        Returns:
            明文字节流
        """
        return self._ctr_encrypt_decrypt(data)

    def encrypt_string(self, text: str, encoding: str = 'utf-8') -> bytes:
        """
        加密字符串（便捷方法）

        Args:
            text: 明文字符串
            encoding: 字符编码

        Returns:
            密文字节流
        """
        return self.encrypt(text.encode(encoding))

    def decrypt_string(self, data: bytes, encoding: str = 'utf-8') -> str:
        """
        解密为字符串（便捷方法）

        Args:
            data: 密文字节流
            encoding: 字符编码

        Returns:
            明文字符串
        """
        return self.decrypt(data).decode(encoding)


# --- 便捷函数 ---

def encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    """
    快捷加密函数（CTR模式）

    Args:
        data: 明文字节流
        key: 16字节密钥
        iv: 初始化向量（16字节）

    Returns:
        密文字节流
    """
    if iv is None:
        raise ValueError("必须提供16字节的IV")
    encryptor = SM4Encryptor(key, iv)
    return encryptor.encrypt(data)


def decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    """
    快捷解密函数（CTR模式）

    Args:
        data: 密文字节流
        key: 16字节密钥
        iv: 初始化向量（16字节）

    Returns:
        明文字节流
    """
    if iv is None:
        raise ValueError("必须提供16字节的IV")
    encryptor = SM4Encryptor(key, iv)
    return encryptor.decrypt(data)


if __name__ == "__main__":
    # 简单测试
    key = b"0123456789abcdef"
    iv = b"fedcba9876543210"
    plaintext = b"Hello, SM4! This is a test."

    print("=== CTR模式测试 ===")
    encrypted_ctr = encrypt(plaintext, key, iv)
    print(f"密文 (hex): {encrypted_ctr.hex()}")

    decrypted_ctr = decrypt(encrypted_ctr, key, iv)
    print(f"解密: {decrypted_ctr}")
    print(f"验证: {'✓ 成功' if plaintext == decrypted_ctr else '✗ 失败'}")

    print("\n=== CTR模式优势：无需填充 ===")
    test_data = b"1234567890"  # 10字节
    enc_ctr = encrypt(test_data, key, iv)
    print(f"原始数据: {len(test_data)} 字节")
    print(f"CTR加密后: {len(enc_ctr)} 字节 ")