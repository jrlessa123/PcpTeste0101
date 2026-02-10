"""Dashboard MVP para PCP Shadow.

Executar:
    streamlit run backend/dashboard_app.py
"""

import pandas as pd
import pyodbc
import streamlit as st

from config import AppConfig
from database.connection import get_db_connection
from services.pcp_service import PCPService

st.set_page_config(page_title="PCP Shadow - MVP", layout="wide")

config = AppConfig.from_env()

EMPTY_DATA = {
    "estoque": [],
    "carteira": [],
    "ops_abertas": [],
    "estoque_negativo": [],
}


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


def load_data_or_fallback(filial: str, empresa: str):
    """Carrega dados do banco ou retorna dados vazios com mensagem de erro."""
    try:
        return load_data(filial, empresa), None
    except pyodbc.OperationalError as e:
        return EMPTY_DATA.copy(), str(e)
    except pyodbc.Error as e:
        return EMPTY_DATA.copy(), str(e)
    except Exception as e:
        return EMPTY_DATA.copy(), str(e)


st.title("PCP Shadow - Dashboard MVP")
st.caption("Leitura direta do Protheus para visibilidade rápida do PCP.")

with st.sidebar:
    st.header("Filtros")
    filial = st.text_input("Filial", value=config.filial)
    empresa = st.text_input("Empresa", value=config.empresa)
    if st.button("Atualizar"):
        st.cache_data.clear()

data, db_error = load_data_or_fallback(filial, empresa)

if db_error:
    st.error(
        "**Não foi possível conectar ao SQL Server.** O dashboard está em modo "
        "offline (dados vazios). Verifique:\n\n"
        "• SQL Server está em execução\n"
        "• Variáveis de ambiente no `.env`: `DB_SERVER`, `DB_NAME`, `DB_USER`, `DB_PASS`\n"
        "• Nome/instância do servidor correto (ex: `localhost` ou `servidor\\SQLEXPRESS`)\n"
        "• Firewall e que o SQL Server aceita conexões remotas\n\n"
        f"*Detalhe técnico:* `{db_error}`"
    )

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
