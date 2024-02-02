#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2024/2/2 S{TIME} 
# @Name crypt. Py
# @Author：jialtang

import base64

KEY = 987654321


def encrypt_integer(num, key):
    # 将整数转换为字节
    num_bytes = num.to_bytes((num.bit_length() + 7) // 8, 'big')
    # 将密钥转换为字节
    key_bytes = key.to_bytes((key.bit_length() + 7) // 8, 'big')
    # 使用XOR加密
    encrypted_bytes = bytes(a ^ b for a, b in zip(num_bytes, key_bytes * (len(num_bytes) // len(key_bytes) + 1)))
    # 将加密后的字节转换为Base64编码的字符串
    encrypted_str = base64.b64encode(encrypted_bytes).decode('utf-8')
    return encrypted_str


def decrypt_string(encrypted_str, key):
    # 将Base64编码的字符串转换回加密的字节
    encrypted_bytes = base64.b64decode(encrypted_str)
    # 将密钥转换为字节
    key_bytes = key.to_bytes((key.bit_length() + 7) // 8, 'big')
    # 使用XOR解密
    decrypted_bytes = bytes(
        a ^ b for a, b in zip(encrypted_bytes, key_bytes * (len(encrypted_bytes) // len(key_bytes) + 1)))
    # 将字节转换为整数
    original_num = int.from_bytes(decrypted_bytes, 'big')
    return original_num


if __name__ == '__main__':
    # 测试
    original_num = 123456789123
    encrypted_str = encrypt_integer(original_num, key)
    print(f"Encrypted: {encrypted_str}")

    decrypted_num = decrypt_string(encrypted_str, key)
    print(f"Decrypted: {decrypted_num}")
