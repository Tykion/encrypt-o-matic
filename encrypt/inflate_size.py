import os

def inflate_file(file_path, size_mb):
    if size_mb is None:
        return
    
    junk = os.urandom(size_mb * 1024 *1024)

    with open(file_path, "ab") as f:
        f.write(junk)

def read_encrypted_data(encrypted_file_path, meta):
    original_size = meta["original_size"]
    with open(encrypted_file_path, "rb") as f:
        data = f.read(original_size)
    return data

def validate_file(file_path):
    if os.path.getsize(file_path) == 0:
        raise ValueError("File is empty")
    if os.path.getsize(file_path) > 1* 1024*1024*1024:
        raise ValueError("File is too large (max 1GB)")
    if not file_path.endswith('.exe'):
        raise ValueError("File must be a Windows executable (.exe)")
    if not os.access(file_path, os.R_OK):
        raise PermissionError("No read permission on file")
    if not os.access(os.path.dirname(file_path), os.W_OK):
        raise PermissionError("No write permission in target directory")