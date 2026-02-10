import pyodbc

from mypcpweb.backend.config import AppConfig


def build_connection_string(
    config: AppConfig, 
    database: str | None = None,
    server: str | None = None,
    user: str | None = None,
    password: str | None = None,
) -> str:
    """
    Builder único de connection string para SQL Server.
    Permite sobrescrever DB/Server/User/Pass quando necessário.
    """

    db = database or config.db_name
    srv = server or config.db_server
    uid = user or config.db_user
    pwd = password or config.db_pass

    return (
        f"DRIVER={{{config.db_driver}}};"
        f"SERVER={srv};"
        f"DATABASE={db};"
        f"UID={uid};"
        f"PWD={pwd};"
        "TrustServerCertificate=yes;"
    )


def get_db_connection(
    config: AppConfig,
    database: str | None = None,
    server: str | None = None,
    user: str | None = None,
    password: str | None = None,
):
    return pyodbc.connect(
        build_connection_string(
            config,
            database=database,
            server=server,
            user=user,
            password=password,
        )
    )


def get_conn(database: str = "PCP_DB"):
    """
    Compatibility wrapper usado por rotas e dependências FastAPI.

    Regras:
    - "PCP_DB"       -> usa PCP_DB_* (banco operacional da aplicação)
    - "PROTHEUS_DB"  -> usa PROTHEUS_DB_* (fonte oficial do Protheus)
    - Qualquer outro -> assume nome literal do banco no mesmo servidor padrão
    """

    config = AppConfig.from_env()
    db_key = database.upper().strip()

    if db_key == "PCP_DB":
        return get_db_connection(
            config,
            database=config.pcp_db_name,
            server=config.pcp_db_server,
            user=config.pcp_db_uid,
            password=config.pcp_db_pwd,
        )

    elif db_key in ("PROTHEUS_DB", "PROTHEUS"):
        return get_db_connection(
            config,
            database=config.protheus_db_name,
            server=config.protheus_db_server,
            user=config.protheus_db_user,
            password=config.protheus_db_pass,
        )

    # Fallback: usa servidor/credenciais padrão (útil para consultas pontuais)
    return get_db_connection(config, database=database)
