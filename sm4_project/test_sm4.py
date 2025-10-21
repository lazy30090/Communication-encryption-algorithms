"""SM4加密模块测试类
(仅测试CTR模式)
"""
import unittest
import os
import time
from SM4_Encryptor import SM4Encryptor, encrypt, decrypt

class TestSM4Encryptor(unittest.TestCase):
    """SM4加密器测试用例 (CTR模式)"""

    def setUp(self):
        """测试前准备"""
        self.key = b"0123456789abcdef"  # 16字节密钥
        self.iv = b"fedcba9876543210"   # 16字节IV

    def test_basic_string_encryption_ctr(self):
        """[测试1] CTR模式 - 基本字符串加密"""
        print("\n[测试1] CTR模式 - 基本字符串加密")
        plaintext = "Hello, SM4! 你好，国密算法！"

        encryptor = SM4Encryptor(self.key, iv=self.iv)
        encrypted = encryptor.encrypt_string(plaintext)
        decrypted = encryptor.decrypt_string(encrypted)

        print(f"明文: {plaintext}")
        print(f"密文 (hex): {encrypted.hex()[:60]}...")
        print(f"解密: {decrypted}")

        self.assertEqual(plaintext, decrypted, "CTR模式：解密后的文本应与原文一致")

    def test_binary_data_encryption_ctr(self):
        """[测试2] 二进制数据加密（模拟视频流）"""
        print("\n[测试2] 二进制数据加密 - CTR模式")
        # 模拟一段二进制视频数据
        binary_data = os.urandom(1024)  # 1KB随机数据

        # CTR模式
        encryptor_ctr = SM4Encryptor(self.key, iv=self.iv)
        encrypted_ctr = encryptor_ctr.encrypt(binary_data)
        decrypted_ctr = encryptor_ctr.decrypt(encrypted_ctr)

        print(f"原始数据长度: {len(binary_data)} bytes")
        print(f"CTR加密后长度: {len(encrypted_ctr)} bytes (无填充)")

        self.assertEqual(binary_data, decrypted_ctr, "CTR：解密后的数据应与原数据一致")
        self.assertEqual(len(binary_data), len(encrypted_ctr), "CTR模式不应改变数据长度")

    def test_ctr_no_padding(self):
        """[测试3] CTR模式 - 无填充特性"""
        print("\n[测试3] CTR模式 - 无填充特性")
        test_cases = [
            b"1",                    # 1字节
            b"1234567890",           # 10字节
            b"1234567890123456",     # 16字节
            b"12345678901234567",    # 17字节
        ]

        encryptor = SM4Encryptor(self.key, iv=self.iv)

        for data in test_cases:
            encrypted = encryptor.encrypt(data)
            decrypted = encryptor.decrypt(encrypted)

            print(f"原始: {len(data):2d}字节 -> 加密: {len(encrypted):2d}字节 -> "
                  f"验证: {'✓' if data == decrypted else '✗'}")

            # CTR模式加密后长度应该相同
            self.assertEqual(len(data), len(encrypted), "CTR模式不应改变数据长度")
            self.assertEqual(data, decrypted)

    def test_quick_functions(self):
        """[测试4] 快捷函数"""
        print("\n[测试4] 快捷函数 - CTR模式")
        plaintext = "Hello, pybind! This is much cleaner.".encode('utf-8')
        secret_key = b"0123456789abcdef"
        secret_iv = b"fedcba9876543210"

        print(f"明文: {plaintext.decode('utf-8')}")
        print(f"密钥: {secret_key.decode()}")
        print(f"IV: {secret_iv.decode()}")
        print("-" * 30)

        # 加密
        encrypted = encrypt(data=plaintext, key=secret_key, iv=secret_iv)
        print(f"加密 (hex): {encrypted.hex()}")

        # 解密
        decrypted_bytes = decrypt(data=encrypted, key=secret_key, iv=secret_iv)
        decrypted = decrypted_bytes.decode('utf-8')
        print(f"解密: {decrypted}")
        print("-" * 30)

        # 断言验证
        self.assertEqual(plaintext, decrypted_bytes, "快捷函数解密应正确")
        print("✓ 验证成功：明文与解密后的文本一致。")

    def test_large_data_performance(self):
        """[测试5] 大数据加密性能（10MB）"""
        print("\n[测试5] 大数据性能测试（10MB）- CTR模式")
        large_data = os.urandom(10 * 1024 * 1024)  # 10MB

        # CTR模式
        encryptor_ctr = SM4Encryptor(self.key, iv=self.iv)

        start = time.time()
        encrypted_ctr = encryptor_ctr.encrypt(large_data)
        ctr_encrypt_time = time.time() - start

        start = time.time()
        decrypted_ctr = encryptor_ctr.decrypt(encrypted_ctr)
        ctr_decrypt_time = time.time() - start

        print(f"  加密: {ctr_encrypt_time:.3f}秒 ({len(large_data)/(1024*1024)/ctr_encrypt_time:.2f} MB/s)")
        print(f"  解密: {ctr_decrypt_time:.3f}秒 ({len(large_data)/(1024*1024)/ctr_decrypt_time:.2f} MB/s)")

        self.assertEqual(large_data[:1000], decrypted_ctr[:1000], "CTR大数据验证")

    def test_different_iv_same_data(self):
        """[测试6] 相同数据 + 不同IV = 不同密文"""
        print("\n[测试6] 相同数据 + 不同IV = 不同密文")
        plaintext = b"Same data repeated!"

        iv1 = b"0000000000000001"
        iv2 = b"0000000000000002"

        enc1 = encrypt(plaintext, self.key, iv1)
        enc2 = encrypt(plaintext, self.key, iv2)

        print(f"明文: {plaintext}")
        print(f"IV1加密: {enc1.hex()[:40]}...")
        print(f"IV2加密: {enc2.hex()[:40]}...")
        print(f"密文不同: {'✓' if enc1 != enc2 else '✗'}")

        self.assertNotEqual(enc1, enc2, "不同IV应产生不同密文")

    def test_invalid_key(self):
        """[测试7] 非法密钥"""
        print("\n[测试7] 非法密钥测试")
        with self.assertRaises(ValueError):
            SM4Encryptor(b"short", iv=self.iv)  # 短密钥（5字节）
        print("✓ 正确拒绝了短密钥")

        # 修改长密钥，使其长度超过16字节（例如17字节）
        with self.assertRaises(ValueError):
            SM4Encryptor(b"this_is_too_long_123", iv=self.iv)  # 长度为19字节
        print("✓ 正确拒绝了长密钥")

    def test_invalid_iv(self):
        """[测试8] 非法IV"""
        print("\n[测试8] 非法IV测试")
        with self.assertRaises(ValueError):
            SM4Encryptor(self.key, iv=b"short")
        print("✓ 正确拒绝了短IV")

