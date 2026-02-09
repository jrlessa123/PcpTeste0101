# queries.py (ajustado para Protheus SQL)
# ------------------------------------------------------------
# - Tabelas com sufixo de empresa (ex: SC2010)
# - Filtro D_E_L_E_T_ = '' para registros válidos
# - Placeholders "?" compatíveis com pyodbc
# ------------------------------------------------------------

from datetime import datetime, timedelta

# ---------------- Helpers ----------------
def get_table_name(prefixo: str, empresa: str = "010") -> str:
    """Retorna o nome real da tabela no SQL (ex: SB2 + 010 -> SB2010)."""
    if not prefixo:
        raise ValueError("prefixo inválido")
    empresa = (empresa or "").strip()
    if not empresa.isdigit():
        raise ValueError("empresa inválida")
    return f"{prefixo}{empresa}"

def _periodo_yyyymmdd(dias: int):
    """Retorna (inicio, fim) como 'YYYYMMDD' para os últimos 'dias'."""
    fim = datetime.now()
    ini = fim - timedelta(days=int(dias))
    return ini.strftime("%Y%m%d"), fim.strftime("%Y%m%d")

def _valida_filial(filial: str) -> str:
    """Garante que a filial esteja no formato esperado (2 a 4 dígitos)."""
    if not isinstance(filial, str):
        raise ValueError("filial deve ser string")
    f = filial.strip()
    if not f.isdigit() or len(f) > 4:
        raise ValueError("filial inválida")
    return f.zfill(len(f))

# ---------------- Consultas ----------------

def get_estoque_query(empresa: str = "010"):
    tb_sb2 = get_table_name("SB2", empresa)
    return f"""
    SELECT
        B2_COD AS CodigoProduto,
        B2_QATU AS EstoqueAtual,
        B2_RESERVA AS QuantidadeReservada,
        (B2_QATU - B2_RESERVA) AS SaldoDisponivel,
        B2_LOCAL AS Armazem
    FROM {tb_sb2}
    WHERE B2_FILIAL = ?
      AND D_E_L_E_T_ = ''
    ORDER BY B2_COD
    """

def get_pedidos_carteira_query(empresa: str = "010"):
    tb_sc5 = get_table_name("SC5", empresa)
    tb_sc6 = get_table_name("SC6", empresa)
    return f"""
    SELECT
        C6.C6_NUM AS NumeroPedido,
        C5.C5_CLIENTE AS CodigoCliente,
        C5.C5_NOMECLI AS NomeCliente,
        C6.C6_PRODUTO AS CodigoProduto,
        C6.C6_QTDVEN AS QuantidadeVendida,
        C6.C6_QTDENT AS QuantidadeEntregue,
        (C6.C6_QTDVEN - C6.C6_QTDENT) AS SaldoAEntregar,
        C6.C6_ENTREGA AS DataEntregaPrevista
    FROM {tb_sc6} C6
    INNER JOIN {tb_sc5} C5
        ON C6.C6_FILIAL = C5.C5_FILIAL
       AND C6.C6_NUM = C5.C5_NUM
       AND C5.D_E_L_E_T_ = ''
    WHERE C6.C6_FILIAL = ?
      AND C6.D_E_L_E_T_ = ''
      AND C6.C6_QTDENT < C6.C6_QTDVEN
      AND C6.C6_BLQ <> 'R'
    ORDER BY C6.C6_ENTREGA
    """

def get_ops_em_aberto_query(empresa: str = "010"):
    tb_sc2 = get_table_name("SC2", empresa)
    return f"""
    SELECT
        C2_NUM AS NumeroOP,
        C2_PRODUTO AS CodigoProduto,
        C2_DATPRI AS DataInicio,
        C2_DATPRF AS DataFim,
        C2_QUANT AS QuantidadeOriginal,
        C2_QUJE AS QuantidadeProduzida,
        (C2_QUANT - C2_QUJE) AS QuantidadePendente,
        C2_STATUS AS StatusOP
    FROM {tb_sc2}
    WHERE C2_FILIAL = ?
      AND D_E_L_E_T_ = ''
      AND C2_QUANT > C2_QUJE
    ORDER BY C2_DATPRF, C2_PRODUTO
    """

