import streamlit as st
import sqlite3
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DE INFRAESTRUTURA E PERSISTÊNCIA ---

DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "chamado.db")

# Assegura a existência do diretório para o banco de dados
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

def criar_tabela():
    """Inicializa a tabela tbl_chamados com a estrutura técnica especificada."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_chamados (
            numero INTEGER PRIMARY KEY AUTOINCREMENT,
            solicitante TEXT NOT NULL,
            assunto TEXT NOT NULL,
            descricao TEXT NOT NULL,
            categoria TEXT,
            prioridade TEXT,
            status TEXT DEFAULT 'Aberto',
            data DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def salvar_chamado(solicitante, assunto, descricao, categoria, prioridade):
    """Executa a inserção de um novo registro na base de dados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tbl_chamados (solicitante, assunto, descricao, categoria, prioridade)
        VALUES (?, ?, ?, ?, ?)
    ''', (solicitante, assunto, descricao, categoria, prioridade))
    conn.commit()
    conn.close()

def ler_chamados():
    """Recupera todos os registros ordenados pelo identificador decrescente."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM tbl_chamados ORDER BY numero DESC", conn)
    conn.close()
    return df

# Inicialização do banco de dados
criar_tabela()

# --- 2. CONFIGURAÇÕES DA INTERFACE E NAVEGAÇÃO ---

st.set_page_config(page_title="Sistema de Chamados", layout="wide", page_icon="🎫")

if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = 'Home'

def mudar_pagina(nome_pagina):
    st.session_state.pagina_atual = nome_pagina

# --- 3. BARRA LATERAL (MENU DE NAVEGAÇÃO) ---

with st.sidebar:
    st.title("🎫 Menu Principal")
    st.write("Selecione a operação desejada:")
    
    if st.button("🏠 Home", use_container_width=True):
        mudar_pagina('Home')
    if st.button("➕ Abrir Chamado", use_container_width=True):
        mudar_pagina('Abrir Chamado')
    if st.button("📋 Meus Chamados", use_container_width=True):
        mudar_pagina('Lista')
    if st.button("📊 Dashboard", use_container_width=True):
        mudar_pagina('Dashboard')
    
    st.divider()
    st.caption(f"Status do DB: Conectado")
    st.caption(f"Caminho: {DB_PATH}")

# --- 4. FUNÇÕES DE RENDERIZAÇÃO DE PÁGINAS ---

def render_home():
    st.header("🏠 Página Inicial - Visão Geral")
    df = ler_chamados()
    
    col1, col2, col3 = st.columns(3)
    abertos = len(df[df['status'] == 'Aberto'])
    concluidos = len(df[df['status'] == 'Concluído'])
    
    col1.metric("Chamados Ativos", abertos, delta_color="inverse")
    col2.metric("Concluídos", concluidos)
    col3.metric("Total de Registros", len(df))
    
    st.info("Utilize o menu lateral para gerenciar as requisições técnicas.")

def render_abrir_chamado():
    st.header("🚀 Abertura de Novo Chamado")
    
    with st.form("form_chamado", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        
        with col_a:
            solicitante = st.text_input("Solicitante", placeholder="Nome completo do colaborador")
            assunto = st.text_input("Assunto", placeholder="Resumo do problema")
        
        with col_b:
            categoria = st.selectbox(
                "Categoria", 
                ["Acesso", "Erro", "Criação de Usuário", "Alteração"]
            )
            prioridade = st.select_slider(
                "Prioridade", 
                options=["Baixa", "Média", "Alta", "Crítica"]
            )
            
        descricao = st.text_area("Descrição Detalhada", placeholder="Descreva o incidente ou solicitação com detalhes técnicos.")
        
        st.divider()
        enviado = st.form_submit_button("Registrar Chamado")
        
        if enviado:
            if solicitante and assunto and descricao:
                salvar_chamado(solicitante, assunto, descricao, categoria, prioridade)
                st.success(f"✅ Chamado registrado com sucesso para: {solicitante}")
                st.balloons()
            else:
                st.error("⚠️ Erro: Todos os campos obrigatórios (*Solicitante, Assunto, Descrição*) devem ser preenchidos.")

def render_lista_chamados():
    st.header("📋 Lista de Chamados Ativos")
    df = ler_chamados()
    
    if not df.empty:
        # Renomeação para melhor legibilidade na interface
        df_display = df.rename(columns={
            'numero': 'ID',
            'solicitante': 'Solicitante',
            'assunto': 'Assunto',
            'categoria': 'Categoria',
            'descricao': 'Descrição',
            'prioridade': 'Prioridade',
            'status': 'Status',
            'data': 'Data de Abertura'
        })
        
        # Filtro rápido por status
        filtro_status = st.multiselect("Filtrar por Status:", options=df_display['Status'].unique(), default=df_display['Status'].unique())
        df_filtrado = df_display[df_display['Status'].isin(filtro_status)]
        
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum chamado encontrado na base de dados.")

def render_dashboard():
    st.header("📊 Análise Estatística")
    df = ler_chamados()
    
    if not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Chamados por Categoria")
            st.bar_chart(df['categoria'].value_counts())
            
        with col2:
            st.subheader("Volume por Prioridade")
            st.line_chart(df['prioridade'].value_counts())
    else:
        st.info("Dados insuficientes para gerar volumetria.")

# --- 5. ROTEADOR DE PÁGINAS ---

if st.session_state.pagina_atual == 'Home':
    render_home()
elif st.session_state.pagina_atual == 'Abrir Chamado':
    render_abrir_chamado()
elif st.session_state.pagina_atual == 'Lista':
    render_lista_chamados()
elif st.session_state.pagina_atual == 'Dashboard':
    render_dashboard()
