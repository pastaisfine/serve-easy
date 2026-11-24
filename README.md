# ServeEasy

ServeEasy is a centralized campus marketplace for Universiti Teknologi Malaysia (UTM). It brings secondhand goods, cafeteria meal ordering, campus services, student enterprises, and in-app requests into one place instead of relying on scattered WhatsApp and Telegram groups.

## Deployed application

**Live:** [https://serve-easy-lilac.vercel.app](https://serve-easy-lilac.vercel.app)

## Features

- User sign-up and sign-in with Neon Auth
- Student profiles with optional public WhatsApp and Telegram contact details
- Secondhand marketplace listings with photos, categories, prices, conditions, and campus meetup spots
- Listing search and filtering by category, condition, price, and keywords
- Product purchase requests with pending, accepted, declined, completed, and cancelled states
- Cafeteria menus for lunch and dinner sessions with provider contacts
- Multi-item meal ordering with pickup-point and provider details
- Cafeteria-side meal and delivery management
- Campus service listings and service booking requests
- Student enterprise (shop) profiles that display their listings and services
- In-app notifications for marketplace request updates
- Unread notification counts and order/booking history
- Telegram bot commands for searching listings, services, cafeterias, menus, and shops

## Tech stack

### Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- shadcn/ui and Base UI
- Lucide icons
- Neon Auth
- Vitest and Playwright

### Backend

- Python 3.13+
- FastAPI
- SQLAlchemy 2
- Alembic
- Pydantic Settings
- Uvicorn
- PostgreSQL on Neon
- Neon Object Storage (S3-compatible)
- python-telegram-bot
- pytest

### Infrastructure and tooling

- Vercel deployment
- Neon Postgres and Neon Auth
- `uv` for Python dependency and environment management
- npm for frontend dependencies

## Project structure

```text
.
├── frontend/   Next.js web application
├── backend/    FastAPI API, database models, migrations, seed data, and Telegram bot
├── PRD.md      Product requirements and feature specification
└── docs/       Architecture decisions and project documentation
```

## Run locally

### Prerequisites

- Node.js 20 or newer
- npm
- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- Access to a Neon Postgres database and Neon Auth branch

### 1. Configure the backend

```bash
cd backend
cp .env.example .env
```

Fill in the database, Neon Auth, and optional object-storage values in `backend/.env`. At minimum, the API needs:

- `DATABASE_URL`
- `DATABASE_URL_UNPOOLED`
- `NEON_AUTH_BASE_URL`
- `NEON_AUTH_JWKS_URL`

Install dependencies:

```bash
uv sync
```

Apply database migrations and load the demo data:

```bash
uv run alembic upgrade head
uv run python -m app.seed
```

Start the API:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`, with interactive documentation at `http://localhost:8000/docs`.

### 2. Configure the frontend

Open a second terminal:

```bash
cd frontend
cp .env.example .env.local
```

Set `SERVE_API_URL=http://localhost:8000`. Configure the Neon Auth and storage values in `frontend/.env.local` if those integrations are enabled.

Install and start the frontend:

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## Optional Telegram bot

Set `TELEGRAM_BOT_TOKEN` in `backend/.env`, then restart the backend. The bot will share the API's database and answer read-only marketplace queries.

Run the API with a single Uvicorn worker so that only one Telegram polling loop is started.

## Testing

Frontend:

```bash
cd frontend
npm run typecheck
npm test
npm run lint
```

Backend:

```bash
cd backend
uv run pytest
```
