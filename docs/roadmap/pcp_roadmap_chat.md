# Roadmap do Projeto PCP

## Fase atual
- Backend FastAPI com cálculo A (produção requerida) e B (explosão MRP).
- Persistência em SQL Server no banco `PCP_DB` e schema `pcp`.
- Integração Protheus em modo SQL fallback.

## Próximas fases
1. Jobs assíncronos com Celery + Redis.
2. Integração REST Protheus quando disponível.
3. UI Streamlit/React consumindo apenas API.
4. Governança: auditoria, métricas e trilha de execução.
