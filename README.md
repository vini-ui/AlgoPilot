# AlgoPilot - Trading Automation App

A local-first desktop/mobile-capable trading automation app that connects to Angel One (SmartAPI) accounts, computes indicators, and runs user-defined strategies.

## Tech Stack

- **Frontend**: Vue 3 (Options API) + Vite + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: SQLite (migratable to Postgres/TimescaleDB)
- **State Management**: Pinia
- **Real-time**: WebSocket

## Project Structure

```
project-root/
├─ frontend/                # Vue 3 app (Vite)
│  ├─ src/
│  │  ├─ pages/
│  │  ├─ components/
│  │  ├─ store/ (Pinia)
│  │  ├─ plugins/ws.js
│  │  └─ main.ts
│  └─ package.json
├─ backend/                 # FastAPI app (Python)
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ api/
│  │  ├─ services/
│  │  ├─ models/ (sqlalchemy)
│  │  └─ workers/
│  └─ requirements.txt
├─ infra/
├─ docs/
└─ README.md
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- SQLite

### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the backend:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Development Status

See `docs/project-scope.md` for detailed architecture and development progress.

## License

MIT

