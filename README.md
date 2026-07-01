# Momentum Backtester

A full-stack web app for backtesting momentum trading strategies.

- **Backend:** Python + [FastAPI](https://fastapi.tiangolo.com/)
- **Frontend:** React + [Vite](https://vite.dev/) + [Tailwind CSS](https://tailwindcss.com/)

## Project structure

```
momentum-backtester/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── routers/         # HTTP route definitions
│   │   ├── services/        # Business logic
│   │   └── models/          # Pydantic schemas
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx          # Main page (fetches /api/health)
    │   ├── main.jsx         # React entry point
    │   └── index.css        # Tailwind entry point
    ├── index.html
    ├── vite.config.js       # Dev-server proxy to the backend
    └── package.json
```

## Prerequisites

- Python 3.10+
- Node.js 18+ (20+ recommended)

## Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API is now running at http://localhost:8000. Verify it:

```bash
curl http://localhost:8000/api/health
# {"status":"ok"}
```

Interactive API docs are available at http://localhost:8000/docs.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. You should see the Momentum Backtester page
with a green **API status: ok** badge, confirming the frontend can reach
the backend.

## How the connection works

- The Vite dev server proxies any request starting with `/api` to the
  backend at `http://localhost:8000` (see `frontend/vite.config.js`), so
  the frontend can use relative URLs with no CORS issues in development.
- The backend also allows CORS from `http://localhost:5173` (see
  `backend/app/main.py`) in case you want to call it directly.

## Adding new endpoints

Follow the existing health-check pattern:

1. Define the request/response schema in `backend/app/models/`.
2. Put the logic in a function in `backend/app/services/`.
3. Expose it via a router in `backend/app/routers/` and include the
   router in `backend/app/main.py`.
