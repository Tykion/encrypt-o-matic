import json
import subprocess
import sys
import getpass
#from encrypt.modified.twofish import Twofish
from Crypto.Cipher import AES, ChaCha20
from Crypto.Util.Padding import unpad
from encrypt.key_validator import *
from encrypt.inflate_size import *
from encrypt.get_trusted_time import get_trusted_time
import os

def find_encrypted_file():
    # handle both normal python and PyInstaller compiled exe
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)  # use exe location
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__)) # or run script directly for testing
                                                                # maybe delete later
    
    for file in os.listdir(script_dir):
        if file.endswith((".encryptedAES", ".encryptedChaCha", ".encryptedTwoFish")):
            return os.path.join(script_dir, file)
    
    raise FileNotFoundError("No encrypted file found")

def delete_files_after_decryption():
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for file in os.listdir(script_dir):
        if file.endswith((".encryptedAES", ".encryptedChaCha",".encryptedTwoFish", ".meta")):
            full_path = os.path.join(script_dir, file)
            os.remove(full_path)
    

def read_encrypted_data(encrypted_file_path, meta):
    original_size = meta["original_size"]
    offset = get_key_offset(meta["salt"])
    
    with open(encrypted_file_path, "rb") as f:
        data = f.read(original_size)
    
    if meta["algorithm"] == "ChaCha20":
        nonce = data[:8]
        rest = data[8:]
        derived_key = rest[offset:offset+32]
        clean_data = rest[:offset] + rest[offset+32:]
        return clean_data, derived_key, nonce
    else:
        derived_key = data[offset:offset+32]
        clean_data = data[:offset] + data[offset+32:]
        return clean_data, derived_key, None

def is_locked(meta):
    return get_trusted_time() <= meta["unlock_at"]

def load_meta(encrypted_file_path):
    meta_path = encrypted_file_path + ".meta"
    with open(meta_path, "r") as f:
        return json.load(f)
    
def decrypt_file_AES(encrypted_file_path, meta):
    data, derived_key, _ = read_encrypted_data(encrypted_file_path, meta)
    cipher = AES.new(derived_key, AES.MODE_ECB)
    decrypted = unpad(cipher.decrypt(data), AES.block_size)

    filename = os.path.basename(meta["original_name"])
    if getattr(sys, 'frozen', False):
        output_path = os.path.join(os.path.dirname(sys.executable), filename)
    else:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    with open(output_path, "wb") as f:
        f.write(decrypted)
    return output_path

def decrypt_file_ChaCha20(encrypted_file_path, meta):
    data, derived_key, nonce = read_encrypted_data(encrypted_file_path, meta)
    cipher = ChaCha20.new(key=derived_key, nonce=nonce)
    decrypted = cipher.decrypt(data)

    filename = os.path.basename(meta["original_name"])
    if getattr(sys, 'frozen', False):
        output_path = os.path.join(os.path.dirname(sys.executable), filename)
    else:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    with open(output_path, "wb") as f:
        f.write(decrypted)
    return output_path

def decrypt_file_TwoFish(encrypted_file_path, meta):
    data, derived_key, _ = read_encrypted_data(encrypted_file_path, meta)
    cipher = Twofish(derived_key)
    decrypted = b""
    for i in range(0, len(data), 16):
        block = data[i:i+16]
        decrypted += cipher.decrypt(block)
    decrypted = unpad(decrypted, 16)
    
    filename = os.path.basename(meta["original_name"])
    if getattr(sys, 'frozen', False):
        output_path = os.path.join(os.path.dirname(sys.executable), filename)
    else:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    with open(output_path, "wb") as f:
        f.write(decrypted)
    return output_path

def decrypt(encrypted_file_path, key, meta):
    valid, _ = verify_key(key, meta)

    if not valid:
        print("Wrong password")
        return
    
    match meta["algorithm"]:
        case "AES":
            output = decrypt_file_AES(encrypted_file_path, meta)
        case "ChaCha20":
            output = decrypt_file_ChaCha20(encrypted_file_path, meta)
        case "TwoFish":
            output = decrypt_file_TwoFish(encrypted_file_path, meta)
        
    print(f"Decrypted to {output}")
    





#!!!!!!!!!!!!!!!!!!
#IGNORE (pasted the twofish package here because it was giving me a headache)
# if __name__ == "__main__" at the bottom
#!!!!!!!!!!!!!!!!!!


import importlib.util
import pathlib
import sys

from ctypes import (cdll, Structure,
                    POINTER, pointer,
                    c_char_p, c_int, c_uint32,
                    create_string_buffer)

def _load_twofish_library():
    spec = importlib.util.find_spec("_twofish")
    if spec is None or spec.origin is None:
        raise ImportError("Unable to locate _twofish shared library")

    return cdll.LoadLibrary(str(pathlib.Path(spec.origin)))

_twofish = _load_twofish_library()

class _Twofish_key(Structure):
    _fields_ = [("s", (c_uint32 * 4) * 256),
                ("K", c_uint32 * 40)]

