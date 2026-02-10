import pandas as pd


def aggregate_base_flavor(prod_req_df: pd.DataFrame, product_df: pd.DataFrame):
    merged = prod_req_df.merge(product_df, on="erp_item_code", how="left")

    base_req = merged.groupby("base_id")["required_kg"].sum().reset_index(name="kg_total")
    flavor_req = merged.groupby(["base_id", "flavor_id"])["required_kg"].sum().reset_index(name="kg_total")

    return base_req, flavor_req
