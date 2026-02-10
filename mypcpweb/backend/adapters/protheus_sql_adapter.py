from __future__ import annotations

from typing import Any

import pyodbc

from mypcpweb.backend.config import AppConfig
from mypcpweb.backend.database.connection import get_db_connection


class ProtheusSQLAdapter:
    """Read-only SQL adapter for Protheus while REST is unavailable."""

    def __init__(self, config: AppConfig):
        self.config = config

    def _connect(self):
        if self.config.protheus_conn_str:
            return pyodbc.connect(self.config.protheus_conn_str)
        return get_db_connection(self.config, database=self.config.protheus_db_name)

    def get_items(self) -> list[dict[str, Any]]:
        table = f"SB1{self.config.empresa}"
        sql = f"""
        SELECT
            B1_COD AS erp_item_code,
            B1_DESC AS descricao,
            B1_UM AS unidade
        FROM {table}
        WHERE D_E_L_E_T_ = ''
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def get_stock(self, armazem: str = "01") -> list[dict[str, Any]]:
        table = f"SB2{self.config.empresa}"
        sql = f"""
        SELECT
            B2_COD AS erp_item_code,
            SUM(B2_QATU) AS qty,
            MAX(B2_LOCAL) AS armazem,
            MAX(B2_UM) AS unidade
        FROM {table}
        WHERE D_E_L_E_T_ = ''
          AND B2_FILIAL = ?
          AND B2_LOCAL = ?
        GROUP BY B2_COD
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, [self.config.filial, armazem])
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
