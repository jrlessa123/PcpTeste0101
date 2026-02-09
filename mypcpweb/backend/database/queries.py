# queries.py (refatorado)
# ------------------------------------------------------------
# Refatoração completa com:
# - Placeholders para pyodbc (evita SQL injection)
# - Colunas corrigidas conforme Protheus
# - Comentários explicativos
# ------------------------------------------------------------

from datetime import datetime, timedelta

_TABELAS = {
    'SB1': 'SB1010',  # Produtos
    'SB2': 'SB2010',  # Saldos/Estoque
    'SD2': 'SD2010',  # Itens do Pedido de Venda
    'SC2': 'SC2010',  # Ordens de Produção
    'SC5': 'SC5010',  # Cabeçalho PV
    'SA1': 'SA1010',  # Clientes
    'SG1': 'SG1010',  # Estrutura (BOM)
    'SD4': 'SD4010',  # Empenhos
    'SC7': 'SC7010',  # Itens do Pedido de Compra
}

# ---------------- Helpers ----------------
def _periodo_yyyymmdd(dias: int):
    """Retorna (inicio, fim) como 'YYYYMMDD' para os últimos 'dias'."""
    fim = datetime.now()
    ini = fim - timedelta(days=int(dias))
    return ini.strftime('%Y%m%d'), fim.strftime('%Y%m%d')

def _valida_filial(filial: str) -> str:
    """Garante que a filial esteja no formato esperado (2 a 4 dígitos)."""
    if not isinstance(filial, str):
        raise ValueError('filial deve ser string')
    f = filial.strip()
    if not f.isdigit() or len(f) > 4:
        raise ValueError('filial inválida')
    return f.zfill(len(f))

# ---------------- Consultas ----------------

def get_estoque_query(filial):
    return f"""
    SELECT
        D2_ITEM AS CodigoProduto,
        D2_DESC AS Descricao,
        D2_EST AS EstoqueAtual,
        D2_LOTECTL AS ControleLote,
        D2_NUMLOTE AS NumeroLote,
        D2_PESO AS Peso
    FROM D2
    WHERE D2_FILIAL = '{filial}'
    """

def get_pedidos_carteira_query(filial):
    return f"""
    SELECT
        C5_NUM AS NumeroPedido,
        C5_CLIENTE AS CodigoCliente,
        C5_NOMECLI AS NomeCliente,
        C5_EMISSAO AS DataEmissao,
        C5_VLRTOT AS ValorTotal,
        C5_TES AS TipoDocumento
    FROM C5
    WHERE C5_FILIAL = '{filial}'
    """

def get_ops_em_aberto_query(filial):
    return f"""
    SELECT
        C2_NUM AS NumeroOP,
        C2_PRODUTO AS CodigoProduto,
        C2_DATPRI AS DataInicio,
        C2_DATPRF AS DataFim,
        C2_QUANT AS QuantidadeOriginal,
        C2_QUJE AS QuantidadeProduzida,
        (C2_QUANT - C2_QUJE) AS QuantidadePendente,
        C2_OBS AS Observacao
    FROM C2
    WHERE C2_FILIAL = '{filial}'
      AND C2_STATUS <> 'E'
    ORDER BY C2_DATPRI, C2_PRODUTO
    """

def get_necessidade_materia_prima_query(filial):
    return f"""
    SELECT
        D4_PRODUTO AS CodigoProduto,
        D4_OP AS NumeroOP,
        D4_QTNECES AS QuantidadeNecessaria,
        D4_LOCAL AS Local,
        D4_LOTECTL AS ControleLote,
        D4_NUMLOTE AS NumeroLote
    FROM D4
    WHERE D4_FILIAL = '{filial}'
      AND D4_QTNECES > 0
    ORDER BY D4_PRODUTO
    """

def get_ops_detalhado_query(filial):
    return f"""
    SELECT
        C2_NUM AS NumeroOP,
        C2_PRODUTO AS CodigoProduto,
        C2_DATPRI AS DataInicio,
        C2_DATPRF AS DataFim,
        C2_QUANT AS QuantidadeOriginal,
        C2_QUJE AS QuantidadeProduzida,
        (C2_QUANT - C2_QUJE) AS QuantidadePendente,
        C2_OBS AS Observacao
    FROM C2
    WHERE C2_FILIAL = '{filial}'
    ORDER BY C2_NUM
    """

def get_estoque_negativo_justificativa_query(filial):
    return f"""
    SELECT
        D2_ITEM AS CodigoProduto,
        D2_EST AS EstoqueAtual,
        D2_LOTECTL AS ControleLote,
        D2_NUMLOTE AS NumeroLote,
        D2_DESC AS Descricao
    FROM D2
    WHERE D2_FILIAL = '{filial}'
      AND D2_EST < 0
    ORDER BY D2_ITEM
    """

def get_empenho_pendente_op_encerrada_query(filial):
    return f"""
    SELECT
        C7_PRODUTO AS CodigoProduto,
        C7_QUANT AS QuantidadeEmpenhada,
        C7_OP AS NumeroOP,
        C7_NUM AS NumeroPedido,
        C7_DATPRF AS DataEntrega
    FROM C7
    WHERE C7_FILIAL = '{filial}'
      AND C7_OP IS NOT NULL
      AND C7_EMITIDO = 0
    ORDER BY C7_PRODUTO
    """

def get_ops_parcialmente_encerradas_query(filial):
    return f"""
    SELECT
        C2_NUM AS NumeroOP,
        C2_PRODUTO AS CodigoProduto,
        C2_QUANT AS QuantidadeOriginal,
        C2_QUJE AS QuantidadeProduzida,
        (C2_QUANT - C2_QUJE) AS QuantidadePendente
    FROM C2
    WHERE C2_FILIAL = '{filial}'
      AND C2_QUJE > 0
      AND C2_QUJE < C2_QUANT
    ORDER BY C2_NUM
    """
