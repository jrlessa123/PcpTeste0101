from fastapi import FastAPI

from mypcpweb.backend.api.routes import mrp, plans, stock

app = FastAPI(title="PCP Core API")

app.include_router(plans.router)
app.include_router(stock.router)
app.include_router(mrp.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
