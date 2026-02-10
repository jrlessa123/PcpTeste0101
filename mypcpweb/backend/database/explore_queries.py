# explore_queries.py - Consultas TOP 10 para explorar estrutura e índices das tabelas Protheus
# -----------------------------------------------------------------------------------------
# Use para: (1) ver amostra de dados e nomes reais de colunas; (2) validar B1_DESC/B1_FILIAL;
#          (3) entender vínculo pedido -> NF (C6_NOTA, SF2, SD2) e entrega/romaneio.
# Execução: python -m backend.run_explore (a partir da pasta mypcpweb)
# -----------------------------------------------------------------------------------------

from .queries import get_table_name


def _top(empresa: str, table_prefix: str, columns: str, where: str = "", order: str = "") -> str:
    tb = get_table_name(table_prefix, empresa)
    where_cl = f" WHERE {where}" if where else ""
    order_cl = f" ORDER BY {order}" if order else ""
    return f"SELECT TOP 10 {columns} FROM {tb}{where_cl}{order_cl}"


def get_top10_sb1(empresa: str = "010") -> str:
    """Produto: ver B1_FILIAL, B1_COD, B1_DESC (e variantes B1_DESCRI se existir)."""
    tb = get_table_name("SB1", empresa)
    return f"""SELECT TOP 10 B1_FILIAL, B1_COD, B1_DESC, B1_UM, D_E_L_E_T_
FROM {tb}
WHERE D_E_L_E_T_ = ''
ORDER BY B1_COD"""


def get_top10_sb2(empresa: str = "010") -> str:
    """Saldos por armazém: B2_FILIAL, B2_COD, B2_QATU, B2_LOCAL."""
    tb = get_table_name("SB2", empresa)
    return f"""SELECT TOP 10 B2_FILIAL, B2_COD, B2_QATU, B2_RESERVA, B2_LOCAL, D_E_L_E_T_
FROM {tb}
WHERE D_E_L_E_T_ = ''
ORDER BY B2_COD"""


def get_top10_sc2(empresa: str = "010") -> str:
    """Ordens de produção (PCP): C2_FILIAL, C2_NUM, C2_PRODUTO, C2_QUANT, C2_QUJE, C2_STATUS."""
    tb = get_table_name("SC2", empresa)
    return f"""SELECT TOP 10 C2_FILIAL, C2_NUM, C2_PRODUTO, C2_QUANT, C2_QUJE, C2_STATUS, C2_DATPRI, C2_DATPRF, D_E_L_E_T_
FROM {tb}
WHERE D_E_L_E_T_ = ''
ORDER BY C2_NUM DESC"""


def get_top10_sc5(empresa: str = "010") -> str:
    """Cabeçalho pedido de venda: C5_FILIAL, C5_NUM, C5_VEND (vendedor), C5_CLIENTE, C5_NOMECLI."""
    tb = get_table_name("SC5", empresa)
    return f"""SELECT TOP 10 C5_FILIAL, C5_NUM, C5_VEND, C5_CLIENTE, C5_NOMECLI, C5_EMISSAO, C5_CONDPAG, D_E_L_E_T_
FROM {tb}
WHERE D_E_L_E_T_ = ''
ORDER BY C5_NUM DESC"""


def get_top10_sc6(empresa: str = "010") -> str:
    """Itens pedido de venda: C6_NUM, C6_PRODUTO, C6_QTDVEN, C6_QTDENT, C6_ENTREG/C6_ENTREGA, C6_NOTA, C6_BLQ, C6_DESCRI."""
    tb = get_table_name("SC6", empresa)
    return f"""SELECT TOP 10 C6_FILIAL, C6_NUM, C6_ITEM, C6_PRODUTO, C6_DESCRI, C6_QTDVEN, C6_QTDENT, C6_ENTREG, C6_NOTA, C6_SERIE, C6_BLQ, D_E_L_E_T_
FROM {tb}
WHERE D_E_L_E_T_ = ''
ORDER BY C6_NUM DESC, C6_ITEM"""


