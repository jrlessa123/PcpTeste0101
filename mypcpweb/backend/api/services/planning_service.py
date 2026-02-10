from __future__ import annotations

import pandas as pd


def calculate_required_production(
    forecast_df: pd.DataFrame,
    stock_df: pd.DataFrame,
    adjustments_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Calculate required production per SKU for a weekly plan.

    Required_kg = max(0, Forecast_kg - Stock_kg + Adjustment_kg)
    """
    if adjustments_df is not None and not adjustments_df.empty:
        adj_map = (
            adjustments_df.groupby("erp_item_code")["adj_qty_kg"].sum().to_dict()
        )
    else:
        adj_map = {}

    if stock_df is not None and not stock_df.empty:
        stock_map = stock_df.groupby("erp_item_code")["qty_kg"].sum().to_dict()
    else:
        stock_map = {}

    results: list[dict] = []

    for _, row in forecast_df.iterrows():
        sku = row["erp_item_code"]
        forecast = float(row["forecast_kg"])
        stock = float(stock_map.get(sku, 0.0))
        adj = float(adj_map.get(sku, 0.0))

        required = max(0.0, forecast - stock + adj)

        coverage_days = None
        if forecast > 0:
            coverage_days = round(stock / (forecast / 7), 0)

        results.append(
            {
                "erp_item_code": sku,
                "forecast_kg": round(forecast, 2),
                "stock_kg": round(stock, 2),
                "adjustment_kg": round(adj, 2),
                "required_kg": round(required, 2),
                "coverage_days": coverage_days,
            }
        )

    return pd.DataFrame(results)
