import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime

from src.auth import init_session, login_form, logout
from src.database import (
    save_lancamento, get_lancamentos, delete_lancamento, delete_all_lancamentos,
    save_orcamento, get_orcamentos
)
from src.io_utils import load_extrato, export_to_csv, export_to_excel
from src.categorizer import categorize_transactions
from src.finance import calcular_fluxo_mensal, calcular_dre, top_categorias_saida, calcular_kpis, gastos_por_conta
from src.config import CONTAS, CATEGORIAS, COLUNAS

st.set_page_config(layout='wide', page_title='Organiza Caixa', initial_sidebar_state='expanded')

init_session()

if not st.session_state.logged_in:
    login_form()
    st.stop()

st.title('Organiza Caixa')

with st.sidebar:
    st.write(f'Logado como: **{st.session_state.username}**')
    if st.button('Sair'):
        logout()
    st.divider()

st.sidebar.header('Conta')
conta_selecionada = st.sidebar.selectbox(
    'Selecionar Conta',
    ['Todas'] + CONTAS,
    key='conta_selecionada'
)

st.sidebar.header('Upload de Arquivos')
extrato_file = st.sidebar.file_uploader(
    'Extrato CSV ou Excel',
    type=['csv', 'xlsx', 'xls'],
    key='extrato'
)

if extrato_file:
    try:
        df = load_extrato(extrato_file)
        if df is not None:
            df = categorize_transactions(df)
            
            delete_all_lancamentos(st.session_state.user_id, conta_selecionada if conta_selecionada != 'Todas' else None)
            
            for _, row in df.iterrows():
                save_lancamento(
                    st.session_state.user_id,
                    row[COLUNAS.DATA],
                    str(row[COLUNAS.TIPO]),
                    str(row[COLUNAS.CATEGORIA]),
                    str(row.get(COLUNAS.CLIENTE_FORNECEDOR, '')),
                    str(row.get(COLUNAS.DESCRICAO, '')),
                    str(row[COLUNAS.CONTA]),
                    float(row[COLUNAS.VALOR])
                )
            
            st.success('Extrato importado com sucesso!')
            st.rerun()
    except Exception as e:
        st.error(f'Erro ao processar extrato: {str(e)}')

lancamentos = get_lancamentos(st.session_state.user_id, conta_selecionada if conta_selecionada != 'Todas' else None)

st.sidebar.header('Filtros')

