# PCP Backend (PCP_DB) — FastAPI

Implementação focada em **backend** com SQL Server e fluxo semanal:

1. Criar plano semanal.
2. Capturar snapshot de estoque (SQL fallback do Protheus).
3. **PARTE A**: calcular produção requerida por SKU.
4. **PARTE B**: explodir MRP (MP + EMB).

## Endpoints principais

- `POST /plans?ref_year=2025&ref_week=6&criado_por=pcp`
- `GET /plans/{plan_id}`
- `POST /stock/snapshot/{plan_id}`
- `POST /mrp/recalculate/{plan_id}`

## Cálculo de produção requerida (A)

Regra aplicada:

`required_kg = max(0, forecast_kg - stock_kg + adjustment_kg)`

## Docker (FastAPI + Redis + Worker)

Arquivos adicionados:
- `Dockerfile`
- `docker-compose.yml`
- `.env.example`

Subir API + Redis:

```bash
docker compose up --build
```

Subir também o worker Celery:

```bash
docker compose --profile worker up --build
```

Serviços:
- `pcp-api` → `http://localhost:8000`
- `redis` → broker para jobs
- `worker` → Celery worker

### Variáveis obrigatórias (.env)
- `PCP_DB_SERVER`
- `PCP_DB_UID`
- `PCP_DB_PWD`
- `PCP_DB_NAME` (default: `PCP_DB`)
- `PROTHEUS_CONN_STR` (quando necessário)

## Executar local sem Docker

```bash
pip install -r requirements.txt
uvicorn mypcpweb.backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

DDL de referência:
`backend/database/sql/pcp_schema_sqlserver.sql`

## 📘 Roadmap do Projeto PCP

Toda a evolução técnica deste projeto foi documentada em:
`../docs/roadmap/pcp_roadmap_chat.pdf`
