import json
import time
import hashlib
import os

from encrypt.get_trusted_time import get_trusted_time

def create_meta(file_path, encrypted_file_path, key, salt, duration_minutes, encryption_algorithm):

    key_hash = hashlib.pbkdf2_hmac('sha256', key.encode(), salt, 100_000).hex()

    meta = {
        "original_name": file_path,
        "original_size": os.path.getsize(encrypted_file_path),
        "encrypted_at": get_trusted_time(),
        "unlock_at": get_trusted_time() + (duration_minutes * 60) if duration_minutes else None,
        "salt": salt.hex(),
        "password_hash": key_hash,
        "algorithm": encryption_algorithm
    }

    meta_path = encrypted_file_path + ".meta"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent = 4)

    return meta_path