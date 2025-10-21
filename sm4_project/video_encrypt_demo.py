"""
SM4-CTR 实时视频流加密最终演示

这个文件模拟了两个角色：
1.  Server (服务器/发送方): 模拟树莓派摄像头，捕获视频帧并使用CTR模式加密后通过网络发送。
2.  Client (客户端/接收方): 模拟接收电脑，接收加密数据并解密以供播放。

演示了CTR模式在流式加密中的核心要点：
-   服务器为每个会话生成一个【随机】的 IV (初始化向量)。
-   服务器【必须】先把这个IV无加密地发送给客户端。
-   客户端首先接收IV，然后双方使用相同的 密钥(Key) 和 IV 进行加解密。

运行方式 (需要打开两个终端):
1.  在第一个终端运行服务器: python video_encrypt_demo.py server
2.  在第二个终端运行客户端: python video_encrypt_demo.py client
"""

import socket
import time
import os
import sys
from SM4_Encryptor import SM4Encryptor

# --- 配置 ---
# 密钥必须是16字节，且服务器和客户端必须完全一致
SECRET_KEY = b'0123456789abcdef'
HOST = '127.0.0.1'       # 本机IP地址。实际部署时，服务器端应设为树莓派的IP
PORT = 12345             # 任意未被占用的端口号
# ----------------

def recv_all(sock, n):
    """一个辅助函数，确保从socket中接收到n个字节的数据"""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def run_server():
    """
    运行服务器 (模拟树莓派发送方)
    """
    print("--- 启动SM4-CTR加密服务器 ---")
    print(f"监听地址: {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()

        with conn:
            print(f"[服务器] 客户端 {addr} 已连接。")

            # 1. 【核心】生成随机IV并发送
            # 每次连接都必须使用新的随机IV
            iv = os.urandom(16)
            print(f"[服务器] 为本次会话生成随机IV: {iv.hex()}")
            conn.sendall(iv)
            print("[服务器] IV已发送至客户端。")

            # 2. 初始化加密器
            encryptor = SM4Encryptor(key=SECRET_KEY, iv=iv)

            print("[服务器] 开始模拟视频流并加密发送...")

            # 模拟发送200帧视频数据
            for i in range(1, 201):
                # 模拟一帧大小不一的视频数据
                # 实际应用中，这里会是 camera.read() 得到的真实数据
                frame_data = f"这是第 {i} 帧视频数据: ".encode('utf-8') + os.urandom(50 * 1024) # 约50KB

                # 3. 加密数据帧
                encrypted_frame = encryptor.encrypt(frame_data)

                # 4. 发送数据帧 (使用简单的 长度-数据 协议)
                #   a. 发送4字节的帧长度
                frame_len_bytes = len(encrypted_frame).to_bytes(4, 'big')
                conn.sendall(frame_len_bytes)
                #   b. 发送加密后的帧数据
                conn.sendall(encrypted_frame)

                if i % 20 == 0:
                    print(f"[服务器] 已加密并发送 {i}/200 帧...")

                time.sleep(1/30) # 模拟30 FPS的帧率

            print("[服务器] 视频流发送完毕。")

def run_client():
    """
    运行客户端 (模拟PC接收方)
    """
    print("--- 启动SM4-CTR解密客户端 ---")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"连接到服务器 {HOST}:{PORT}...")
            s.connect((HOST, PORT))
            print("[客户端] 已成功连接到服务器。")

            # 1. 【核心】接收16字节的IV
            iv = recv_all(s, 16)
            if not iv:
                print("[客户端] 错误：未能从服务器接收到IV。")
                return
            print(f"[客户端] 成功收到会话IV: {iv.hex()}")

            # 2. 初始化解密器 (使用收到的IV)
            decryptor = SM4Encryptor(key=SECRET_KEY, iv=iv)

            print("[客户端] 准备接收和解密视频流...")

            frame_count = 0
            while True:
                # 3. 接收数据帧
                #   a. 接收4字节的长度信息
                len_data = recv_all(s, 4)
                if not len_data:
                    break # 服务器关闭了连接

                frame_len = int.from_bytes(len_data, 'big')

                #   b. 根据长度接收完整的加密帧数据
                encrypted_frame = recv_all(s, frame_len)
                if not encrypted_frame:
                    break

                # 4. 解密数据帧
                decrypted_frame = decryptor.decrypt(encrypted_frame)

                frame_count += 1
                if frame_count % 20 == 0:
                    print(f"[客户端] 成功解密第 {frame_count} 帧 (大小: {len(decrypted_frame)/1024:.1f} KB)")
                    # 打印解密后内容的前50个字节以验证
                    print(f"    内容预览: {decrypted_frame[:50]}...")

            print(f"\n[客户端] 视频流结束。共成功接收并解密 {frame_count} 帧。")

    except ConnectionRefusedError:
        print("[客户端] 错误：连接被拒绝。请确保服务器端已运行。")
    except Exception as e:
        print(f"[客户端] 发生未知错误: {e}")
    finally:
        print("[客户端] 关闭连接。")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ['server', 'client']:
        print("用法: python video_encrypt_demo.py [server|client]")
        print("请打开两个终端：")
        print("  终端1: python video_encrypt_demo.py server")
        print("  终端2: python video_encrypt_demo.py client")
        sys.exit(1)

    if len(SECRET_KEY) != 16:
        print(f"错误: 密钥(SECRET_KEY)长度必须为16字节，当前为 {len(SECRET_KEY)} 字节。")
        sys.exit(1)

    if sys.argv[1] == 'server':
        run_server()
    elif sys.argv[1] == 'client':
        run_client()