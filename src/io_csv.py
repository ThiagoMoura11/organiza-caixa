import streamlit as st
import pandas as pd
from datetime import datetime


def parse_date(date_str):
    date_str = str(date_str).strip()
    
    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
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


def load_extrato(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        
        df.columns = [c.strip().lower() for c in df.columns]
        
        required_cols = {'data', 'descricao', 'valor'}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            st.error(f"Colunas obrigatórias ausentes: {', '.join(missing)}")
            return None
        
        df['data'] = df['data'].apply(parse_date)
        if df['data'].isna().any():
            st.error("Algumas datas não puderam ser interpretadas. Use formato YYYY-MM-DD ou DD/MM/YYYY")
            return None
        
        df['valor'] = df['valor'].apply(parse_value)
        
        df['descricao'] = df['descricao'].astype(str).str.strip()
        
        df = df[['data', 'descricao', 'valor']].sort_values('data').reset_index(drop=True)
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao processar extrato: {str(e)}")
        return None


def load_regras(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        
        df.columns = [c.strip().lower() for c in df.columns]
        
        if 'match' not in df.columns or 'categoria' not in df.columns:
            st.error("O arquivo de regras deve ter colunas 'match' e 'categoria'")
            return None
        
        df['match'] = df['match'].astype(str).str.strip().str.lower()
        df['categoria'] = df['categoria'].astype(str).str.strip()
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao processar regras: {str(e)}")
        return None


def convert_df_to_csv(df):
    return df.to_csv(index=False, sep=';').encode('utf-8-sig')
