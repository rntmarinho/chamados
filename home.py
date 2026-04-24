import streamlit as st
import sqlite3
import pandas as pd

# --- 1. CAMADA DE PERSISTÊNCIA (BANCO DE DADOS) ---

def criar_tabela():
    conn = sqlite3.connect('chamados.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assunto TEXT NOT NULL,
            categoria TEXT,
            descricao TEXT,
            prioridade TEXT,
            status TEXT DEFAULT 'Aberto',
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def salvar_chamado(assunto, categoria, descricao, prioridade):
    conn = sqlite3.connect('chamados.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chamados (assunto, categoria, descricao, prioridade)
        VALUES (?, ?, ?, ?)
    ''', (assunto, categoria, descricao, prioridade))
    conn.commit()
    conn.close()

def ler_chamados():
    conn = sqlite3.connect('chamados.db')
    df = pd.read_sql_query("SELECT * FROM chamados ORDER BY id DESC", conn)
    conn.close()
    return df

# Inicialização do banco de dados
criar_tabela()

# --- 2. CONFIGURAÇÕES DA INTERFACE ---

st.set_page_config(page_title="Sistema de Chamados", layout="wide")

if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = 'Home'

def mudar_pagina(nome_pagina):
    st.session_state.pagina_atual = nome_pagina

# --- 3. BARRA LATERAL (NAVEGAÇÃO) ---

with st.sidebar:
    st.title("🎫 Menu Principal")
    if st.button("🏠 Home", use_container_width=True):
        mudar_pagina('Home')
    if st.button("➕ Abrir Chamado", use_container_width=True):
        mudar_pagina('Abrir Chamado')
    if st.button("📋 Meus Chamados", use_container_width=True):
        mudar_pagina('Lista')
    if st.button("📊 Dashboard", use_container_width=True):
        mudar_pagina('Dashboard')
    st.divider()
    st.caption("v1.1.0 - SQLite Integrado")

# --- 4. FUNÇÕES DE RENDERIZAÇÃO ---

def render_home():
    st.header("Bem-vindo ao Sistema de Chamados")
    df = ler_chamados()
    
    col1, col2, col3 = st.columns(3)
    abertos = len(df[df['status'] == 'Aberto'])
    concluidos = len(df[df['status'] == 'Concluído'])
    
    col1.metric("Chamados Ativos", abertos)
    col2.metric("Concluídos", concluidos)
    col3.metric("Total Geral", len(df))

def render_abrir_chamado():
    st.header("🚀 Abrir Novo Chamado")
    with st.form("form_chamado", clear_on_submit=True):
        titulo = st.text_input("Assunto do Chamado")
        categoria = st.selectbox("Categoria", ["Hardware", "Software", "Redes", "Acessos"])
        descricao = st.text_area("Descrição detalhada")
        prioridade = st.select_slider("Prioridade", options=["Baixa", "Média", "Alta", "Crítica"])
        
        enviado = st.form_submit_button("Registrar Chamado")
        if enviado:
            if titulo and descricao:
                salvar_chamado(titulo, categoria, descricao, prioridade)
                st.success("Chamado registrado com sucesso no banco de dados!")
            else:
                st.error("Preencha todos os campos obrigatórios.")

def render_lista_chamados():
    st.header("📋 Lista de Chamados Ativos")
    df = ler_chamados()
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum registro encontrado.")

def render_dashboard():
    st.header("📊 Análise de Dados")
    df = ler_chamados()
    if not df.empty:
        st.bar_chart(df['categoria'].value_counts())
    else:
        st.info("Dados insuficientes para gerar gráficos.")

# --- 5. ROTEADOR ---

if st.session_state.pagina_atual == 'Home':
    render_home()
elif st.session_state.pagina_atual == 'Abrir Chamado':
    render_abrir_chamado()
elif st.session_state.pagina_atual == 'Lista':
    render_lista_chamados()
elif st.session_state.pagina_atual == 'Dashboard':
    render_dashboard()
