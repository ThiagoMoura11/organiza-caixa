from supabase import create_client, Client
from datetime import datetime
from typing import Optional
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://cjvpldbsaxsrtmdvqeyv.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqdnBsZGJzYXhzcnRtZHZxZXl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEwOTUxMTEsImV4cCI6MjA4NjY3MTExMX0.qf-JHw4qYrwqYT58UqyIlKXhIvOOAdgqYR8RVty5gYQ')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


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


def get_lancamentos(user_id: int, conta: str = None):
    if not user_id:
        return []
    
    try:
        query = supabase.table('lancamentos').select('*').eq('user_id', user_id)
        
        if conta and conta != 'Todas':
            query = query.eq('conta', conta)
        
        result = query.order('data', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching lancamentos: {e}")
        return []


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
