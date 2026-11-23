from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.bot.telegram_bot import start_bot, stop_bot
from app.config import settings
from app.db import get_db
from app.routers import (
    cafeterias,
    listings,
    me,
    meals,
    notifications,
    requests,
    services,
    shops,
    uploads,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Run the Telegram bot next to the API.

    The bot polls Telegram for commands and answers them with read-only
    queries. It is skipped when no token is configured.
    """
    # Uvicorn only configures its own loggers, so the app's messages (the bot
    # starting and stopping) would otherwise be dropped.
    logging.basicConfig(level=logging.INFO)
    # httpx logs every request URL, and the Telegram API keeps the bot token in it.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    bot = None
    if settings.telegram_bot_token:
        try:
            bot = await start_bot(settings.telegram_bot_token)
        except Exception:
            # A Telegram outage must not take the API down with it.
            logger.exception("Could not start the Telegram bot")
    try:
        yield
    finally:
        if bot is not None:
            await stop_bot(bot)


app = FastAPI(title="ServeEasy API", lifespan=lifespan)
app.include_router(listings.router)
app.include_router(cafeterias.router)
app.include_router(meals.router)
app.include_router(requests.router)
app.include_router(notifications.router)
app.include_router(services.router)
app.include_router(shops.router)
app.include_router(me.router)
app.include_router(uploads.router)


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "reachable"}
