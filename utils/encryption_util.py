from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import json
import os
from utils.util import *

def encrypt_aes_ecb(key, plaintext):
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(plaintext.encode('utf-8'), AES.block_size))
    ciphertext = base64.b64encode(ciphertext).decode('utf-8')
    return ciphertext

def encrypt_aes_uuid(uuid, end_time, key=b'IMChenXHSkCkttpT', file_path: str = "key.db"):
    data = {}
    data["uuid"] = uuid
    data["end_time"] = concatenate_datetime_with_string(end_time)
    j = json.dumps(data)
    en_data = encrypt_aes_ecb(key, j)
    with open(file_path, 'wb') as f:  # 打开文件为二进制写模式
        f.write(en_data.encode('utf-8'))  # 将字符串转为字节对象并写入文件

def decrypt_aes_ecb(key, ciphertext):
    ciphertext = base64.b64decode(ciphertext)
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode('utf-8')

def decrypt_aes_uuid(key=b'IMChenXHSkCkttpT', file_path: str = "key.db"):
    if not os.path.exists(file_path):
        return  False,"key 不存在！"
    
    try:
        with open(file_path, 'rb') as file:  # 打开文件为二进制读模式
            ciphertext = file.read().decode('utf-8')  # 读取内容后将字节对象转为字符串
            data = decrypt_aes_ecb(key, ciphertext)
        j = json.loads(data)
        uuid = j["uuid"]
        end_time = j["end_time"]
        if not uuid or not end_time:
           return False,"key 错误"
        curdId = get_machine_code()
        if curdId != uuid:
           return False,"key 不对！"
        result = is_current_time_greater(end_time)
        if result:
            print("当前时间 > 输入时间")
            return False,"key 过期！"
        print("当前时间 < 输入时间")
        return True,"成功"
       
    
    except Exception  as ce:
        return False,"key 文件错误！"
