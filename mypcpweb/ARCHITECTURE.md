# Arquitetura mínima - PCP Shadow

## Premissas
- PCP em `PCP_DB` (schema `pcp`).
- Protheus sem REST disponível (uso de SQL fallback read-only).
- Motor de cálculo no backend FastAPI.
## Objetivo
Disponibilizar visibilidade em tempo real do PCP sem depender do módulo padrão do Protheus, mantendo o Protheus como sistema de registro e evitando escrita direta no banco.

## Alinhamento ao Protheus (PCP e Comercial)
- **SB1**: cadastro de produto; **B1_DESC** = descrição; normalização por B1_COD (cadastro único ou por filial).
- **SB2**: saldos por armazém (estoque atual, reserva, local).
- **SC2**: ordens de produção (PCP); C2_QUANT/C2_QUJE = original/produzido; **C2_STATUS**: N=Liberada, E=Encerrada; **StatusOPDescricao** e **ApontadoParcial**/**ApontadoTotal** para análise de ganho/perda.
- **SC5/SC6**: pedidos de venda. **Carteira** = itens com saldo a entregar; **C5_VEND** + **SA3** = vendedor de origem; **C6_NOTA**/C6_SERIE = NF emitida; **EntregaParcial** = corte no carregamento (QTDENT < QTDVEN).
- **Coleta e Entrega (TOTVS)**: **DAI** = itens da carga (DAI_PEDIDO, DAI_DTCHEG = data chegada); **DAK** = cargas (DAK_FEZNF = gerou NF). **TemRomaneioCarga** e **StatusEntrega** (Pendente | Com romaneio/carga | NF emitida | Entrega realizada) vêm dessas amarrações. Se o módulo não estiver em uso, a query da Carteira pode falhar (tabelas DAI/DAK); ajustar ou desativar o uso de DAI nesse caso.

## Componentes (MVP)
1. **Leitura direta do banco (SQL Server/Oracle)**
   - Consultas de estoque, carteira e OPs com filtro `D_E_L_E_T_ = ''`.
   - Tabelas com sufixo de empresa (ex: `SC2010`, `SB2010`).
2. **Serviço de dados (Python)**
   - `PCPService` encapsula as queries.
   - Saída em JSON/dicionários para consumir em dashboards e agentes.
3. **Dashboard MVP (Streamlit)**
   - Painéis de estoque, carteira, OPs em aberto e alertas rápidos.
4. **Agente Auditor**
   - Identifica anomalias (ex: OP encerrada sem consumo).
   - Envia alertas para responsáveis antes de rodar o PCP.
5. **Configuração**
   - Variáveis de ambiente em `.env` (ver `.env.example`).

## Fluxo de dados
```mermaid
flowchart LR
    A[Protheus SQL] --> B[PCPService]
    B --> C[Dashboard MVP]
    B --> D[Agente Auditor]
```

## Evolução sugerida
1. **Alertas operacionais**: alertas em Teams/Email/Telegram.
2. **Simulador de cenários**: cálculo de disponibilidade futura (estoque + OPs - carteira).
3. **Escrita segura**: integração via API REST/ADVPL para apontamentos e baixas.

> Nota: esta versão consolida a resolução dos conflitos apontados no PR.
