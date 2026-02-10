from __future__ import annotations

from typing import Any

from mypcpweb.backend.config import AppConfig
from mypcpweb.backend.database.connection import get_db_connection


class PCPRepository:
    def __init__(self, config: AppConfig):
        self.config = config

    def _connect(self):
        return get_db_connection(self.config, database=self.config.pcp_db_name)

    def create_plan(self, ref_year: int, ref_week: int, criado_por: str) -> dict[str, Any]:
        query = """
        INSERT INTO pcp.plan (ref_year, ref_week, status, criado_por)
        OUTPUT INSERTED.plan_id, INSERTED.ref_year, INSERTED.ref_week, INSERTED.status, INSERTED.criado_por, INSERTED.criado_em
        VALUES (?, ?, 'DRAFT', ?)
        """
        with self._connect() as conn:
            row = conn.cursor().execute(query, [ref_year, ref_week, criado_por]).fetchone()
            conn.commit()
            return {
                "plan_id": row[0],
                "ref_year": row[1],
                "ref_week": row[2],
                "status": row[3],
                "criado_por": row[4],
                "criado_em": row[5],
            }

    def get_plan(self, plan_id: int) -> dict[str, Any] | None:
        q = "SELECT plan_id, ref_year, ref_week, status, criado_por, criado_em FROM pcp.plan WHERE plan_id = ?"
        with self._connect() as conn:
            row = conn.cursor().execute(q, [plan_id]).fetchone()
            if not row:
                return None
            return {
                "plan_id": row[0],
                "ref_year": row[1],
                "ref_week": row[2],
                "status": row[3],
                "criado_por": row[4],
                "criado_em": row[5],
            }

    def update_plan_status(self, plan_id: int, status: str):
        with self._connect() as conn:
            conn.cursor().execute("UPDATE pcp.plan SET status=? WHERE plan_id=?", [status, plan_id])
            conn.commit()

    def get_plan_status(self, plan_id: int) -> dict[str, Any] | None:
        q = "SELECT plan_id, status FROM pcp.plan WHERE plan_id=?"
        with self._connect() as conn:
            row = conn.cursor().execute(q, [plan_id]).fetchone()
            if not row:
                return None
            return {"plan_id": row[0], "status": row[1]}

    def upsert_stock_snapshot(self, plan_id: int, item_type: str, erp_item_code: str, qty: float, unidade: str | None, source: str):
        q = """
        MERGE pcp.plan_stock_snapshot AS target
        USING (SELECT ? AS plan_id, ? AS item_type, ? AS erp_item_code) AS src
        ON target.plan_id = src.plan_id AND target.item_type = src.item_type AND target.erp_item_code = src.erp_item_code
        WHEN MATCHED THEN UPDATE SET qty = ?, unidade = ?, captured_at = SYSDATETIME(), source = ?
        WHEN NOT MATCHED THEN
            INSERT (plan_id, item_type, erp_item_code, qty, unidade, source)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        params = [plan_id, item_type, erp_item_code, qty, unidade, source, plan_id, item_type, erp_item_code, qty, unidade, source]
        with self._connect() as conn:
            conn.cursor().execute(q, params)
            conn.commit()

    def list_production_requirements(self, plan_id: int) -> list[dict[str, Any]]:
        q = """
        SELECT p.erp_item_code, r.required_kg
        FROM pcp.plan_required_production r
        INNER JOIN pcp.product p ON p.product_id = r.product_id
        WHERE r.plan_id = ?
        ORDER BY p.erp_item_code
        """
        with self._connect() as conn:
            rows = conn.cursor().execute(q, [plan_id]).fetchall()
            return [{"item_code": r[0], "quantity": float(r[1]), "week": "WEEK"} for r in rows]

    def list_material_requirements(self, plan_id: int, req_type: str) -> list[dict[str, Any]]:
        q = """
        SELECT m.erp_item_code, r.net_qty
        FROM pcp.plan_material_requirement r
        INNER JOIN pcp.material m ON m.material_id = r.material_id
        WHERE r.plan_id = ? AND r.tipo = ?
        ORDER BY m.erp_item_code
        """
        with self._connect() as conn:
            rows = conn.cursor().execute(q, [plan_id, req_type]).fetchall()
            return [{"item_code": r[0], "quantity": float(r[1]), "week": "WEEK"} for r in rows]

    def replace_required_production(self, plan_id: int):
        delete_q = "DELETE FROM pcp.plan_required_production WHERE plan_id = ?"
        insert_q = """
        INSERT INTO pcp.plan_required_production (plan_id, product_id, required_kg, coverage_days, calc_version)
        SELECT
            f.plan_id,
            f.product_id,
            CASE
                WHEN (f.forecast_kg - ISNULL(s.qty, 0)) > 0 THEN (f.forecast_kg - ISNULL(s.qty, 0))
                ELSE 0
            END AS required_kg,
            7,
            'A_v1'
        FROM pcp.plan_forecast f
        INNER JOIN pcp.product p ON p.product_id = f.product_id
        LEFT JOIN pcp.plan_stock_snapshot s
            ON s.plan_id = f.plan_id
           AND s.item_type = 'PROD'
           AND s.erp_item_code = p.erp_item_code
        WHERE f.plan_id = ?
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(delete_q, [plan_id])
            cur.execute(insert_q, [plan_id])
            conn.commit()

    def replace_material_requirements(self, plan_id: int):
        delete_q = "DELETE FROM pcp.plan_material_requirement WHERE plan_id = ?"

        insert_emb_q = """
        INSERT INTO pcp.plan_material_requirement (plan_id, material_id, tipo, gross_qty, net_qty, unidade)
        SELECT
            r.plan_id,
            pb.material_id,
            'EMB',
            SUM((r.required_kg / NULLIF(sl.kg_por_pct, 0)) * pb.qty_por_pct) AS gross_qty,
            SUM((r.required_kg / NULLIF(sl.kg_por_pct, 0)) * pb.qty_por_pct) AS net_qty,
            MAX(pb.unidade) AS unidade
        FROM pcp.plan_required_production r
        INNER JOIN pcp.sku_logistics sl ON sl.product_id = r.product_id
        INNER JOIN pcp.pack_bom pb ON pb.product_id = r.product_id
        WHERE r.plan_id = ?
        GROUP BY r.plan_id, pb.material_id
        """

        insert_mp_base_q = """
        INSERT INTO pcp.plan_material_requirement (plan_id, material_id, tipo, gross_qty, net_qty, unidade)
        SELECT
            r.plan_id,
            b.material_id,
            'MP',
            SUM((r.required_kg / NULLIF(b.lote_kg, 0)) * b.qty_por_lote) AS gross_qty,
            SUM((r.required_kg / NULLIF(b.lote_kg, 0)) * b.qty_por_lote) AS net_qty,
            MAX(b.unidade) AS unidade
        FROM pcp.plan_required_production r
        INNER JOIN pcp.product p ON p.product_id = r.product_id
        INNER JOIN pcp.recipe_base_bom b ON b.base_id = p.base_id
        WHERE r.plan_id = ?
        GROUP BY r.plan_id, b.material_id
        """

        insert_mp_flavor_q = """
        MERGE pcp.plan_material_requirement AS target
        USING (
            SELECT
                r.plan_id AS plan_id,
                fb.material_id AS material_id,
                SUM((r.required_kg / NULLIF(fb.lote_kg, 0)) * fb.qty_por_lote) AS qty,
                MAX(fb.unidade) AS unidade
            FROM pcp.plan_required_production r
            INNER JOIN pcp.product p ON p.product_id = r.product_id
            INNER JOIN pcp.recipe_flavor_bom fb
                ON fb.base_id = p.base_id
               AND fb.flavor_id = p.flavor_id
            WHERE r.plan_id = ?
            GROUP BY r.plan_id, fb.material_id
        ) AS src
        ON target.plan_id = src.plan_id AND target.material_id = src.material_id AND target.tipo = 'MP'
        WHEN MATCHED THEN UPDATE
            SET target.gross_qty = target.gross_qty + src.qty,
                target.net_qty = target.net_qty + src.qty,
                target.unidade = src.unidade
        WHEN NOT MATCHED THEN
            INSERT (plan_id, material_id, tipo, gross_qty, net_qty, unidade)
            VALUES (src.plan_id, src.material_id, 'MP', src.qty, src.qty, src.unidade);
        """

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(delete_q, [plan_id])
            cur.execute(insert_emb_q, [plan_id])
            cur.execute(insert_mp_base_q, [plan_id])
            cur.execute(insert_mp_flavor_q, [plan_id])
            conn.commit()

    def create_requisition(self, plan_id: int, req_type: str) -> dict[str, Any]:
        q = """
        INSERT INTO pcp.requisition (plan_id, tipo, status)
        OUTPUT INSERTED.requisition_id, INSERTED.plan_id, INSERTED.tipo, INSERTED.status, INSERTED.erp_request_id, INSERTED.criado_em
        VALUES (?, ?, 'DRAFT')
        """
        with self._connect() as conn:
            row = conn.cursor().execute(q, [plan_id, req_type]).fetchone()
            conn.commit()
            return {
                "id": row[0],
                "plan_id": row[1],
                "req_type": row[2],
                "status": row[3],
                "erp_request_id": row[4],
                "created_at": row[5],
            }

    def update_requisition_sent(self, requisition_id: int, erp_request_id: str, status: str) -> dict[str, Any] | None:
        q = """
        UPDATE pcp.requisition
        SET erp_request_id=?, status=?
        OUTPUT INSERTED.requisition_id, INSERTED.plan_id, INSERTED.tipo, INSERTED.status, INSERTED.erp_request_id, INSERTED.criado_em
        WHERE requisition_id=?
        """
        with self._connect() as conn:
            row = conn.cursor().execute(q, [erp_request_id, status, requisition_id]).fetchone()
            conn.commit()
            if not row:
                return None
            return {
                "id": row[0],
                "plan_id": row[1],
                "req_type": row[2],
                "status": row[3],
                "erp_request_id": row[4],
                "created_at": row[5],
            }
