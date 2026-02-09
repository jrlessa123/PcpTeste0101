"""Dashboard MVP para PCP Shadow.

Executar:
    streamlit run backend/dashboard_app.py
"""

import pandas as pd
import streamlit as st

from config import AppConfig
from database.connection import get_db_connection
from services.pcp_service import PCPService

st.set_page_config(page_title="PCP Shadow - MVP", layout="wide")

config = AppConfig.from_env()

@st.cache_data(ttl=60)
def load_data(filial: str, empresa: str):
    cnxn = get_db_connection(config)
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
    filial = st.text_input("Filial", value=config.filial)
    empresa = st.text_input("Empresa", value=config.empresa)
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
