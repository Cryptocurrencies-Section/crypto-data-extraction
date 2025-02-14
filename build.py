import PyInstaller.__main__
import os
import platform

# Ottieni il percorso assoluto della directory corrente
current_dir = os.path.dirname(os.path.abspath(__file__))

# Determina il separatore corretto per il sistema operativo
separator = ';' if platform.system() == 'Windows' else ':'

PyInstaller.__main__.run([
    'app.py',
    '--name=Badger',
    '--onefile',
    '--windowed',
    '--icon=favicon.ico',
    f'--add-data=favicon.ico{separator}.',
    f'--add-data=logo.png{separator}.',
    '--clean',
    '--noconfirm',
]) 