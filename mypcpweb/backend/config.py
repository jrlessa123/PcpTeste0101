from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppConfig:
    db_driver: str
    db_server: str
    db_name: str
    db_user: str
    db_pass: str
    filial: str
    empresa: str

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            db_driver=os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
            db_server=os.getenv("DB_SERVER", ""),
            db_name=os.getenv("DB_NAME", ""),
            db_user=os.getenv("DB_USER", ""),
            db_pass=os.getenv("DB_PASS", ""),
            filial=os.getenv("FILIAL", "01"),
            empresa=os.getenv("EMPRESA", "010"),
        )
