# Organiza Caixa Pro

MVP web para gestão de fluxo de caixa de pequenas empresas.

## Funcionalidades

- **Login simples** com credenciais configuráveis via .env
- **Upload de extrato CSV** com suporte a diversos formatos de data
- **Upload de regras de categorização** para classificar automaticamente
- **Dashboard completo**:
  - Fluxo de caixa mensal (entradas, saídas, saldo)
  - DRE simplificada (receita, despesas, lucro, margem)
  - Top 10 categorias de gastos
- **Filtros por período** (data início e fim)
- **Tabela de lançamentos** com todas as transações
- **Export CSV** dos relatórios e lançamentos

## Instalação

```bash
# Clone o projeto ou navegue até a pasta
cd $HOME/organiza-caixa-pro

# Crie o ambiente virtual
python -m venv .venv

# Ative o ambiente virtual
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Copie o arquivo de exemplo e configure as credenciais
cp .env.example .env

# Execute o app
streamlit run app.py
```

## Configuração

Edite o arquivo `.env` com suas credenciais:

```
APP_USER=admin
APP_PASS=sua_senha_aqui
```

## Formato dos CSVs

### Extrato CSV

Colunas obrigatórias (case-insensitive):
- **data**: Data no formato YYYY-MM-DD ou DD/MM/YYYY
- **descricao**: Descrição do lançamento
- **valor**: Valor positivo (entrada) ou negativo (saída)

Exemplo:
```csv
data,descricao,valor
15/01/2025,Pix Recebido - Cliente João,3500.00
16/01/2025,Ifood - Pedido #1234,-85.00
17/01/2025,Uber Viagem,-45.50
```

### Regras de Categorização CSV

Colunas obrigatórias:
- **match**: Texto a ser procurado na descrição (case-insensitive)
- **categoria**: Categoria a ser atribuída

Exemplo:
```csv
match,categoria
ifood,Alimentação
uber,Transporte
aluguel,Aluguel
energia,Contas de Luz
pix recebido,Receita
```

## Arquivos de Exemplo

O projeto inclui exemplos em `data/`:
- `sample_extrato.csv`: Extrato de exemplo com 18 lançamentos
- `regras_categorias.csv`: Regras de categorização para os exemplos

## Tecnologias

- Python 3.10+
- Streamlit 1.32.2
- Pandas 2.2.2
- Plotly 5.19.0
- python-dotenv 1.0.1
