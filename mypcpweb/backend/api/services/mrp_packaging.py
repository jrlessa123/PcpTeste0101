from __future__ import annotations

import pandas as pd


def explode_packaging(requirement_df: pd.DataFrame, pack_bom_df: pd.DataFrame) -> pd.DataFrame:
    """Explode packaging requirements from required production per SKU."""
    rows: list[dict] = []

    for _, req in requirement_df.iterrows():
        sku = req["erp_item_code"]
        kg = float(req["required_kg"])

        bom_items = pack_bom_df[pack_bom_df["erp_item_code"] == sku]
        for _, bom in bom_items.iterrows():
            qty = (kg / float(bom["kg_por_pct"])) * float(bom["qty_por_pct"])
            rows.append(
                {
                    "material_id": int(bom["material_id"]),
                    "tipo": "EMB",
                    "gross_qty": round(qty, 2),
                    "unidade": bom["unidade"],
                }
            )

    return pd.DataFrame(rows)
