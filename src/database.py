from supabase import create_client, Client
from datetime import datetime
from typing import Optional
import streamlit as st
import bcrypt
import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

if not SUPABASE_URL or not SUPABASE_KEY:
    SUPABASE_URL = st.secrets.get('SUPABASE_URL', '') if hasattr(st, 'secrets') else ''
    SUPABASE_KEY = st.secrets.get('SUPABASE_KEY', '') if hasattr(st, 'secrets') else ''

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


def init_db():
    pass


def create_user(username: str, password: str):
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    result = supabase.table('users').insert({
        'username': username,
        'password_hash': password_hash,
        'created_at': datetime.utcnow().isoformat()
    }).execute()
    
    return result.data[0] if result.data else None


def get_user(username: str):
    result = supabase.table('users').select('*').eq('username', username).execute()
    return result.data[0] if result.data else None


def get_user_by_id(user_id: int):
    result = supabase.table('users').select('*').eq('id', user_id).execute()
    return result.data[0] if result.data else None


def verify_password(user, password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8'))


def delete_user(user_id: int):
    supabase.table('orcamentos').delete().eq('user_id', user_id).execute()
    supabase.table('lancamentos').delete().eq('user_id', user_id).execute()
    supabase.table('users').delete().eq('id', user_id).execute()


def save_lancamento(
    user_id: int,
    data,
    tipo: str,
    categoria: str,
    cliente_fornecedor: str,
    descricao: str,
    conta: str,
    valor: float
):
    if not supabase:
        raise Exception("Supabase not configured")
    
    try:
        data_str = data.isoformat() if isinstance(data, datetime) else data
        
        result = supabase.table('lancamentos').insert({
            'user_id': user_id,
            'data': data_str,
            'tipo': tipo,
            'categoria': categoria,
            'cliente_fornecedor': cliente_fornecedor or '',
            'descricao': descricao or '',
            'conta': conta,
            'valor': valor,
            'created_at': datetime.utcnow().isoformat()
        }).execute()
        
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error saving lancamento: {e}")
        raise


def get_lancamentos(user_id: int, conta: str = None):
    if not supabase or not user_id:
        return []
    
    try:
        user_id_int = int(user_id)
        query = supabase.table('lancamentos').select('*').eq('user_id', user_id_int)
        
        if conta and conta != 'Todas':
            query = query.eq('conta', conta)
        
        result = query.order('data', desc=True).execute()
        
        st.session_state['lancamentos_cache'] = result.data if result.data else []
        return st.session_state.get('lancamentos_cache', [])
    except Exception as e:
        print(f"Error fetching lancamentos: {e}")
        return st.session_state.get('lancamentos_cache', [])


def delete_lancamento(lancamento_id: int, user_id: int):
    try:
        supabase.table('lancamentos').delete().eq('id', lancamento_id).eq('user_id', user_id).execute()
    except Exception as e:
        print(f"Error deleting lancamento: {e}")


def delete_all_lancamentos(user_id: int, conta: Optional[str] = None):
    try:
        query = supabase.table('lancamentos').delete().eq('user_id', user_id)
        if conta and conta != 'Todas':
            query = query.eq('conta', conta)
        query.execute()
    except Exception as e:
        print(f"Error deleting all lancamentos: {e}")


def save_orcamento(user_id: int, categoria: str, limite: float, mes: str):
    existing = supabase.table('orcamentos').select('*').eq('user_id', user_id).eq('categoria', categoria).eq('mes', mes).execute()
    
    if existing.data:
        supabase.table('orcamentos').update({'limite': limite}).eq('id', existing.data[0]['id']).execute()
    else:
        supabase.table('orcamentos').insert({
            'user_id': user_id,
            'categoria': categoria,
            'limite': limite,
            'mes': mes,
            'created_at': datetime.utcnow().isoformat()
        }).execute()


def get_orcamentos(user_id: int, mes: str):
    result = supabase.table('orcamentos').select('*').eq('user_id', user_id).eq('mes', mes).execute()
    return result.data
