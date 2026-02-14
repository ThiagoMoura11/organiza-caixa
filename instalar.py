print("=" * 50)
print("  ORGANIZA CAIXA - INSTALADOR")
print("=" * 50)
print()

import subprocess
import sys
import os
import urllib.request
import zipfile
import shutil
import time
import ctypes

def check_admin():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        return is_admin
    except:
        return False

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

def check_python():
    result = subprocess.run(['python', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Python ja instalado: {result.stdout.strip()}")
        return True
    return False

def download_and_install_python():
    print("\nPython nao encontrado. Baixando...")
    try:
        url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
        urllib.request.urlretrieve(url, "python_installer.exe")
        
        print("Instalando Python (aguarde ~2 minutos)...")
        subprocess.run(["python_installer.exe", "/quiet", "InstallAllUsers=1", "PrependPath=1", "AssociateFiles=0", "Shortcuts=0"], check=True)
        
        os.remove("python_installer.exe")
        
        # Atualizar PATH na sessão atual
        os.environ['PATH'] = r'C:\Python312;C:\Python312\Scripts;' + os.environ['PATH']
        
        print("Python instalado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao instalar Python: {e}")
        return False

def install_dependencies():
    print("\nInstalando dependencias...")
    deps = ["streamlit", "pandas", "plotly", "openpyxl", "sqlalchemy", "bcrypt", "python-dotenv"]
    
    for dep in deps:
        print(f"  Instalando {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "install", dep, "--quiet"], check=True)
    
    print("Todas as dependencias instaladas!")

def create_shortcut():
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop, "Organiza Caixa.lnk")
        
        # Criar atalho usando VBS
        vbs = f'''
Set WshShell = CreateObject("WScript.Shell")
Set Shortcut = WshShell.CreateShortcut("{shortcut_path}")
Shortcut.TargetPath = "cmd.exe"
Shortcut.Arguments = "/k cd /d ""{os.getcwd()}"" && streamlit run app.py --server.headless true"
Shortcut.WorkingDirectory = "{os.getcwd()}"
Shortcut.Description = "Organiza Caixa - Gestao Financeira"
Shortcut.Save
'''
        with open("create_shortcut.vbs", "w", encoding="utf-8") as f:
            f.write(vbs)
        
        subprocess.run(["cscript", "//nologo", "create_shortcut.vbs"], check=True)
        os.remove("create_shortcut.vbs")
        print("Atalho criado na Area de Trabalho!")
    except Exception as e:
        print(f"Nota: Atalho nao criado ({e})")

def main():
    # Verificar Python
    if not check_python():
        download_and_install_python()
    
    # Instalar dependencias
    install_dependencies()
    
    # Criar atalho
    create_shortcut()
    
    print("\n" + "=" * 50)
    print("  INSTALACAO CONCLUIDA!")
    print("=" * 50)
    print("\nPara executar, clique no atalho na Area de Trabalho")
    print("Ou execute: streamlit run app.py")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()
