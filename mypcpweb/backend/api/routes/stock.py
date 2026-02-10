from fastapi import APIRouter

from mypcpweb.backend.adapters.protheus_sql_adapter import ProtheusSQLAdapter
from mypcpweb.backend.api.dependencies import get_config, get_pcp_conn

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.post("/snapshot/{plan_id}")
def capture_stock_snapshot(plan_id: int, armazem: str = "01"):
    config = get_config()
    protheus = ProtheusSQLAdapter(config)
    stock_df = protheus.get_stock(armazem)

    conn = get_pcp_conn()
    cur = conn.cursor()

    for _, r in stock_df.iterrows():
        cur.execute(
            """
            MERGE pcp.plan_stock_snapshot AS t
            USING (SELECT ? AS plan_id, ? AS item_type, ? AS erp_item_code) AS s
            ON (t.plan_id = s.plan_id AND t.item_type = s.item_type AND t.erp_item_code = s.erp_item_code)
            WHEN MATCHED THEN
                UPDATE SET qty = ?, captured_at = SYSDATETIME(), source = 'SQL_FALLBACK'
            WHEN NOT MATCHED THEN
                INSERT (plan_id, item_type, erp_item_code, qty, unidade, source)
                VALUES (?, 'PROD', ?, ?, 'KG', 'SQL_FALLBACK');
            """,
            plan_id,
            "PROD",
            r["erp_item_code"],
            float(r["qty"]),
            plan_id,
            r["erp_item_code"],
            float(r["qty"]),
        )

    conn.commit()
    conn.close()
    return {"status": "ok", "rows": int(len(stock_df))}
