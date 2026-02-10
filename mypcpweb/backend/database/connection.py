import json
import time
import pyodbc
from pathlib import Path

from config import AppConfig

# Ordem de preferência para driver ODBC (mais recente primeiro)
_SQL_DRIVERS = [
    "ODBC Driver 19 for SQL Server",
    "ODBC Driver 18 for SQL Server",
    "ODBC Driver 17 for SQL Server",
]


def _resolve_driver(config: AppConfig) -> str:
    """Usa o driver do config se estiver instalado; senão o primeiro disponível (19/18/17)."""
    requested = (config.db_driver or "").strip()
    installed = {d for d in pyodbc.drivers()}
    if requested and requested in installed:
        return requested
    for name in _SQL_DRIVERS:
        if name in installed:
            return name
    return requested or _SQL_DRIVERS[-1]


DEBUG_LOG_PATH = Path(
    r"c:\Users\Administrador\Documents\PcpTeste0101\.cursor\debug.log"
)


def _agent_log(hypothesis_id: str, message: str, data: dict) -> None:
    """Pequeno helper de log para debug da conexão com o banco."""
    payload = {
        "id": f"log_{int(time.time() * 1000)}",
        "timestamp": int(time.time() * 1000),
        "runId": "initial-run",
        "hypothesisId": hypothesis_id,
        "location": "backend/database/connection.py",
        "message": message,
        "data": data,
    }
    try:
        DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with DEBUG_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        # Nunca deixar o log quebrar a aplicação.
        pass


def build_connection_string(config: AppConfig) -> str:
    driver = _resolve_driver(config)
    # region agent log
    _agent_log(
        "H1_env_config",
        "Construindo connection string",
        {
            "db_driver_requested": config.db_driver,
            "db_driver_resolved": driver,
            "db_server": config.db_server,
            "db_name_empty": not bool(config.db_name),
            "db_user_empty": not bool(config.db_user),
            "db_pass_empty": not bool(config.db_pass),
        },
    )
    # endregion
    # Força TCP ao usar IP (evita "Pipes Nomeados" em servidor remoto)
    server = (config.db_server or "").strip()
    if server and "\\" not in server and "," not in server:
        server = f"{server},1433"
    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={config.db_name};"
        f"UID={config.db_user};"
        f"PWD={config.db_pass};"
        "TrustServerCertificate=yes;"
        "Connection Timeout=15;"
    )


def get_db_connection(config: AppConfig):
    # region agent log
    _agent_log(
        "H2_connectivity",
        "Tentando abrir conexão com SQL Server",
        {
            "db_server": config.db_server,
            "db_name": config.db_name,
            "db_user": config.db_user,
        },
    )
    # endregion

    try:
        cnxn = pyodbc.connect(build_connection_string(config))
        # region agent log
        _agent_log(
            "H3_success_path",
            "Conexão estabelecida com sucesso",
            {"ok": True},
        )
        # endregion
        return cnxn
    except pyodbc.Error as e:
        # region agent log
        _agent_log(
            "H4_error_details",
            "Falha ao conectar no SQL Server",
            {"error": str(e)},
        )
        # endregion
        raise
