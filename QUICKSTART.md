# Quick Start Guide

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- **SQLite** (usually comes with Python)

## Initial Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`
API documentation (Swagger UI) will be at `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## First Steps

1. **Register a User**
   - Open the app in your browser (`http://localhost:5173`)
   - You'll see the login page
   - For now, you'll need to register via the API:
     ```bash
     curl -X POST http://localhost:8000/api/register \
       -H "Content-Type: application/json" \
       -d '{"username": "testuser", "password": "testpass123"}'
     ```

2. **Login**
   - Use the credentials you just created to login through the UI

3. **Add an App**
   - After login, you'll see the App Selector page
   - Click "Add New App" to create your first Angel One account configuration
   - Note: Full SmartAPI integration is still TODO, so this is just the UI for now

4. **Create a Strategy**
   - Switch to an app, then navigate to Strategies
   - Create your first strategy
   - Start/stop strategies (execution engine is placeholder for now)

## Project Structure

```
AlgoPilot/
├── frontend/          # Vue 3 + Vite + Tailwind CSS
│   └── src/
│       ├── pages/    # All page components
│       ├── store/    # Pinia stores
│       ├── api/      # API client
│       └── router/   # Vue Router
├── backend/          # FastAPI
│   └── app/
│       ├── api/      # REST endpoints
│       ├── models/   # Database models
│       ├── services/ # Business logic
│       └── main.py   # FastAPI app entry
└── docs/             # Documentation
```

## Development Status

✅ **Completed:**
- Project structure and scaffolding
- All UI pages with Tailwind styling
- Database models and API endpoints
- Authentication system
- Indicator engine functions (RSI, Stochastic, Pivot, MA/EMA)

🚧 **In Progress:**
- SmartAPI integration
- WebSocket live data streaming
- Strategy execution engine
- Encryption for app secrets

See `docs/project-scope.md` for detailed architecture and progress.

## Troubleshooting

### Backend won't start
- Make sure you're in the virtual environment
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.10+)

### Frontend won't start
- Make sure Node.js 18+ is installed: `node --version`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check that the backend is running on port 8000

### Database issues
- The SQLite database (`algopilot.db`) is created automatically on first run
- If you need to reset, delete `algopilot.db` and restart the backend

## Next Steps

1. Implement SmartAPI client integration
2. Add encryption for storing API keys
3. Build WebSocket endpoint for live market data
4. Complete strategy execution engine
5. Add charting for strategy visualization

