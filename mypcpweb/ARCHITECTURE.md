# Arquitetura Backend (fase atual)

## Premissas
- PCP em `PCP_DB` (schema `pcp`).
- Protheus sem REST disponível (uso de SQL fallback read-only).
- Motor de cálculo no backend FastAPI.

## Componentes
- `backend/adapters/protheus_sql_adapter.py`: leitura de itens/estoque do Protheus via SQL.
- `backend/api/routes/stock.py`: snapshot para `pcp.plan_stock_snapshot`.
- `backend/api/routes/mrp.py`: PARTE A (`/calc-production`) e PARTE B (`/explode-mrp`).
- `backend/api/services/planning_service.py`: cálculo determinístico da produção requerida.
- `backend/api/services/mrp_*`: explosão e consolidação de materiais.

## Fluxo
1. `POST /plans`
2. `POST /plans/{id}/snapshot-stock`
3. `POST /plans/{id}/calc-production`
4. `POST /plans/{id}/explode-mrp`