def run_interactive_test():
    """交互式测试"""
    print("=" * 60)
    print("SM4国密算法 - 交互式测试（CTR模式）")
    print("=" * 60)

    plaintext = "Hello, pybind! This is much cleaner."
    secret_key = b"0123456789abcdef"
    secret_iv = b"fedcba9876543210"

    print(f"明文: {plaintext}")
    print(f"密钥: {secret_key.decode()}")
    print(f"IV:   {secret_iv.decode()}")
    print("-" * 60)

    # 加密（CTR模式）
    encrypted = encrypt(data=plaintext.encode('utf-8'), key=secret_key, iv=secret_iv)
    print(f"加密 (hex): {encrypted.hex()}")

    # 解密
    decrypted_bytes = decrypt(data=encrypted, key=secret_key, iv=secret_iv)
    decrypted = decrypted_bytes.decode('utf-8')
    print(f"解密: {decrypted}")
    print("-" * 60)

    # 断言验证
    assert plaintext == decrypted
    print("✓ 验证成功：明文与解密后的文本一致。")

if __name__ == "__main__":
    # 先运行交互式测试
    run_interactive_test()

    print("\n" + "=" * 60)
    print("运行单元测试")
    print("=" * 60)

    # 运行单元测试
    # 修改了unittest.main()的调用方式，以便在IDLE或notebook中正常运行
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSM4Encryptor))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)