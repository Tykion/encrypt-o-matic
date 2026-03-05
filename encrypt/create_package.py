import shutil
import subprocess
import os
import sys

def create_package(file_path, encrypted_file_path):
    app_name = os.path.splitext(os.path.basename(file_path))[0]
    package_dir = os.path.join(os.path.dirname(file_path), f"{app_name}.Encrypted")
    os.makedirs(package_dir, exist_ok=True)

    # move encrypted file and meta into folder
    meta_path = encrypted_file_path + ".meta"
    shutil.move(encrypted_file_path, package_dir)
    shutil.move(meta_path, package_dir)

    # get correct decrypt.exe path whether running as script or compiled exe
    if getattr(sys, 'frozen', False):
        decrypt_exe_src = os.path.join(os.path.dirname(sys.executable), "decrypt.exe")
    else:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        decrypt_exe_src = os.path.join(root_dir, "dist", "decrypt.exe")

    if not os.path.exists(decrypt_exe_src):
        print("Creating decrypt.exe...")
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        build_bat = os.path.join(root_dir, "encrypt", "build.bat")
        subprocess.run(build_bat, shell=True, cwd=root_dir)

    shutil.copy(decrypt_exe_src, package_dir)
    print(f"Package created at: {package_dir}")
    return package_dir