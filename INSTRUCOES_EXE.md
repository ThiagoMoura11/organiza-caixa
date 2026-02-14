# Como gerar o executável

## Problema com .exe
Streamlit é uma biblioteca web e não gera executáveis nativamente. Existem 2 alternativas:

## Alternativa 1: Criar instalador simples

```bash
# Instalar PyInstaller
pip install pyinstaller

# Gerar executável (mas não funcionará bem com Streamlit)
pyinstaller --onefile --name OrganizaCaixa app.py
```

## Alternativa 2: Entregar como código + instalador

Essa é a melhor opção para vender:

1. **Entrega**: Arquivos Python + instructions
2. **Cliente**: Instala Python + Roda `pip install -r requirements.txt` + `streamlit run app.py`
3. **Você**: Pode criar um instalador simples usando NSIS ou Inno Setup

---

## Script para criar instalador (Windows)

Quer que eu crie um instalador para Windows que:
- Instala o Python automaticamente
- Instala as dependências
- Cria atalho na área de trabalho
- Aceita CSV/Excel com clique duplo?
