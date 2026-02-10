from fastapi import APIRouter
import pandas as pd

from mypcpweb.backend.api.dependencies import get_pcp_conn
from mypcpweb.backend.api.services.aggregation_service import aggregate_base_flavor
from mypcpweb.backend.api.services.mrp_packaging import explode_packaging
from mypcpweb.backend.api.services.mrp_raw_materials import explode_raw_materials
from mypcpweb.backend.api.services.mrp_service import consolidate_material_needs
from mypcpweb.backend.api.services.planning_service import calculate_required_production

router = APIRouter(prefix="/mrp", tags=["MRP"])


@router.post("/recalculate/{plan_id}")
def recalc_plan(plan_id: int):
    conn = get_pcp_conn()
    cur = conn.cursor()

    forecast_df = pd.read_sql(
        """
        SELECT p.erp_item_code, f.forecast_kg
        FROM pcp.plan_forecast f
        JOIN pcp.product p ON p.product_id = f.product_id
        WHERE f.plan_id = ?
        """,
        conn,
        params=[plan_id],
    )

    stock_df = pd.read_sql(
        """
        SELECT erp_item_code, qty AS qty_kg
        FROM pcp.plan_stock_snapshot
        WHERE plan_id = ?
          AND item_type = 'PROD'
        """,
        conn,
        params=[plan_id],
    )

    adj_df = pd.read_sql(
        """
        SELECT erp_item_code, qty AS adj_qty_kg
        FROM pcp.plan_adjustment
        WHERE plan_id = ?
          AND item_type = 'PROD'
        """,
        conn,
        params=[plan_id],
    )

    prod_req = calculate_required_production(forecast_df, stock_df, adj_df)

    prod_map = pd.read_sql("SELECT product_id, erp_item_code FROM pcp.product", conn)
    sku_to_id = dict(zip(prod_map["erp_item_code"], prod_map["product_id"]))

    for _, r in prod_req.iterrows():
        product_id = sku_to_id.get(r["erp_item_code"])
        if not product_id:
            continue

        cur.execute(
            """
            MERGE pcp.plan_required_production AS t
            USING (SELECT ? AS plan_id, ? AS product_id) AS s
            ON (t.plan_id = s.plan_id AND t.product_id = s.product_id)
            WHEN MATCHED THEN
                UPDATE SET required_kg = ?, coverage_days = ?, calc_version = 'v1'
            WHEN NOT MATCHED THEN
                INSERT (plan_id, product_id, required_kg, coverage_days, calc_version)
                VALUES (?, ?, ?, ?, 'v1');
            """,
            plan_id,
            int(product_id),
            float(r["required_kg"]),
            r["coverage_days"],
            plan_id,
            int(product_id),
            float(r["required_kg"]),
            r["coverage_days"],
        )

    product_df = pd.read_sql("SELECT erp_item_code, base_id, flavor_id FROM pcp.product", conn)
    base_req, flavor_req = aggregate_base_flavor(prod_req, product_df)

    pack_bom = pd.read_sql(
        """
        SELECT p.erp_item_code, b.material_id, b.qty_por_pct, l.kg_por_pct, b.unidade
        FROM pcp.pack_bom b
        JOIN pcp.product p ON p.product_id = b.product_id
        JOIN pcp.sku_logistics l ON l.product_id = p.product_id
        """,
        conn,
    )
    emb_gross = explode_packaging(prod_req, pack_bom)

    base_bom = pd.read_sql("SELECT * FROM pcp.recipe_base_bom", conn)
    flavor_bom = pd.read_sql("SELECT * FROM pcp.recipe_flavor_bom", conn)
    mp_gross = explode_raw_materials(base_req, base_bom, flavor_req, flavor_bom)

    gross_all = pd.concat([emb_gross, mp_gross], ignore_index=True)

    stock_mat = pd.read_sql(
        """
        SELECT m.material_id, SUM(s.qty) AS qty
        FROM pcp.plan_stock_snapshot s
        JOIN pcp.material m ON m.erp_item_code = s.erp_item_code
        WHERE s.plan_id = ?
          AND s.item_type = 'MAT'
        GROUP BY m.material_id
        """,
        conn,
        params=[plan_id],
    )

    net_req = consolidate_material_needs(gross_all, stock_mat)

    tipo_map = gross_all.groupby("material_id")["tipo"].agg(lambda s: "EMB" if "EMB" in set(s) else "MP").to_dict()

    for _, r in net_req.iterrows():
        tipo = tipo_map.get(int(r["material_id"]), "MP")
        cur.execute(
            """
            MERGE pcp.plan_material_requirement AS t
            USING (SELECT ? AS plan_id, ? AS material_id, ? AS tipo) AS s
            ON (t.plan_id = s.plan_id AND t.material_id = s.material_id AND t.tipo = s.tipo)
            WHEN MATCHED THEN
                UPDATE SET gross_qty = ?, net_qty = ?, unidade = ?
            WHEN NOT MATCHED THEN
                INSERT (plan_id, material_id, tipo, gross_qty, net_qty, unidade)
                VALUES (?, ?, ?, ?, ?, ?);
            """,
            plan_id,
            int(r["material_id"]),
            tipo,
            float(r["gross_qty"]),
            float(r["net_qty"]),
            r["unidade"],
            plan_id,
            int(r["material_id"]),
            tipo,
            float(r["gross_qty"]),
            float(r["net_qty"]),
            r["unidade"],
        )

    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "prod_rows": int(len(prod_req)),
        "material_rows": int(len(net_req)),
    }
