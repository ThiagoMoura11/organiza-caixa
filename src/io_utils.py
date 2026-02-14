import pandas as pd
from datetime import datetime
from io import BytesIO
from src.config import COLUNAS, CONTAS, CATEGORIAS


def parse_date(date_str):
    date_str = str(date_str).strip()
    
    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y']:
        try:
            return pd.to_datetime(datetime.strptime(date_str, fmt).date())
        except ValueError:
            continue
    
    try:
        return pd.to_datetime(date_str)
    except Exception:
        return None


def parse_value(val):
    if pd.isna(val):
        return 0.0
    
    val_str = str(val).strip()
    val_str = val_str.replace('.', '').replace(',', '.')
    
    try:
        return float(val_str)
    except ValueError:
        return 0.0


def detectar_banco(df, filename: str = '') -> str:
    cols_lower = [c.lower().strip() for c in df.columns]
    
    if 'agência' in cols_lower or 'conta corrente' in cols_lower or 'saldo anterior' in cols_lower:
        return 'Itau'
    if 'identificação' in cols_lower and 'data do movimento' in cols_lower:
        return 'Inter'
    
    return 'Outro'


def normalizar_extrato_itau(df: pd.DataFrame) -> pd.DataFrame:
    result = []
    
    for _, row in df.iterrows():
        data = parse_date(row.get('data', row.get('Data', None)))
        if data is None:
            continue
        
        descricao = str(row.get('descrição', row.get('Descrição', row.get('historico', '')))).strip()
        valor_str = str(row.get('valor', row.get('Valor', row.get('valor lançamento', 0))))
        valor = parse_value(valor_str)
        
        if 'crédito' in str(row.get('movimentação', '')).lower() or valor > 0:
            tipo = 'Entrada'
        else:
            tipo = 'Saída'
            valor = -abs(valor)
        
        cliente_fornecedor = ''
        if 'parceiro' in df.columns:
            cliente_fornecedor = str(row.get('parceiro', '')).strip()
        
        result.append({
            COLUNAS.DATA: data,
            COLUNAS.TIPO: tipo,
            COLUNAS.CATEGORIA: 'Sem categoria',
            COLUNAS.CLIENTE_FORNECEDOR: cliente_fornecedor,
            COLUNAS.DESCRICAO: descricao,
            COLUNAS.CONTA: 'Itau',
            COLUNAS.VALOR: valor
        })
    
    return pd.DataFrame(result)


def normalizar_extrato_inter(df: pd.DataFrame) -> pd.DataFrame:
    result = []
    
    for _, row in df.iterrows():
        data = parse_date(row.get('data do movimento', row.get('Data do movimento', None)))
        if data is None:
            continue
        
        descricao = str(row.get('Descrição', row.get('descrição', ''))).strip()
        valor = parse_value(row.get('valor', row.get('Valor', 0)))
        
        if 'c' in str(row.get('tipo', '')).lower() or valor > 0:
            tipo = 'Entrada'
        else:
            tipo = 'Saída'
            valor = -abs(valor)
        
        cliente_fornecedor = str(row.get('parceiro', row.get('Parceiro', ''))).strip()
        
        result.append({
            COLUNAS.DATA: data,
            COLUNAS.TIPO: tipo,
            COLUNAS.CATEGORIA: 'Sem categoria',
            COLUNAS.CLIENTE_FORNECEDOR: cliente_fornecedor,
            COLUNAS.DESCRICAO: descricao,
            COLUNAS.CONTA: 'Inter',
            COLUNAS.VALOR: valor
        })
    
    return pd.DataFrame(result)


def normalizar_extrato_padrao(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {
        'data': COLUNAS.DATA,
        'tipo': COLUNAS.TIPO,
        'categoria': COLUNAS.CATEGORIA,
        'cliente': COLUNAS.CLIENTE_FORNECEDOR,
        'fornecedor': COLUNAS.CLIENTE_FORNECEDOR,
        'cliente/fornecedor': COLUNAS.CLIENTE_FORNECEDOR,
        'descricao': COLUNAS.DESCRICAO,
        'descrição': COLUNAS.DESCRICAO,
        'conta': COLUNAS.CONTA,
        'valor': COLUNAS.VALOR,
    }
    
    df.columns = [c.lower().strip() for c in df.columns]
    df = df.rename(columns=col_map)
    
    if COLUNAS.DATA not in df.columns:
        raise ValueError('Coluna Data obrigatória')
    
    result = []
    for _, row in df.iterrows():
        data = parse_date(row.get(COLUNAS.DATA))
        if data is None:
            continue
        
        valor = parse_value(row.get(COLUNAS.VALOR, 0))
        
        if COLUNAS.TIPO in df.columns:
            tipo = str(row.get(COLUNAS.TIPO, '')).strip()
            if tipo.lower() not in ['entrada', 'saída', 'saida', 'entrada', 'crédito', 'débito', 'debito']:
                tipo = 'Entrada' if valor > 0 else 'Saída'
        else:
            tipo = 'Entrada' if valor > 0 else 'Saída'
        
        if valor < 0 and tipo == 'Entrada':
            valor = abs(valor)
        elif valor > 0 and tipo == 'Saída':
            valor = -abs(valor)
        
        result.append({
            COLUNAS.DATA: data,
            COLUNAS.TIPO: tipo,
            COLUNAS.CATEGORIA: str(row.get(COLUNAS.CATEGORIA, 'Sem categoria')).strip(),
            COLUNAS.CLIENTE_FORNECEDOR: str(row.get(COLUNAS.CLIENTE_FORNECEDOR, '')).strip(),
            COLUNAS.DESCRICAO: str(row.get(COLUNAS.DESCRICAO, '')).strip(),
            COLUNAS.CONTA: str(row.get(COLUNAS.CONTA, 'Itau')).strip(),
            COLUNAS.VALOR: valor
        })
    
    return pd.DataFrame(result)


def load_extrato(uploaded_file, filename: str = '') -> pd.DataFrame | None:
    try:
        if uploaded_file.name.endswith('.csv'):
            uploaded_file.seek(0)
            first_bytes = uploaded_file.read(1024)
            uploaded_file.seek(0)
            
            if b';' in first_bytes:
                df = pd.read_csv(uploaded_file, encoding='utf-8-sig', sep=';')
            else:
                df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            return None
        
        banco = detectar_banco(df, uploaded_file.name)
        
        if banco == 'Itau':
            return normalizar_extrato_itau(df)
        elif banco == 'Inter':
            return normalizar_extrato_inter(df)
        else:
            return normalizar_extrato_padrao(df)
    
    except Exception as e:
        raise Exception(f'Erro ao processar extrato: {str(e)}')


def export_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, sep=';', encoding='utf-8-sig')


def export_to_excel(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Lançamentos')
    return output.getvalue()
