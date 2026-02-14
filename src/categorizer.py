import pandas as pd
from src.config import CATEGORIAS


REGRAS_AUTOMATICAS = {
    'seguro': 'Seguro',
    'parcela': 'Parcela compra',
    'aluguel': 'Aluguel',
    'itau': 'Itau',
    'cartão': 'Cartão de Crédito',
    'cartao': 'Cartão de Crédito',
    'credito': 'Cartão de Crédito',
    'reembolso': 'Reembolso',
    'pedágio': 'Pedagio',
    'pedagio': 'Pedagio',
    'financiamento': 'Financiamento',
    'pessoal': 'Pessoal',
    'tarifa': 'Tarifa Bancaria',
    'imposto': 'Imposto',
    'salário': 'Salario',
    'salario': 'Salario',
    'abastecimento': 'Abastecimento',
    'combustível': 'Abastecimento',
    'combustivel': 'Abastecimento',
    'manutenção': 'Manutenção',
    'manutencao': 'Manutenção',
    'contabilidade': 'Contabilidade',
    'rastreador': 'Rastreador',
    'aplicação': 'Recebimento Aplicação',
    'amonex': 'Operação amonex',
    'log': 'Operação LOG',
    'brasil web': 'Velada - Brasil Web',
    'frete': 'Frete',
    'transferência': 'Transferência',
    'transferencia': 'Transferência',
}


def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    
    df = df.copy()
    
    df['Categoria'] = 'Sem categoria'
    
    for keyword, categoria in REGRAS_AUTOMATICAS.items():
        mask = df['Descrição'].str.lower().str.contains(keyword, na=False)
        df.loc[mask, 'Categoria'] = categoria
    
    return df


def categorize_by_descricao(descricao: str) -> str:
    desc_lower = descricao.lower()
    
    for keyword, categoria in REGRAS_AUTOMATICAS.items():
        if keyword in desc_lower:
            return categoria
    
    return 'Sem categoria'