def get_necessidade_materia_prima_query(empresa: str = "010"):
    tb_sd4 = get_table_name("SD4", empresa)
    return f"""
    SELECT
        D4_PRODUTO AS CodigoProduto,
        D4_OP AS NumeroOP,
        D4_QTNECES AS QuantidadeNecessaria,
        D4_LOCAL AS Local,
        D4_LOTECTL AS ControleLote,
        D4_NUMLOTE AS NumeroLote
    FROM {tb_sd4}
    WHERE D4_FILIAL = ?
      AND D_E_L_E_T_ = ''
      AND D4_QTNECES > 0
    ORDER BY D4_PRODUTO
    """

def get_ops_detalhado_query(empresa: str = "010"):
    tb_sc2 = get_table_name("SC2", empresa)
    return f"""
    SELECT
        C2_NUM AS NumeroOP,
        C2_PRODUTO AS CodigoProduto,
        C2_DATPRI AS DataInicio,
        C2_DATPRF AS DataFim,
        C2_QUANT AS QuantidadeOriginal,
        C2_QUJE AS QuantidadeProduzida,
        (C2_QUANT - C2_QUJE) AS QuantidadePendente,
        C2_STATUS AS StatusOP,
        C2_OBS AS Observacao
    FROM {tb_sc2}
    WHERE C2_FILIAL = ?
      AND D_E_L_E_T_ = ''
    ORDER BY C2_NUM
    """

def get_estoque_negativo_justificativa_query(empresa: str = "010"):
    tb_sb2 = get_table_name("SB2", empresa)
    return f"""
    SELECT
        B2_COD AS CodigoProduto,
        B2_QATU AS EstoqueAtual,
        B2_LOCAL AS Armazem
    FROM {tb_sb2}
    WHERE B2_FILIAL = ?
      AND D_E_L_E_T_ = ''
      AND B2_QATU < 0
    ORDER BY B2_COD
    """

def get_empenho_pendente_op_encerrada_query(empresa: str = "010"):
    tb_sc7 = get_table_name("SC7", empresa)
    return f"""
    SELECT
        C7_PRODUTO AS CodigoProduto,
        C7_QUANT AS QuantidadeEmpenhada,
        C7_OP AS NumeroOP,
        C7_NUM AS NumeroPedido,
        C7_DATPRF AS DataEntrega
    FROM {tb_sc7}
    WHERE C7_FILIAL = ?
      AND D_E_L_E_T_ = ''
      AND C7_OP IS NOT NULL
      AND C7_QUANT > 0
    ORDER BY C7_PRODUTO
    """

def get_ops_parcialmente_encerradas_query(empresa: str = "010"):
    tb_sc2 = get_table_name("SC2", empresa)
    return f"""
    SELECT
        C2_NUM AS NumeroOP,
        C2_PRODUTO AS CodigoProduto,
        C2_QUANT AS QuantidadeOriginal,
        C2_QUJE AS QuantidadeProduzida,
        (C2_QUANT - C2_QUJE) AS QuantidadePendente
    FROM {tb_sc2}
    WHERE C2_FILIAL = ?
      AND D_E_L_E_T_ = ''
      AND C2_QUJE > 0
      AND C2_QUJE < C2_QUANT
    ORDER BY C2_NUM
    """

def get_ops_encerradas_sem_consumo_query(empresa: str = "010"):
    tb_sc2 = get_table_name("SC2", empresa)
    tb_sd3 = get_table_name("SD3", empresa)
    return f"""
    SELECT
        C2.C2_NUM AS NumeroOP,
        C2.C2_PRODUTO AS CodigoProduto,
        C2.C2_DATPRF AS DataFim,
        C2.C2_QUJE AS QuantidadeProduzida
    FROM {tb_sc2} C2
    LEFT JOIN {tb_sd3} D3
        ON D3.D3_FILIAL = C2.C2_FILIAL
       AND D3.D3_OP = C2.C2_NUM
       AND D3.D_E_L_E_T_ = ''
    WHERE C2.C2_FILIAL = ?
      AND C2.D_E_L_E_T_ = ''
      AND C2.C2_STATUS = 'E'
      AND D3.D3_OP IS NULL
    ORDER BY C2.C2_DATPRF
    """
