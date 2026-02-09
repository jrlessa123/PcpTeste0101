import pyodbc

from config import AppConfig


def build_connection_string(config: AppConfig) -> str:
    return (
        f"DRIVER={{{config.db_driver}}};"
        f"SERVER={config.db_server};"
        f"DATABASE={config.db_name};"
        f"UID={config.db_user};"
        f"PWD={config.db_pass};"
        "TrustServerCertificate=yes;"
    )


def get_db_connection(config: AppConfig):
    return pyodbc.connect(build_connection_string(config))