if lancamentos:
    df = pd.DataFrame([{
        'id': l['id'],
        'Data': l['data'],
        'Tipo': l['tipo'],
        'Categoria': l['categoria'],
        'Cliente/Fornecedor': l['cliente_fornecedor'],
        'Descrição': l['descricao'],
        'Conta': l['conta'],
        'Valor': l['valor']
    } for l in lancamentos])
    
    if df.empty:
        st.warning('Nenhum lançamento encontrado.')
        st.stop()
    
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data'])
    
    if df.empty:
        st.warning('Nenhum lançamento com data válida.')
        st.stop()
    
    min_date = df['Data'].min().date()
    max_date = df['Data'].max().date()
    
    data_inicio = st.sidebar.date_input('Data Início', min_date, min_value=min_date, max_value=max_date)
    data_fim = st.sidebar.date_input('Data Fim', max_date, min_value=min_date, max_value=max_date)
    
    df_filtrado = df[(df['Data'].dt.date >= pd.to_datetime(data_inicio).date()) & 
                     (df['Data'].dt.date <= pd.to_datetime(data_fim).date())]
    
    categorias_disponiveis = ['Todas'] + sorted(df['Categoria'].unique().tolist())
    categoria_filtro = st.sidebar.selectbox('Categoria', categorias_disponiveis)
    if categoria_filtro != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria_filtro]
    
    kpis = calcular_kpis(df_filtrado)
    
    st.header('KPIs')
    
    col1, col2, col3 = st.columns(3)
    col1.metric('Entradas', f'R$ {kpis["entradas"]:,.2f}', delta_color='normal')
    col2.metric('Saídas', f'R$ {kpis["saidas"]:,.2f}', delta_color='inverse')
    col3.metric('Saldo', f'R$ {kpis["saldo"]:,.2f}', delta_color='normal')
    
    st.divider()
    
    st.header('Fluxo de Caixa Mensal')
    
    fluxo = calcular_fluxo_mensal(df_filtrado)
    
    if not fluxo.empty:
        col_g1, col_g2 = st.columns([2, 1])
        
        with col_g1:
            fig_bar = px.bar(
                fluxo,
                x='mes',
                y=['Entradas', 'Saídas', 'Saldo'],
                barmode='group',
                title='Entradas vs Saídas por Mês',
                color_discrete_map={'Entradas': '#2ecc71', 'Saídas': '#e74c3c', 'Saldo': '#3498db'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col_g2:
            st.dataframe(fluxo, hide_index=True, use_container_width=True)
        
        csv_fluxo = export_to_csv(fluxo)
        st.download_button(
            'Download Fluxo CSV',
            csv_fluxo,
            'fluxo_caixa.csv',
            'text/csv'
        )
    
    st.divider()
    
    st.header('DRE Simplificada')
    
    dre = calcular_dre(df_filtrado)
    
    col_dre1, col_dre2, col_dre3, col_dre4 = st.columns(4)
    col_dre1.metric('Receita Total', f'R$ {dre["receita_total"]:,.2f}')
    col_dre2.metric('Despesas Totais', f'R$ {dre["despesas_totais"]:,.2f}')
    col_dre3.metric('Lucro', f'R$ {dre["lucro"]:,.2f}')
    col_dre4.metric('Margem', f'{dre["margem"]:.1f}%')
    
    st.divider()
    
    st.header('Gastos por Categoria')
    
    top_cats = top_categorias_saida(df_filtrado, 10)
    
    if not top_cats.empty:
        col_t1, col_t2 = st.columns([2, 1])
        
        with col_t1:
            fig_pie = px.pie(
                top_cats,
                values='total',
                names='categoria',
                title='Distribuição de Gastos por Categoria',
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_t2:
            st.dataframe(top_cats, hide_index=True, use_container_width=True)
    
    st.divider()
    
    st.header('Gastos por Conta')
    
    gastos_conta = gastos_por_conta(df_filtrado)
    
    if not gastos_conta.empty:
        col_c1, col_c2 = st.columns([2, 1])
        
        with col_c1:
            fig_conta = px.bar(
                gastos_conta,
                x='conta',
                y=['entradas', 'saidas'],
                title='Entradas e Saídas por Conta',
                barmode='group',
                color_discrete_map={'entradas': '#2ecc71', 'saidas': '#e74c3c'}
            )
            st.plotly_chart(fig_conta, use_container_width=True)
        
        with col_c2:
            st.dataframe(gastos_conta, hide_index=True, use_container_width=True)
    
    st.divider()
    
    st.header('Lançamentos')
    
    col_botoes1, col_botoes2 = st.columns([1, 6])
    with col_botoes1:
        with st.expander('Adicionar'):
            with st.form('add_lancamento'):
                nova_data = st.date_input('Data', date.today())
                nova_desc = st.text_input('Descrição')
                novo_valor = st.number_input('Valor', value=0.0, step=0.01)
                nova_categoria = st.selectbox('Categoria', CATEGORIAS)
                novo_tipo = st.selectbox('Tipo', ['Entrada', 'Saída'])
                nova_conta = st.selectbox('Conta', CONTAS)
                novo_cliente = st.text_input('Cliente/Fornecedor')
                submit_novo = st.form_submit_button('Adicionar')
                if submit_novo and nova_desc:
                    if novo_tipo == 'Saída':
                        novo_valor = -abs(novo_valor)
                    else:
                        novo_valor = abs(novo_valor)
                    save_lancamento(
                        st.session_state.user_id,
                        pd.to_datetime(nova_data),
                        novo_tipo,
                        nova_categoria,
                        novo_cliente,
                        nova_desc,
                        nova_conta,
                        novo_valor
                    )
                    st.rerun()
    
    col_export1, col_export2 = st.columns(2)
    with col_export1:
        csv_lancamentos = export_to_csv(df_filtrado)
        st.download_button(
            'Download CSV',
            csv_lancamentos,
            'lancamentos.csv',
            'text/csv'
        )
    with col_export2:
        excel_lancamentos = export_to_excel(df_filtrado)
        st.download_button(
            'Download Excel',
            excel_lancamentos,
            'lancamentos.xlsx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    st.dataframe(
        df_filtrado[['Data', 'Tipo', 'Categoria', 'Cliente/Fornecedor', 'Descrição', 'Conta', 'Valor']],
        use_container_width=True,
        hide_index=True
    )
    
    with st.expander('Excluir Lançamentos'):
        st.warning('Selecione os IDs dos lançamentos para excluir:')
        ids_para_excluir = st.multiselect('IDs', df_filtrado['id'].tolist())
        if st.button('Excluir Selecionados'):
            for id_excluir in ids_para_excluir:
                delete_lancamento(id_excluir, st.session_state.user_id)
            st.rerun()
    
    st.divider()
    
    st.header('Orçamentos')
    
    meses_disponiveis = df['Data'].dt.to_period('M').unique().astype(str).tolist()
    meses_disponiveis.sort(reverse=True)
    mes_selecionado = st.selectbox('Mês', meses_disponiveis, index=0)
    
    orcamentos = get_orcamentos(st.session_state.user_id, mes_selecionado)
    orcamentos_dict = {o.categoria: o.limite for o in orcamentos}
    
    categorias_saida = df[df['Valor'] < 0]['Categoria'].unique().tolist()
    
    with st.expander('Definir Orçamento'):
        with st.form('add_orcamento'):
            cat_orcamento = st.selectbox('Categoria', categorias_saida)
            limite_orcamento = st.number_input('Limite R$', value=0.0, step=100.0)
            submit_orcamento = st.form_submit_button('Salvar')
            if submit_orcamento and limite_orcamento > 0:
                save_orcamento(st.session_state.user_id, cat_orcamento, limite_orcamento, mes_selecionado)
                st.rerun()
    
    st.subheader(f'Orçamentos - {mes_selecionado}')
    
    alertas = []
    for cat in categorias_saida:
        gasto_cat = abs(df_filtrado[(df_filtrado['Categoria'] == cat) & (df_filtrado['Valor'] < 0)]['Valor'].sum())
        limite_cat = orcamentos_dict.get(cat, 0)
        
        if limite_cat > 0:
            pct = (gasto_cat / limite_cat) * 100
            cor = 'verde'
            if pct >= 100:
                cor = 'vermelho'
                alertas.append(f'**{cat}**: R$ {gasto_cat:,.2f} / R$ {limite_cat:,.2f} ({pct:.1f}%) - EXCEDIDO!')
            elif pct >= 80:
                cor = 'amarelo'
                alertas.append(f'**{cat}**: R$ {gasto_cat:,.2f} / R$ {limite_cat:,.2f} ({pct:.1f}%) - Atenção!')
            
            emoji = '🟢' if cor == 'verde' else ('🔴' if cor == 'vermelho' else '🟡')
            st.write(f'{emoji} {cat}: R$ {gasto_cat:,.2f} / R$ {limite_cat:,.2f} ({pct:.1f}%)')
    
    if alertas:
        st.divider()
        st.warning('**Alertas de Orçamento:**')
        for alerta in alertas:
            st.write(alerta)
    
else:
    st.info('Faça upload do extrato CSV ou Excel na barra lateral para começar.')
    st.markdown('''
    ### Formato esperado das colunas:
    - **Data**: Data no formato YYYY-MM-DD ou DD/MM/YYYY
    - **Tipo**: Entrada ou Saída
    - **Categoria**: Categoria do lançamento
    - **Cliente/Fornecedor**: Nome do cliente ou fornecedor
    - **Descrição**: Descrição do lançamento
    - **Conta**: Banco (Itau ou Inter)
    - **Valor**: Valor positivo (entrada) ou negativo (saída)
    ''')
