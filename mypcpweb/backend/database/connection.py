import pyodbc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypcpweb.backend.config import AppConfig


def build_connection_string(config: "AppConfig", database: str | None = None) -> str:
    db_name = database or config.db_name
    return (
        f"DRIVER={{{config.db_driver}}};"
        f"SERVER={config.db_server};"
        f"DATABASE={db_name};"
        f"UID={config.db_user};"
        f"PWD={config.db_pass};"
        "TrustServerCertificate=yes;"
    )


def get_db_connection(config: "AppConfig", database: str | None = None):
    return pyodbc.connect(build_connection_string(config, database=database))


def get_conn(database: str = "PCP_DB"):
    """Compatibility wrapper used by API dependencies and routes."""
    from mypcpweb.backend.config import AppConfig

    config = AppConfig.from_env()
    db_name = database

    if database.upper() == "PCP_DB":
        db_name = config.pcp_db_name
    elif database.upper() == "PROTHEUS_DB":
        db_name = config.protheus_db_name

    return get_db_connection(config, database=db_name)
