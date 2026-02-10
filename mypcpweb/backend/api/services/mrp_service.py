from __future__ import annotations

import pandas as pd


def consolidate_material_needs(gross_df: pd.DataFrame, stock_df: pd.DataFrame) -> pd.DataFrame:
    if gross_df.empty:
        return pd.DataFrame(columns=["material_id", "gross_qty", "net_qty", "unidade"])

    stock_map = {}
    if stock_df is not None and not stock_df.empty:
        stock_map = stock_df.set_index("material_id")["qty"].to_dict()

    consolidated: list[dict] = []

    for material_id, group in gross_df.groupby("material_id"):
        gross = float(group["gross_qty"].sum())
        stock = float(stock_map.get(material_id, 0.0))
        net = max(0.0, gross - stock)

        consolidated.append(
            {
                "material_id": int(material_id),
                "gross_qty": round(gross, 2),
                "net_qty": round(net, 2),
                "unidade": group["unidade"].iloc[0],
            }
        )

    return pd.DataFrame(consolidated)
