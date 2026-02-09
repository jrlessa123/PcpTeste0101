"""Dashboard MVP para PCP Shadow.

Executar:
    streamlit run backend/dashboard_app.py
"""

import os

import pandas as pd
import streamlit as st
import pyodbc

from services.pcp_service import PCPService

st.set_page_config(page_title="PCP Shadow - MVP", layout="wide")

DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_SERVER = os.getenv("DB_SERVER", "192.168.163.20")
DB_NAME = os.getenv("DB_NAME", "PROTHEUS11")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASS = os.getenv("DB_PASS", "Flamb@2014")

DEFAULT_FILIAL = os.getenv("FILIAL", "01")
DEFAULT_EMPRESA = os.getenv("EMPRESA", "010")

def get_db_connection():
    cnxn_str = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USER};"
        f"PWD={DB_PASS};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(cnxn_str)

@st.cache_data(ttl=60)
def load_data(filial: str, empresa: str):
    cnxn = get_db_connection()
    service = PCPService(cnxn, filial=filial, empresa=empresa)
    return {
        "estoque": service.get_estoque(),
        "carteira": service.get_pedidos_carteira(),
        "ops_abertas": service.get_ops_em_aberto(),
        "estoque_negativo": service.get_estoque_negativo_justificativa(),
    }

st.title("PCP Shadow - Dashboard MVP")
st.caption("Leitura direta do Protheus para visibilidade rápida do PCP.")

with st.sidebar:
    st.header("Filtros")
    filial = st.text_input("Filial", value=DEFAULT_FILIAL)
    empresa = st.text_input("Empresa", value=DEFAULT_EMPRESA)
    if st.button("Atualizar"):
        st.cache_data.clear()

data = load_data(filial, empresa)

tab_estoque, tab_carteira, tab_ops, tab_alertas = st.tabs(
    ["Estoque", "Carteira", "OPs em Aberto", "Alertas"]
)

with tab_estoque:
    st.subheader("Estoque")
    st.dataframe(pd.DataFrame(data["estoque"]))

with tab_carteira:
    st.subheader("Pedidos em Carteira")
    st.dataframe(pd.DataFrame(data["carteira"]))

with tab_ops:
    st.subheader("Ordens de Produção em Aberto")
    st.dataframe(pd.DataFrame(data["ops_abertas"]))

with tab_alertas:
    st.subheader("Alertas rápidos")
    st.write("Estoque negativo")
    st.dataframe(pd.DataFrame(data["estoque_negativo"]))
