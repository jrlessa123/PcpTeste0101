import logging

from database import queries

logger = logging.getLogger(__name__)

class PCPService:
    def __init__(self, cnxn, filial, empresa="010"):
        self.cnxn = cnxn
        self.filial = filial
        self.empresa = empresa

    def _execute_query(self, query_func, params=None, **query_kwargs):
        """Executa a query da função recebida e retorna o resultado como lista de dicionários."""
        try:
            query = query_func(**query_kwargs)
            cursor = self.cnxn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception:
            logger.exception("Erro ao executar a consulta")
            return None

    def get_estoque(self):
        return self._execute_query(
            queries.get_estoque_query,
            params=[self.filial],
            empresa=self.empresa,
        )

    def get_pedidos_carteira(self):
        return self._execute_query(
            queries.get_pedidos_carteira_query,
            params=[self.filial],
            empresa=self.empresa,
        )

    def get_ops_em_aberto(self):
        return self._execute_query(
            queries.get_ops_em_aberto_query,
            params=[self.filial],
            empresa=self.empresa,
        )

    def get_necessidade_materia_prima(self):
        return self._execute_query(
            queries.get_necessidade_materia_prima_query,
            params=[self.filial],
            empresa=self.empresa,
        )

    def get_ops_detalhado(self):
        return self._execute_query(
            queries.get_ops_detalhado_query,
            params=[self.filial],
            empresa=self.empresa,
        )

    def get_estoque_negativo_justificativa(self):
        return self._execute_query(
            queries.get_estoque_negativo_justificativa_query,
            params=[self.filial],
            empresa=self.empresa,
        )

    def get_empenho_pendente_op_encerrada(self):
        return self._execute_query(
            queries.get_empenho_pendente_op_encerrada_query,
            params=[self.filial],
            empresa=self.empresa,
        )

    def get_ops_parcialmente_encerradas(self):
        return self._execute_query(
            queries.get_ops_parcialmente_encerradas_query,
            params=[self.filial],
            empresa=self.empresa,
        )

    def get_ops_encerradas_sem_consumo(self):
        return self._execute_query(
            queries.get_ops_encerradas_sem_consumo_query,
            params=[self.filial],
            empresa=self.empresa,
        )
