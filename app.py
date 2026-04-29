import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime, date
import os

# --- CONFIGURAÇÃO E BANCO DE DADOS ---
st.set_page_config(page_title="Controle Pré-Compras UFMG", layout="wide")

# Conexão com o banco (Railway usa a variável DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS processos (
            id SERIAL PRIMARY KEY,
            sei TEXT UNIQUE,
            objeto TEXT,
            unidade TEXT,
            responsavel TEXT,
            tipo_contratacao TEXT,
            srp TEXT,
            ir_p TEXT,
            pregao TEXT,
            valor_estimado FLOAT,
            situacao TEXT,
            datas JSONB
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# --- LÓGICA DE NEGÓCIO ---
EVENTOS = [
    "Recebimento", "Divulgação da IRP", "Transferência da IRP", "Envio para DPL",
    "Envio para Nota Técnica", "Retorno da Nota Técnica", "Atendimento NT (Solicitante)",
    "Atendimento NT (Pré-compras)", "Envio para Procuradoria", "Retorno da Procuradoria",
    "Atendimento Parecer (Solicitante)", "Atendimento Parecer (Pré-compras)",
    "Publicação do Edital", "Envio para o setor de pregão"
]

def calcular_prazos(datas_dict):
    # Converte strings de volta para data se necessário
    datas = {k: datetime.strptime(v, '%Y-%m-%d').date() for k, v in datas_dict.items() if v}
    tempos = {}
    etapa_atual = "Não iniciado"
    aberto = 0
    
    for i, nome in enumerate(EVENTOS):
        if nome in datas:
            etapa_atual = nome
            if i + 1 < len(EVENTOS):
                prox = EVENTOS[i+1]
                if prox in datas:
                    tempos[nome] = (datas[prox] - datas[nome]).days
                else:
                    aberto = (date.today() - datas[nome]).days
                    break
    return etapa_atual, aberto, tempos

# --- INTERFACE ---
init_db()

st.title("🏛️ Sistema de Gestão de Processos - UFMG")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Cadastrar Processo", "Lista de Processos"])

if menu == "Cadastrar Processo":
    st.subheader("Novo Processo SEI")
    with st.form("cadastro"):
        c1, c2 = st.columns(2)
        sei = c1.text_input("Processo SEI")
        objeto = c1.text_area("Objeto")
        unidade = c2.text_input("Unidade Demandante")
        responsavel = c2.text_input("Responsável (Pré-compras)")
        
        st.write("---")
        st.write("Insira as datas dos eventos realizados:")
        datas_col = st.columns(3)
        dict_datas = {}
        for i, ev in enumerate(EVENTOS):
            with datas_col[i % 3]:
                d = st.date_input(ev, value=None)
                dict_datas[ev] = str(d) if d else None
        
        if st.form_submit_button("Salvar"):
            # Lógica para inserir no Postgres aqui
            st.success(f"Processo {sei} salvo com sucesso!")

elif menu == "Dashboard":
    st.subheader("Análise de Gargalos e Eficiência")
    # Aqui entrarão os gráficos do Plotly baseados nos cálculos de data
    st.info("O Dashboard exibirá automaticamente os processos com mais de 10 dias em aberto.")