# queries.py (ajustado para Protheus SQL)
# ------------------------------------------------------------
# - Tabelas com sufixo de empresa (ex: SC2010, SB1010)
# - Filtro D_E_L_E_T_ = '' para registros válidos
# - Placeholders "?" compatíveis com pyodbc
# - SB1 = cadastro de produto (B1_DESC = descrição); SC5/SC6 = pedidos de venda;
#   SC2 = ordens de produção (PCP); SB2 = saldos por armazém
# ------------------------------------------------------------

from datetime import datetime, timedelta

# ---------------- Helpers ----------------
def get_table_name(prefixo: str, empresa: str = "010") -> str:
    """Retorna o nome real da tabela no SQL (ex: SB2 + 010 -> SB2010).
    Normalização: 2 dígitos -> acrescenta 0 à direita (01 -> 010); 1 dígito -> zfill 3 (1 -> 001)."""
    if not prefixo:
        raise ValueError("prefixo inválido")
    empresa = (empresa or "").strip()
    if not empresa.isdigit():
        raise ValueError("empresa inválida")
    if len(empresa) == 2:
        empresa = empresa + "0"   # 01 -> 010, 02 -> 020
    elif len(empresa) == 1:
        empresa = empresa.zfill(3)  # 1 -> 001
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
    tb_sb1 = get_table_name("SB1", empresa)
    # SB1 pode ter cadastro por filial ou único (B1_FILIAL vazio); preferir um registro por B1_COD
    return f"""
    SELECT
        B2.B2_COD AS CodigoProduto,
        RTRIM(ISNULL(B1.B1_DESC, '')) AS DescricaoProduto,
        B2.B2_QATU AS EstoqueAtual,
        B2.B2_RESERVA AS QuantidadeReservada,
        (B2.B2_QATU - B2.B2_RESERVA) AS SaldoDisponivel,
        B2.B2_LOCAL AS Armazem
    FROM {tb_sb2} B2
    LEFT JOIN (
        SELECT B1_COD, B1_DESC,
               ROW_NUMBER() OVER (PARTITION BY B1_COD ORDER BY CASE WHEN RTRIM(ISNULL(B1_FILIAL,'')) = '' THEN 0 ELSE 1 END) AS rn
        FROM {tb_sb1}
        WHERE D_E_L_E_T_ = ''
    ) B1 ON B1.B1_COD = B2.B2_COD AND B1.rn = 1
    WHERE B2.B2_FILIAL = ?
      AND B2.D_E_L_E_T_ = ''
    ORDER BY B2.B2_COD
    """

def get_pedidos_carteira_query(empresa: str = "010"):
    """Carteira de pedidos: saldo a entregar com amarrações (vendedor, romaneio/carga DAI/DAK, NF).
    Coleta e Entrega (TOTVS): DAI=itens da carga, DAK=cargas; DAI_DTCHEG=data chegada; DAK_FEZNF=gerou NF.
    StatusEntrega: Pendente | Com romaneio/carga | NF emitida | Entrega realizada."""
    tb_sc5 = get_table_name("SC5", empresa)
    tb_sc6 = get_table_name("SC6", empresa)
    tb_sb1 = get_table_name("SB1", empresa)
    tb_sa3 = get_table_name("SA3", empresa)
    tb_dai = get_table_name("DAI", empresa)
    return f"""
    SELECT
        C6.C6_NUM AS NumeroPedido,
        RTRIM(ISNULL(C5.C5_VEND, '')) AS CodigoVendedor,
        RTRIM(ISNULL(A3.A3_NOME, '')) AS NomeVendedor,
        C5.C5_CLIENTE AS CodigoCliente,
        RTRIM(ISNULL(C5.C5_NOMECLI, '')) AS NomeCliente,
        C6.C6_PRODUTO AS CodigoProduto,
        RTRIM(ISNULL(B1.B1_DESC, C6.C6_DESCRI)) AS DescricaoProduto,
        C6.C6_QTDVEN AS QuantidadeVendida,
        ISNULL(C6.C6_QTDENT, 0) AS QuantidadeEntregue,
        (C6.C6_QTDVEN - ISNULL(C6.C6_QTDENT, 0)) AS SaldoAEntregar,
        C6.C6_ENTREG AS DataEntregaPrevista,
        CASE WHEN RTRIM(ISNULL(C6.C6_NOTA, '')) <> '' THEN 1 ELSE 0 END AS TemNF,
        RTRIM(ISNULL(C6.C6_NOTA, '')) AS NumeroNF,
        RTRIM(ISNULL(C6.C6_SERIE, '')) AS SerieNF,
        CASE WHEN EXISTS (SELECT 1 FROM {tb_dai} d WHERE d.DAI_FILIAL = C6.C6_FILIAL AND d.DAI_PEDIDO = C6.C6_NUM AND d.D_E_L_E_T_ = '') THEN 1 ELSE 0 END AS TemRomaneioCarga,
        CASE
            WHEN EXISTS (SELECT 1 FROM {tb_dai} d WHERE d.DAI_FILIAL = C6.C6_FILIAL AND d.DAI_PEDIDO = C6.C6_NUM AND d.D_E_L_E_T_ = '' AND d.DAI_DTCHEG IS NOT NULL) THEN 'Entrega realizada'
            WHEN RTRIM(ISNULL(C6.C6_NOTA, '')) <> '' THEN 'NF emitida'
            WHEN EXISTS (SELECT 1 FROM {tb_dai} d WHERE d.DAI_FILIAL = C6.C6_FILIAL AND d.DAI_PEDIDO = C6.C6_NUM AND d.D_E_L_E_T_ = '') THEN 'Com romaneio/carga'
            ELSE 'Pendente'
        END AS StatusEntrega,
        CASE WHEN ISNULL(C6.C6_QTDENT, 0) > 0 AND ISNULL(C6.C6_QTDENT, 0) < C6.C6_QTDVEN THEN 1 ELSE 0 END AS EntregaParcial
    FROM {tb_sc6} C6
    INNER JOIN {tb_sc5} C5
        ON C6.C6_FILIAL = C5.C5_FILIAL
       AND C6.C6_NUM = C5.C5_NUM
       AND C5.D_E_L_E_T_ = ''
    LEFT JOIN {tb_sa3} A3 ON A3.A3_FILIAL = C5.C5_FILIAL AND A3.A3_COD = C5.C5_VEND AND A3.D_E_L_E_T_ = ''
    LEFT JOIN (
        SELECT B1_COD, B1_DESC,
               ROW_NUMBER() OVER (PARTITION BY B1_COD ORDER BY CASE WHEN RTRIM(ISNULL(B1_FILIAL,'')) = '' THEN 0 ELSE 1 END) AS rn
        FROM {tb_sb1}
        WHERE D_E_L_E_T_ = ''
    ) B1 ON B1.B1_COD = C6.C6_PRODUTO AND B1.rn = 1
    WHERE C6.C6_FILIAL = ?
      AND C6.D_E_L_E_T_ = ''
      AND (C6.C6_QTDENT < C6.C6_QTDVEN OR (C6.C6_QTDENT IS NULL AND C6.C6_QTDVEN > 0))
      AND (C6.C6_BLQ IS NULL OR (C6.C6_BLQ <> 'R' AND C6.C6_BLQ <> 'S'))
    ORDER BY C6.C6_ENTREG, C6.C6_NUM
    """

