import subprocess
import sys
import os
import urllib.request
import zipfile
import shutil
import time

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

def check_python():
    result = subprocess.run(['python', '--version'], capture_output=True, text=True)
    return result.returncode == 0

def download_python():
    print("Baixando Python...")
    url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-embed-amd64.zip"
    urllib.request.urlretrieve(url, "python.zip")
    
    print("Extraindo Python...")
    with zipfile.ZipFile("python.zip", 'r') as zip_ref:
        zip_ref.extractall("C:\\Python312")
    
    os.remove("python.zip")
    
    # Habilitar pip
    with open("C:\\Python312\\python._pth", "a") as f:
        f.write("import site\n")
    
    print("Instalando pip...")
    urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "C:\\Python312\\get-pip.py")
    os.system('C:\\Python312\\python.exe C:\\Python312\\get-pip.py')
    
    return True

def install_dependencies():
    print("Instalando dependências...")
    deps = ["streamlit", "pandas", "plotly", "openpyxl", "sqlalchemy", "bcrypt", "python-dotenv"]
    for dep in deps:
        print(f"Instalando {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "install", dep, "--quiet"])
    return True

def create_shortcut():
    import winshell
    from win32com.client import Dispatch
    
    desktop = winshell.desktop()
    path = os.path.join(desktop, "Organiza Caixa.lnk")
    target = os.path.abspath(__file__)
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.TargetPath = "cmd.exe"
    shortcut.Arguments = f'/k cd /d "{os.getcwd()}" && streamlit run app.py --server.headless true'
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.Description = "Organiza Caixa - Gestão Financeira"
    shortcut.Save()
    return True

def main():
    print("=" * 50)
    print("  ORGANIZA CAIXA - INSTALADOR")
    print("=" * 50)
    
    # Verificar Python
    if not check_python():
        print("\nPython não encontrado. Baixando...")
        download_python()
        # Atualizar PATH temporariamente
        os.environ['PATH'] = r'C:\Python312;C:\Python312\Scripts;' + os.environ['PATH']
    else:
        print("\nPython já está instalado.")
    
    # Instalar dependências
    install_dependencies()
    
    # Criar atalho
    try:
        create_shortcut()
        print("\nAtalho criado na Área de Trabalho!")
    except:
        print("\nNão foi possível criar atalho. Execute: streamlit run app.py")
    
    print("\n" + "=" * 50)
    print("  INSTALAÇÃO CONCLUÍDA!")
    print("=" * 50)
    print("\nExecutando Organiza Caixa...")
    
    # Abrir app
    os.system("streamlit run app.py --server.headless true")

if __name__ == "__main__":
    main()
