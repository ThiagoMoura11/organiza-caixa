import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.database import init_db, create_user, get_user, get_user_by_id, verify_password

init_db()


def init_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None


def login_form():
    st.title('Organiza Caixa')
    
    tab_login, tab_cadastro = st.tabs(['Entrar', 'Cadastrar'])
    
    with tab_login:
        with st.form('login_form'):
            username = st.text_input('Usuário')
            password = st.text_input('Senha', type='password')
            submit = st.form_submit_button('Entrar')
            
            if submit:
                user = get_user(username)
                if user and verify_password(user, password):
                    st.session_state.logged_in = True
                    st.session_state.user_id = user['id']
                    st.session_state.username = user['username']
                    st.rerun()
                else:
                    st.error('Usuário ou senha incorretos')
    
    with tab_cadastro:
        with st.form('cadastro_form'):
            novo_usuario = st.text_input('Novo Usuário')
            nova_senha = st.text_input('Nova Senha', type='password')
            confirmar_senha = st.text_input('Confirmar Senha', type='password')
            submit_cadastro = st.form_submit_button('Cadastrar')
            
            if submit_cadastro:
                if not novo_usuario or not nova_senha:
                    st.error('Usuário e senha são obrigatórios')
                elif nova_senha != confirmar_senha:
                    st.error('As senhas não conferem')
                else:
                    existing = get_user(novo_usuario)
                    if existing:
                        st.error('Usuário já existe')
                    else:
                        create_user(novo_usuario, nova_senha)
                        st.success('Cadastro realizado! Faça login.')
    
    if not st.session_state.logged_in:
        st.stop()


def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()


def check_auth():
    if not st.session_state.logged_in:
        login_form()
        st.stop()