_Twofish_initialise = _twofish.exp_Twofish_initialise
_Twofish_initialise.argtypes = []
_Twofish_initialise.restype = None

_Twofish_prepare_key = _twofish.exp_Twofish_prepare_key
_Twofish_prepare_key.argtypes = [ c_char_p,  # uint8_t key[]
                                  c_int,     # int key_len
                                  POINTER(_Twofish_key) ]
_Twofish_prepare_key.restype = None

_Twofish_encrypt = _twofish.exp_Twofish_encrypt
_Twofish_encrypt.argtypes = [ POINTER(_Twofish_key),
                              c_char_p,     # uint8_t p[16]
                              c_char_p      # uint8_t c[16]
                            ]
_Twofish_encrypt.restype = None

_Twofish_decrypt = _twofish.exp_Twofish_decrypt
_Twofish_decrypt.argtypes = [ POINTER(_Twofish_key),
                              c_char_p,     # uint8_t c[16]
                              c_char_p      # uint8_t p[16]
                            ]
_Twofish_decrypt.restype = None

_Twofish_initialise()

IS_PY2 = sys.version_info < (3, 0, 0, 'final', 0)

def _ensure_bytes(data):
    if (IS_PY2 and not isinstance(data, str)) or (not IS_PY2 and not isinstance(data, bytes)):
        raise TypeError('can not encrypt/decrypt unicode objects')


class Twofish():
    def __init__(self, key):
        if not (len(key) > 0 and len(key) <= 32):
            raise ValueError('invalid key length')
        _ensure_bytes(key)

        self.key = _Twofish_key()
        _Twofish_prepare_key(key, len(key), pointer(self.key))

    def encrypt(self, data):
        if not len(data) == 16:
            raise ValueError('invalid block length')
        _ensure_bytes(data)

        outbuf = create_string_buffer(len(data))
        _Twofish_encrypt(pointer(self.key), data, outbuf)
        return outbuf.raw

    def decrypt(self, data):
        if not len(data) == 16:
            raise ValueError('invalid block length')
        _ensure_bytes(data)

        outbuf = create_string_buffer(len(data))
        _Twofish_decrypt(pointer(self.key), data, outbuf)
        return outbuf.raw


# Repeat the test on the same vectors checked at runtime by the library
def self_test():
    import binascii

    # 128-bit test is the I=3 case of section B.2 of the Twofish book.
    t128 = ('9F589F5CF6122C32B6BFEC2F2AE8C35A',
        'D491DB16E7B1C39E86CB086B789F5419',
        '019F9809DE1711858FAAC3A3BA20FBC3')

    # 192-bit test is the I=4 case of section B.2 of the Twofish book.
    t192 = ('88B2B2706B105E36B446BB6D731A1E88EFA71F788965BD44',
        '39DA69D6BA4997D585B6DC073CA341B2',
        '182B02D81497EA45F9DAACDC29193A65')

    # 256-bit test is the I=4 case of section B.2 of the Twofish book.
    t256 = ('D43BB7556EA32E46F2A282B7D45B4E0D57FF739D4DC92C1BD7FC01700CC8216F',
        '90AFE91BB288544F2C32DC239B2635E6',
        '6CB4561C40BF0A9705931CB6D408E7FA')

    for t in (t128, t192, t256):
        k = binascii.unhexlify(t[0])
        p = binascii.unhexlify(t[1])
        c = binascii.unhexlify(t[2])

        T = Twofish(k)
        if not T.encrypt(p) == c or not T.decrypt(c) == p:
            raise ImportError('the Twofish library is corrupted')

self_test()

#!!!!!!!!!!!!!!!!!!

if __name__ == "__main__":
    try:
        #encrypted_file_path = input("Enter encrypted file path(C:\\path\\to\\file): ")
        encrypted_file_path = find_encrypted_file()
        meta = load_meta(encrypted_file_path)

        # Check the timer before asking password
        if is_locked(meta):
            key = getpass.getpass("Enter master password to unlock early: ")
            decrypt(encrypted_file_path, key, meta)
        else:
            print("Timer expired, auto decrypting...")
            match meta["algorithm"]:
                case "AES":
                    output = decrypt_file_AES(encrypted_file_path, meta)
                case "ChaCha20":
                    output = decrypt_file_ChaCha20(encrypted_file_path, meta)
                case "TwoFish":
                    output = decrypt_file_TwoFish(encrypted_file_path, meta)
            print(f"Decrypted to {output}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        delete_files_after_decryption()
        input("Press Enter to exit...")
        if getattr(sys, 'frozen', False):
            # Create a temp batch file to delete decrypt.exe
            bat = os.path.join(os.path.dirname(sys.executable), "_c.bat")
            open(bat, 'w').write(f'@echo off\ntimeout /t 2 /nobreak>nul\ndel "{sys.executable}"\ndel "%~f0"')
            subprocess.Popen(bat, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)