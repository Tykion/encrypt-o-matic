import os
from encrypt.modified.twofish import Twofish
from Crypto.Cipher import AES, ChaCha20
from Crypto.Util.Padding import pad
from encrypt.inflate_size import *
from encrypt.meta import *
from encrypt.key_validator import *
from encrypt.create_package import *
from encrypt.custom_op import *

# AES
def encrypt_file_AES(key, file_path, size_mb, duration, x):
    derived_key, salt = key_validator(key, None)

    custom_operation(x)

    if not os.path.exists(file_path):
        raise FileNotFoundError("File not found")
    
    validate_file(file_path)
    
    if len(derived_key) != 32:
        raise ValueError("Key length should be 32 bytes (256 bits)")
    
    # Will save a new file with .encrypted at the end
    encrypted_file_path = file_path + ".encryptedAES"

    # Open file with binary format because AES only works on binary
    with open(file_path, "rb") as file:
        file_contents = file.read()
    
    cipher = AES.new(derived_key, AES.MODE_ECB)
    
    padded_file_contents = pad(file_contents, AES.block_size)

    offset = get_key_offset(salt.hex()) # Create an offset to store key

    encrypted_file_contents = cipher.encrypt(padded_file_contents)
    # Write new bytes to the file
    with open(encrypted_file_path, "wb") as encrypted_file:
        encrypted_file.write(encrypted_file_contents[:offset])
        encrypted_file.write(derived_key)
        encrypted_file.write(encrypted_file_contents[offset:])

    # Create meta file that should be secure to later use it for decryption and storing information about the original file
    create_meta(file_path, encrypted_file_path, key, salt, duration, "AES")

    # Custom function to increase file size by size_mb
    inflate_file(encrypted_file_path, size_mb)
    
    return create_package(file_path, encrypted_file_path)

# ChaCha20
def encrypt_file_ChaCha20(key, file_path, size_mb, duration, x):
    derived_key, salt = key_validator(key, None)

    custom_operation(x)

    if not os.path.exists(file_path):
        raise FileNotFoundError("File not found")
    
    validate_file(file_path)
    
    if len(derived_key) != 32:
        raise ValueError("Key length should be 32 bytes (256 bits)")
    
    encrypted_file_path = file_path + ".encryptedChaCha"

    with open(file_path, "rb") as file:
        file_contents = file.read()
    
    cipher = ChaCha20.new(key=derived_key)
    encrypted_file_contents = cipher.encrypt(file_contents)

    offset = get_key_offset(salt.hex())

    with open(encrypted_file_path, "wb") as encrypted_file:
        encrypted_file.write(cipher.nonce)
        encrypted_file.write(encrypted_file_contents[:offset])
        encrypted_file.write(derived_key)
        encrypted_file.write(encrypted_file_contents[offset:])
    
    create_meta(file_path, encrypted_file_path, key, salt, duration, "ChaCha20")

    inflate_file(encrypted_file_path, size_mb)
    return create_package(file_path, encrypted_file_path)

# TwoFish
def encrypt_file_TwoFish(key, file_path, size_mb, duration, x):
    derived_key, salt = key_validator(key, None)

    custom_operation(x)

    if not os.path.exists(file_path):
        raise FileNotFoundError("File not found")
    
    validate_file(file_path)
    
    if len(derived_key) != 32:
        raise ValueError("Key length should be 32 bytes (256 bits)")
    
    with open(file_path, "rb") as file:
        file_contents = file.read()
    
    padded = pad(file_contents, 16)
    cipher = Twofish(derived_key)
    
    # Encrypt 16 bytes blocks since twofish uses 16 byte blocks
    encrypted = b""
    for i in range(0, len(padded), 16):
        block = padded[i:i+16]
        encrypted += cipher.encrypt(block)

    encrypted_file_path = file_path + ".encryptedTwoFish"

    offset = get_key_offset(salt.hex())

    with open(encrypted_file_path, "wb") as file:
        file.write(encrypted[:offset])
        file.write(derived_key)
        file.write(encrypted[offset:])

    create_meta(file_path, encrypted_file_path, key, salt, duration, "TwoFish")
    
    inflate_file(encrypted_file_path, size_mb)
    return create_package(file_path, encrypted_file_path)
