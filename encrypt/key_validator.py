import hashlib
import os

# To hash key (string = hashed password)
def key_validator(key, salt):
    if salt is None:
        salt = os.urandom(16)  # generate new salt on encryption
    new_key = hashlib.pbkdf2_hmac('sha256', key.encode(), salt, 100_000)
    #print(new_key)
    return new_key, salt
# To verify key (check key valid/not valid)
def verify_key(key, meta):
    salt = bytes.fromhex(meta["salt"])
    derived_key, _= key_validator(key, salt)
    return derived_key.hex() == meta["password_hash"], derived_key

def get_key_offset(salt_hex):
    numbers = ''.join(c for c in salt_hex if c.isdigit())[:4]
    offset = int(numbers)
    return max(64, offset)