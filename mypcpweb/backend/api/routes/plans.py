from fastapi import APIRouter
import pandas as pd

from mypcpweb.backend.api.dependencies import get_pcp_conn

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.post("")
def create_plan(ref_year: int, ref_week: int, criado_por: str):
    conn = get_pcp_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO pcp.plan (ref_year, ref_week, status, criado_por)
        VALUES (?, ?, 'DRAFT', ?)
        """,
        ref_year,
        ref_week,
        criado_por,
    )

    conn.commit()
    conn.close()
    return {"status": "ok", "message": "Plano criado"}


@router.get("/{plan_id}")
def get_plan(plan_id: int):
    conn = get_pcp_conn()
    df = pd.read_sql("SELECT * FROM pcp.plan WHERE plan_id = ?", conn, params=[plan_id])
    conn.close()
    return df.to_dict(orient="records")
