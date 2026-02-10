# PCPTeste0101

## 📘 Roadmap do Projeto PCP

Toda a evolução técnica deste projeto foi documentada em:
`docs/roadmap/pcp_roadmap_chat.pdf`

Versão editável:
`docs/roadmap/pcp_roadmap_chat.md`

## Ambiente Docker (FastAPI + Redis + Worker)

Suba API + Redis:

```bash
docker compose up --build
```

Para subir também o worker Celery:

```bash
docker compose --profile worker up --build
```

Serviços previstos:
- `pcp-api` na porta `8000`
- `redis` na porta `6379`
- `worker` (Celery)

Defina as variáveis em `mypcpweb/.env` com base em `mypcpweb/.env.example`.
