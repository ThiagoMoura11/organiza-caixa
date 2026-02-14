@echo off
chcp 65001 >nul
title Instalador - Organiza Caixa

echo ========================================
echo    Organiza Caixa - Instalador
echo ========================================
echo.

REM Obter caminho dos Documentos
set "DOCS=%USERPROFILE%\Documents\OrganizaCaixa"

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python nao encontrado. Iniciando instalacao...
    echo.
    
    REM Baixar Python (versao embeddable mais leve)
    echo Baixando Python...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-embed-amd64.zip' -OutFile 'python.zip'"
    
    echo Extraindo Python...
    powershell -Command "Expand-Archive -Path 'python.zip' -DestinationPath 'C:\Python312' -Force"
    del python.zip
    
    echo Configurando Python...
    echo import sys >> C:\Python312\python._pth
    echo import site >> C:\Python312\python._pth
    
    REM Baixar get-pip
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'C:\Python312\get-pip.py'"
    
    echo Instalando pip...
    C:\Python312\python.exe C:\Python312\get-pip.py
    
    REM Adicionar ao PATH temporariamente
    set PATH=C:\Python312;C:\Python312\Scripts;%PATH%
    
    echo Python instalado!
) else (
    echo Python ja esta instalado.
)

echo.
echo Verificando pip...
python -m pip install --upgrade pip >nul 2>&1

echo.
echo Instalando dependencias do Organiza Caixa...
pip install streamlit pandas plotly openpyxl sqlalchemy bcrypt python-dotenv

echo.
echo Copiando arquivos para %DOCS%...
if not exist "%DOCS%" mkdir "%DOCS%"

REM Copiar arquivos do pendrive/pasta atual
xcopy /E /Y /Q "%~dp0app.py" "%DOCS%\" >nul 2>&1
xcopy /E /Y /Q /exclude:%~dp0exclude.txt "%~dp0src" "%DOCS%\src\" >nul 2>&1
if exist "%~dp0data" xcopy /E /Y /Q "%~dp0data" "%DOCS%\data\" >nul 2>&1

echo.
echo Criando atalho na Area de Trabalho...

REM Criar arquivo VBS para atalho
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\create_shortcut.vbs"
echo SetShortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\Organiza Caixa.lnk") >> "%TEMP%\create_shortcut.vbs"
echo Shortcut.TargetPath = "cmd.exe" >> "%TEMP%\create_shortcut.vbs"
echo Shortcut.Arguments = "/k cd /d ""%DOCS%"" && streamlit run app.py --server.headless true" >> "%TEMP%\create_shortcut.vbs"
echo Shortcut.WorkingDirectory = "%DOCS%" >> "%TEMP%\create_shortcut.vbs"
echo Shortcut.Description = "Organiza Caixa - Gestao Financeira" >> "%TEMP%\create_shortcut.vbs"
echo Shortcut.IconLocation = "cmd.exe, 0" >> "%TEMP%\create_shortcut.vbs"
echo Shortcut.Save >> "%TEMP%\create_shortcut.vbs"

cscript //nologo "%TEMP%\create_shortcut.vbs"
del "%TEMP%\create_shortcut.vbs"

echo.
echo ========================================
echo    Instalacao concluida!
echo ========================================
echo.
echo Para usar:
echo 1. Clique no atalho ""Organiza Caixa"" na Area de Trabalho
echo 2. O aplicativo abrira no navegador
echo.
echo Arquivos salvos em:
echo %DOCS%
echo.
echo IMPORTANTE: Mantenha os arquivos nesta pasta!
echo.

pause
