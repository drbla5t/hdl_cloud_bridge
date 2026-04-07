from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def get_secret(home_id: str) -> bytes:
    s = str(home_id)[::-1]
    if len(s) > 16:
        s = s[:16]
    else:
        s = s.ljust(16, "0")
    return s.encode("utf-8")


def decrypt_mqtt(payload: bytes, home_id: str) -> str:
    key = get_secret(home_id)
    iv = key
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(payload)
    return unpad(decrypted, AES.block_size).decode("utf-8", errors="ignore")