def get_top10_sf2(empresa: str = "010") -> str:
    """Cabeçalho NF de saída: F2_DOC, F2_SERIE, F2_CLIENTE, F2_EMISSAO, status (F2_ZSTATUS ou similar)."""
    tb = get_table_name("SF2", empresa)
    return f"""SELECT TOP 10 F2_FILIAL, F2_DOC, F2_SERIE, F2_CLIENTE, F2_LOJA, F2_EMISSAO, F2_VALBRUT, D_E_L_E_T_
FROM {tb}
WHERE D_E_L_E_T_ = ''
ORDER BY F2_EMISSAO DESC"""


def get_top10_sd2(empresa: str = "010") -> str:
    """Itens NF de saída: D2_DOC, D2_SERIE, D2_PEDIDO, D2_COD (produto), D2_QUANT, vínculo com pedido."""
    tb = get_table_name("SD2", empresa)
    return f"""SELECT TOP 10 D2_FILIAL, D2_DOC, D2_SERIE, D2_PEDIDO, D2_ITEM, D2_COD, D2_QUANT, D2_TOTAL, D_E_L_E_T_
FROM {tb}
WHERE D_E_L_E_T_ = ''
ORDER BY D2_DOC DESC, D2_ITEM"""


def get_top10_sa1(empresa: str = "010") -> str:
    """Clientes: A1_FILIAL, A1_COD, A1_NOME."""
    tb = get_table_name("SA1", empresa)
    return f"""SELECT TOP 10 A1_FILIAL, A1_COD, A1_LOJA, A1_NOME, A1_END, D_E_L_E_T_
FROM {tb}
WHERE D_E_L_E_T_ = ''
ORDER BY A1_COD"""


def get_top10_sa3(empresa: str = "010") -> str:
    """Vendedores: A3_FILIAL, A3_COD, A3_NOME (para amarrar C5_VEND)."""
    tb = get_table_name("SA3", empresa)
    return f"""SELECT TOP 10 A3_FILIAL, A3_COD, A3_NOME, D_E_L_E_T_
FROM {tb}
WHERE D_E_L_E_T_ = ''
ORDER BY A3_COD"""


def get_top10_dai(empresa: str = "010") -> str:
    """Itens da carga (Coleta e Entrega): DAI_PEDIDO, DAI_DTCHEG (chegada), vínculo com pedido."""
    tb = get_table_name("DAI", empresa)
    return f"""SELECT TOP 10 DAI_FILIAL, DAI_COD, DAI_SEQCAR, DAI_PEDIDO, DAI_CLIENT, DAI_VENDED, DAI_NFISCA, DAI_DTCHEG, D_E_L_E_T_
FROM {tb}
WHERE D_E_L_E_T_ = ''
ORDER BY DAI_PEDIDO DESC"""


def get_top10_dak(empresa: str = "010") -> str:
    """Cargas (Coleta e Entrega): DAK_COD, DAK_FEZNF (gerou NF), DAK_ACECAR (acerto carga)."""
    tb = get_table_name("DAK", empresa)
    return f"""SELECT TOP 10 DAK_FILIAL, DAK_COD, DAK_SEQCAR, DAK_DATA, DAK_FEZNF, DAK_ACECAR, DAK_DATENT, D_E_L_E_T_
FROM {tb}
WHERE D_E_L_E_T_ = ''
ORDER BY DAK_DATA DESC"""


def get_all_explore_queries(empresa: str = "010"):
    """Retorna lista de (nome, sql) para execução no explorador."""
    return [
        ("SB1 (Produto)", get_top10_sb1(empresa)),
        ("SB2 (Estoque)", get_top10_sb2(empresa)),
        ("SC2 (OPs)", get_top10_sc2(empresa)),
        ("SC5 (Pedido cabeçalho)", get_top10_sc5(empresa)),
        ("SC6 (Pedido itens)", get_top10_sc6(empresa)),
        ("SF2 (NF Saída cabeçalho)", get_top10_sf2(empresa)),
        ("SD2 (NF Saída itens)", get_top10_sd2(empresa)),
        ("SA1 (Cliente)", get_top10_sa1(empresa)),
        ("SA3 (Vendedor)", get_top10_sa3(empresa)),
        ("DAI (Itens da Carga / Romaneio)", get_top10_dai(empresa)),
        ("DAK (Cargas)", get_top10_dak(empresa)),
    ]
