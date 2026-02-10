from __future__ import annotations

import pandas as pd


def explode_raw_materials(
    base_requirement_df: pd.DataFrame,
    base_bom_df: pd.DataFrame,
    flavor_requirement_df: pd.DataFrame,
    flavor_bom_df: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict] = []

    for _, req in base_requirement_df.iterrows():
        base_id = req["base_id"]
        base_kg = float(req["kg_total"])
        bom = base_bom_df[base_bom_df["base_id"] == base_id]

        for _, item in bom.iterrows():
            qty = (base_kg / float(item["lote_kg"])) * float(item["qty_por_lote"])
            rows.append(
                {
                    "material_id": int(item["material_id"]),
                    "tipo": "MP",
                    "gross_qty": round(qty, 2),
                    "unidade": item["unidade"],
                }
            )

    for _, req in flavor_requirement_df.iterrows():
        base_id = req["base_id"]
        flavor_id = req["flavor_id"]
        flavor_kg = float(req["kg_total"])

        bom = flavor_bom_df[
            (flavor_bom_df["base_id"] == base_id)
            & (flavor_bom_df["flavor_id"] == flavor_id)
        ]

        for _, item in bom.iterrows():
            qty = (flavor_kg / float(item["lote_kg"])) * float(item["qty_por_lote"])
            rows.append(
                {
                    "material_id": int(item["material_id"]),
                    "tipo": "MP",
                    "gross_qty": round(qty, 2),
                    "unidade": item["unidade"],
                }
            )

    return pd.DataFrame(rows)