def get_ops_em_aberto_query(empresa: str = "010"):
    """OPs em aberto com status descritivo e indicadores de apontamento (parcial/total).
    C2_STATUS: N=Liberada, E=Encerrada, U=Outros; QUJE=quantidade já produzida (apontada)."""
    tb_sc2 = get_table_name("SC2", empresa)
    tb_sb1 = get_table_name("SB1", empresa)
    return f"""
    SELECT
        C2.C2_NUM AS NumeroOP,
        C2.C2_PRODUTO AS CodigoProduto,
        RTRIM(ISNULL(B1.B1_DESC, '')) AS DescricaoProduto,
        C2.C2_DATPRI AS DataInicio,
        C2.C2_DATPRF AS DataFim,
        C2.C2_QUANT AS QuantidadeOriginal,
        C2.C2_QUJE AS QuantidadeProduzida,
        (C2.C2_QUANT - C2.C2_QUJE) AS QuantidadePendente,
        C2.C2_STATUS AS StatusOP,
        CASE RTRIM(ISNULL(C2.C2_STATUS, ''))
            WHEN 'N' THEN 'Liberada'
            WHEN 'E' THEN 'Encerrada'
            WHEN 'U' THEN 'Em produção'
            ELSE 'Outros'
        END AS StatusOPDescricao,
        CASE WHEN C2.C2_QUJE > 0 AND C2.C2_QUJE < C2.C2_QUANT THEN 1 ELSE 0 END AS ApontadoParcial,
        CASE WHEN C2.C2_QUJE >= C2.C2_QUANT THEN 1 ELSE 0 END AS ApontadoTotal
    FROM {tb_sc2} C2
    LEFT JOIN (
        SELECT B1_COD, B1_DESC,
               ROW_NUMBER() OVER (PARTITION BY B1_COD ORDER BY CASE WHEN RTRIM(ISNULL(B1_FILIAL,'')) = '' THEN 0 ELSE 1 END) AS rn
        FROM {tb_sb1}
        WHERE D_E_L_E_T_ = ''
    ) B1 ON B1.B1_COD = C2.C2_PRODUTO AND B1.rn = 1
    WHERE C2.C2_FILIAL = ?
      AND C2.D_E_L_E_T_ = ''
      AND C2.C2_QUANT > C2.C2_QUJE
    ORDER BY C2.C2_DATPRF, C2.C2_PRODUTO
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
    tb_sb1 = get_table_name("SB1", empresa)
    return f"""
    SELECT
        B2.B2_COD AS CodigoProduto,
        RTRIM(ISNULL(B1.B1_DESC, '')) AS DescricaoProduto,
        B2.B2_QATU AS EstoqueAtual,
        B2.B2_LOCAL AS Armazem
    FROM {tb_sb2} B2
    LEFT JOIN (
        SELECT B1_COD, B1_DESC,
               ROW_NUMBER() OVER (PARTITION BY B1_COD ORDER BY CASE WHEN RTRIM(ISNULL(B1_FILIAL,'')) = '' THEN 0 ELSE 1 END) AS rn
        FROM {tb_sb1}
        WHERE D_E_L_E_T_ = ''
    ) B1 ON B1.B1_COD = B2.B2_COD AND B1.rn = 1
    WHERE B2.B2_FILIAL = ?
      AND B2.D_E_L_E_T_ = ''
      AND B2.B2_QATU < 0
    ORDER BY B2.B2_QATU, B2.B2_COD
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
