from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

# Garante que o .env seja carregado (dashboard e outros usam config, não db_connection)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


@dataclass(frozen=True)
class AppConfig:
    db_driver: str
    db_server: str
    db_user: str
    db_pass: str
    db_name: str
    pcp_db_name: str
    protheus_db_name: str
    protheus_conn_str: str
    filial: str
    empresa: str

    @classmethod
    def from_env(cls) -> "AppConfig":
        db_name = os.getenv("DB_NAME", "")
        return cls(
            db_driver=os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
            db_server=os.getenv("DB_SERVER", ""),
            db_name=os.getenv("DB_NAME", ""),
            db_user=os.getenv("DB_USER", ""),
            db_pass=os.getenv("DB_PASS", ""),
            filial=os.getenv("FILIAL", "01"),
            empresa=os.getenv("EMPRESA", "01"),
        )
