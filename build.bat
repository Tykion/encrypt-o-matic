REM This is a pyinstaller command to compile the decrypt.exe alongside the encrypted file
pyinstaller --onefile ^
    --hidden-import=Crypto ^
    --hidden-import=Crypto.Cipher.AES ^
    --hidden-import=Crypto.Cipher.ChaCha20 ^
    --hidden-import=Crypto.Util.Padding ^
    --add-binary ".venv\Lib\site-packages\_twofish.cp313-win_amd64.pyd;." ^
    --paths "." ^
    decrypt.py

REM Compile encrypt-o-matic.exe
pyinstaller --onefile ^
    --hidden-import=Crypto ^
    --hidden-import=Crypto.Cipher.AES ^
    --hidden-import=Crypto.Cipher.ChaCha20 ^
    --hidden-import=Crypto.Util.Padding ^
    --add-binary ".venv\Lib\site-packages\_twofish.cp313-win_amd64.pyd;." ^
    --paths "." ^
    --name "encrypt-o-matic" ^
    main.py