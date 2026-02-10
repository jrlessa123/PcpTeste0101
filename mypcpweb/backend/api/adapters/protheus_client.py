from __future__ import annotations

import os
from typing import Any

import requests


class ProtheusClient:
    """REST adapter for Protheus endpoints.

    If endpoint environment variables are missing, methods raise RuntimeError to keep
    the integration explicit during phase 1.
    """

    def __init__(self):
        self.base_url = os.getenv("PROTHEUS_BASE_URL", "").rstrip("/")
        self.items_path = os.getenv("PROTHEUS_ITEMS_PATH", "")
        self.stock_path = os.getenv("PROTHEUS_STOCK_PATH", "")
        self.requisition_path = os.getenv("PROTHEUS_REQUISITION_PATH", "")
        self.timeout_s = int(os.getenv("PROTHEUS_TIMEOUT_S", "20"))

    def _require_path(self, path: str, env_name: str) -> str:
        if not self.base_url or not path:
            raise RuntimeError(
                f"Protheus REST endpoint not configured. Set PROTHEUS_BASE_URL and {env_name}."
            )
        return f"{self.base_url}/{path.lstrip('/')}"

    def get_items(self) -> list[dict[str, Any]]:
        url = self._require_path(self.items_path, "PROTHEUS_ITEMS_PATH")
        return requests.get(url, timeout=self.timeout_s).json()

    def get_stock(self, warehouse: str) -> list[dict[str, Any]]:
        url = self._require_path(self.stock_path, "PROTHEUS_STOCK_PATH")
        return requests.get(url, params={"armazem": warehouse}, timeout=self.timeout_s).json()

    def post_requisition(self, payload: dict[str, Any]) -> str:
        url = self._require_path(self.requisition_path, "PROTHEUS_REQUISITION_PATH")
        response = requests.post(url, json=payload, timeout=self.timeout_s)
        response.raise_for_status()
        data = response.json()
        return str(data.get("erp_request_id") or data.get("id") or "")
