import subprocess
import sys

def install_requirements():
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def build_exe():
    import PyInstaller.__main__
    PyInstaller.__main__.run([
        'app.py',
        '--name=OrganizaCaixa',
        '--onefile',
        '--windowed',
        '--add-data=src:src',
        '--hidden-import=streamlit',
        '--hidden-import=pandas',
        '--hidden-import=plotly',
        '--hidden-import=openpyxl',
        '--hidden-import=sqlalchemy',
        '--hidden-import=bcrypt',
        '--hidden-import=dotenv',
        '--collect-all=streamlit',
        '--collect-all=plotly',
        '--clean',
    ])

if __name__ == '__main__':
    install_requirements()
    build_exe()
    print('Executável gerado na pasta dist/')
