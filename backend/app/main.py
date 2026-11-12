from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db
from app.routers import cafeterias, listings, services

app = FastAPI(title="ServeEasy API")
app.include_router(listings.router)
app.include_router(cafeterias.router)
app.include_router(services.router)


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "reachable"}
