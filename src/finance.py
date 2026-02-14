import pandas as pd
from src.config import COLUNAS


def calcular_fluxo_mensal(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=['mes', 'Entradas', 'Saídas', 'Saldo'])
    
    df = df.copy()
    df['mes'] = pd.to_datetime(df[COLUNAS.DATA]).dt.to_period('M').astype(str)
    
    entradas = df[df[COLUNAS.VALOR] > 0].groupby('mes')[COLUNAS.VALOR].sum().reset_index()
    entradas.columns = ['mes', 'Entradas']
    
    saidas = df[df[COLUNAS.VALOR] < 0].groupby('mes')[COLUNAS.VALOR].sum().reset_index()
    saidas.columns = ['mes', 'Saídas']
    saidas['Saídas'] = saidas['Saídas'].abs()
    
    fluxo = pd.merge(entradas, saidas, on='mes', how='outer').fillna(0)
    fluxo['Saldo'] = fluxo['Entradas'] - fluxo['Saídas']
    fluxo = fluxo.sort_values('mes')
    
    return fluxo


def calcular_dre(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {
            'receita_total': 0.0,
            'despesas_totais': 0.0,
            'lucro': 0.0,
            'margem': 0.0
        }
    
    receita_total = df[df[COLUNAS.VALOR] > 0][COLUNAS.VALOR].sum()
    despesas_totais = abs(df[df[COLUNAS.VALOR] < 0][COLUNAS.VALOR].sum())
    lucro = receita_total - despesas_totais
    margem = (lucro / receita_total * 100) if receita_total > 0 else 0.0
    
    return {
        'receita_total': receita_total,
        'despesas_totais': despesas_totais,
        'lucro': lucro,
        'margem': margem
    }


def top_categorias_saida(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=['categoria', 'total'])
    
    saidas = df[df[COLUNAS.VALOR] < 0].copy()
    saidas['valor_abs'] = saidas[COLUNAS.VALOR].abs()
    
    top = saidas.groupby(COLUNAS.CATEGORIA)['valor_abs'].sum().reset_index()
    top.columns = ['categoria', 'total']
    top = top.sort_values('total', ascending=False).head(top_n)
    
    return top


def top_categorias_entrada(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=['categoria', 'total'])
    
    entradas = df[df[COLUNAS.VALOR] > 0].copy()
    
    top = entradas.groupby(COLUNAS.CATEGORIA)[COLUNAS.VALOR].sum().reset_index()
    top.columns = ['categoria', 'total']
    top = top.sort_values('total', ascending=False).head(top_n)
    
    return top


def calcular_kpis(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {'entradas': 0.0, 'saidas': 0.0, 'saldo': 0.0}
    
    entradas = df[df[COLUNAS.VALOR] > 0][COLUNAS.VALOR].sum()
    saidas = abs(df[df[COLUNAS.VALOR] < 0][COLUNAS.VALOR].sum())
    saldo = entradas - saidas
    
    return {'entradas': entradas, 'saidas': saidas, 'saldo': saldo}


def gastos_por_conta(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=['conta', 'entradas', 'saidas', 'saldo'])
    
    result = []
    
    for conta in df[COLUNAS.CONTA].unique():
        df_conta = df[df[COLUNAS.CONTA] == conta]
        entradas = df_conta[df_conta[COLUNAS.VALOR] > 0][COLUNAS.VALOR].sum()
        saidas = abs(df_conta[df_conta[COLUNAS.VALOR] < 0][COLUNAS.VALOR].sum())
        result.append({
            'conta': conta,
            'entradas': entradas,
            'saidas': saidas,
            'saldo': entradas - saidas
        })
    
    return pd.DataFrame(result)
