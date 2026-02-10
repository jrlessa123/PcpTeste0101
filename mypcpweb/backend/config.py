from dataclasses import dataclass
import os


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
        db_name = os.getenv("DB_NAME", "") or os.getenv("DB_DATABASE", "")
        db_user = os.getenv("DB_USER", "") or os.getenv("DB_USERNAME", "")
        db_pass = os.getenv("DB_PASS", "") or os.getenv("DB_PASSWORD", "")

        return cls(
            db_driver=os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
            db_server=os.getenv("DB_SERVER", ""),
            db_user=db_user,
            db_pass=db_pass,
            db_name=db_name,
            pcp_db_name=os.getenv("PCP_DB_NAME", db_name or "PCP_DB"),
            protheus_db_name=os.getenv("PROTHEUS_DB_NAME", db_name),
            protheus_conn_str=os.getenv("PROTHEUS_CONN_STR", ""),
            filial=os.getenv("FILIAL", "01"),
            empresa=os.getenv("EMPRESA", "010"),
        )
