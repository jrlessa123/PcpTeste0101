from functools import lru_cache

from mypcpweb.backend.api.services.repository import PCPRepository
from mypcpweb.backend.config import AppConfig
from mypcpweb.backend.database.connection import get_conn


@lru_cache
def get_config() -> AppConfig:
    return AppConfig.from_env()


@lru_cache
def get_repository() -> PCPRepository:
    return PCPRepository(get_config())


def get_pcp_conn():
    return get_conn(database="PCP_DB")
