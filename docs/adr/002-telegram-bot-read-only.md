# ADR-002: The Telegram bot reads the database directly, read-only

**Date:** 2026-11-13  
**Status:** accepted  
**Deciders:** pastaisfine  
**Context:** Students browse the marketplace in WhatsApp and Telegram groups today. A bot that answers questions about the listings, services and menus should read the same data the app shows, without a second source of truth.

## Decision

Run the Telegram bot **inside the FastAPI app**, and let it read the **Neon database directly**
over a **read-only** connection. It never calls the HTTP API and never writes.

## Details

### Where it runs

The bot is started by the FastAPI lifespan (`app/main.py`) and stopped on shutdown. One process
runs the API and the bot. A Telegram outage at startup is logged and does not stop the API.

The bot must run with a **single worker**: two polling loops on one token make Telegram answer
`409 Conflict`. `--reload` is fine.

### How it reads

`app/bot/queries.py` builds its own engine from the same pooled `DATABASE_URL` and sets
`SET TRANSACTION READ ONLY` on every transaction it opens. Postgres then refuses any `INSERT`,
`UPDATE`, `DELETE` or DDL from the bot, even if a handler has a bug.

The flag is set **per transaction**, not per connection. Neon hands each transaction to whichever
pooled server connection is free, so a connection-level setting would not stick and could leak to
another client.

The API keeps its own engine without the flag, so its write routes are unaffected.

### What it shows

Every query returns the same Pydantic schemas the HTTP API uses (`ListingOut`, `ServiceOut`,
`MenuOut`, `ShopOut`). The bot therefore shows the same fields as the app and cannot expose an
email address, phone number or student id, because those are already missing from the schemas.

### Why not call the API

The API would have to be deployed and reachable from wherever the bot runs, and its routes would
need a public contract for the bot. Reading the database is one hop fewer and gives the bot free
access to the joins it needs.

The cost is duplicated filter logic: the bot's `search_listings` mirrors `GET /listings`. The two
must be kept in step when the filters change.

## Rationale

| Option | Pros | Cons |
|-------|------|------|
| Direct read, read-only transaction (chosen) | one hop fewer; the database enforces the read-only rule; no deployment needed | filter logic is duplicated from the API |
| Direct read, no guard | simplest | a bug could write to the marketplace |
| Call the HTTP API | no duplicated logic | needs a deployed API; the bot depends on it being up |
| Separate read-only Neon role | the credential itself cannot write | needs a second login and a DDL step; pooler semantics still matter |

## Consequences

- **Positive:** the bot cannot corrupt the marketplace by accident; no second deployment to run.
- **Negative:** filter logic exists in two places; the bot adds `python-telegram-bot` to the
  backend's dependencies.
- **Later:** a dedicated `SELECT`-only Neon role would harden this further, and an allowlist of
  Telegram user IDs would restrict who can query the bot. Neither is in place yet.

## Verification

1. `SHOW transaction_read_only` returns `on` inside a bot session.
2. An `UPDATE` from a bot session raises `ReadOnlySqlTransaction`.
3. Every reply shows only `id`, `name`, `image` and `faculty` for a seller or provider.
4. `uvicorn app.main:app` starts the bot and `/listings calculator` answers with real listings.
