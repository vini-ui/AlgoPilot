# Vue + Python Trading App — Project Architecture

**Created:** 2025-11-25

## 1. Project Summary

A local-first desktop/mobile-capable trading automation app that connects to Angel One (SmartAPI) accounts, computes indicators (Pivot Points, RSI, Stochastic, MAs), and runs user-defined strategies. The app UI is built with **Vue 3** (Options API) and the backend/business logic is in **Python (FastAPI)**. The app stores configuration and runtime state in a local **SQLite** database. Each configured "app" represents one Angel One account. Only one app may be active on the device at a time; users can switch between apps and mark an app as default.

Target users: retail algo traders who want a local, simple, robust automation platform.

---

## 2. Key requirements & constraints

* Multi-account (multi-app) support in a single user login. Each app = one Angel One account config.
* Single device activation per app at any time (the app will detect conflicting sessions and prompt to deactivate other device if needed).
* Local-first architecture: use **SQLite** for all local persistence initially; design the schema to be migratable to Postgres/Timescale later.
* Realtime feeds via SmartAPI WebSocket for ticks; REST for order placement/historical fetch.
* Indicator engine: pivot points, RSI, Stochastic, MAs implemented in Python using pandas/pandas_ta.
* Strategy lifecycle: create/list/enable/disable/execute/stop; strategy detail view with parameters and logs.
* Security: store API keys securely on-device (encrypted at rest). Provide a master login PIN or password for app unlock.

---

## 3. High-level architecture

```
[Vue Frontend] <--> [FastAPI Backend] <--> [SmartAPI (Angel One)]
       |                 |  
       |                 +--> [Local SQLite DB]
       |                 +--> [Indicator Engine (pandas, pandas_ta)]
       |                 +--> [Workers / Background Tasks]
       +--> WebSocket/REST
```

* **Frontend (Vue)**: UI, local views, sends user commands to backend (start strategy, switch app, edit config) and subscribes to backend WebSocket for live data, signals and logs.
* **Backend (FastAPI)**: single process/service that handles SmartAPI sessions, indicator computations, strategy evaluation loop(s), order execution wrapper, and provides REST & WebSocket endpoints to the UI. Uses a local SQLite DB for persistence.
* **SmartAPI**: remote broker API for market data and trade execution.

Notes:

* The backend is the single source of truth for strategy execution. The frontend is thin and stateless beyond cached UI settings.
* For dev/test, the backend supports a `paper_mode` or `simulate` flag where order calls are logged but not sent to SmartAPI.

---

## 4. User flows

### 4.1 Login

* App launches -> show login screen (Master credentials or device PIN).
* On first use, the user creates a master password/PIN and this will be used to encrypt local secrets (per-device).
* Successful login goes to **App Selector**.

### 4.2 App Selector

* Shows list of configured apps (each row: App Name, Account ID/email, status (active/inactive), `Make Default` checkbox).
* Options: `Add New App`, `Edit`, `Delete`, `Switch to App`, `Make Default`.
* If multiple apps exist, user can mark one as default — that app will auto-select on login.
* When user **Switches to App** the backend loads that app's credentials into an active runtime session and **applies that app's configuration** globally (strategies, risk limits, default symbols, etc.).

### 4.3 Dashboard (blank for now)

* After selecting an app, backend opens the active session and the user sees the overall dashboard (empty screen placeholder for now).

### 4.4 Strategy List

* Screen lists strategies for the active app: strategy name, type, status (running/paused/disabled), last run time, P&L (if applicable), actions (Start/Stop/Edit/View Logs/Delete).
* Bulk actions: Start All, Stop All, Export/Import strategies.

### 4.5 Strategy Detail

* Show parameters (lookback, thresholds, lot size), status, last runs, trades executed (log), and a simple timeline chart (candles) with indicators overlay.
* Buttons: `Run Now (single tick)`, `Start (continuous)`, `Pause`, `Backtest` (uses historical OHLC + OI if available), `Edit Parameters`.

---

## 5. Data model (SQLite schema)

Tables (initial):

* `users` (app-level master user credentials)
* `apps` (each row = one AngelOne account configuration)
* `app_secrets` (encrypted tokens/refresh tokens/keys) — linked to apps
* `strategies` (per app)
* `strategy_params` (JSON blob for parameters)
* `strategy_runs` (instances of runs/executions)
* `orders` (order logs & metadata)
* `ticks` (optional, rolling storage for most recent N ticks per symbol)
* `ohlc` (historical OHLC for backtesting, optional; could also store references to CSVs)
* `settings` (global and per-app settings)

### 5.1 Example simplified CREATE TABLEs (SQLite)

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE apps (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  account_id TEXT NOT NULL,
  is_default INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE app_secrets (
  id INTEGER PRIMARY KEY,
  app_id INTEGER NOT NULL,
  secret_key TEXT NOT NULL, -- encrypted blob
  api_key TEXT NOT NULL,    -- encrypted blob
  refresh_token TEXT,       -- encrypted
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(app_id) REFERENCES apps(id)
);

CREATE TABLE strategies (
  id INTEGER PRIMARY KEY,
  app_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  params_json TEXT,
  enabled INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(app_id) REFERENCES apps(id)
);

CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  app_id INTEGER NOT NULL,
  strategy_id INTEGER,
  order_id TEXT,
  symbol TEXT,
  qty INTEGER,
  price REAL,
  status TEXT,
  response_json TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

* Note: `secret_key/api_key` must be encrypted using a device-specific symmetric key derived from master password. Do not store plaintext API credentials.

---

## 6. Backend components & responsibilities

### 6.1 FastAPI server

* REST endpoints for UI: login, list apps, add/edit/delete app, switch app, list strategies, CRUD strategies, start/stop strategy, fetch logs, fetch orders, fetch backtest results.
* WebSocket endpoint to push live ticks, signals, order status updates to the Vue client.

### 6.2 Session manager (per-app runtime)

* Responsible for: connecting to SmartAPI (login/generate session), keeping token refreshed, opening WS for market data, maintaining a per-app in-memory runtime context (current positions, running strategies, runtime params).
* Only one app session may be active at a time. Switching apps will gracefully stop the previous app runtime (persist state) and start the new one.

### 6.3 Indicator Engine

* Python module that accepts OHLC or tick data and returns indicators: pivot points (daily), RSI (configurable period), Stochastic (%K/%D), MA/EMA.
* Designed to be stateless and functional (pure functions) so unit testing is easy.
* Use `pandas` + `pandas_ta` or `ta` packages.

### 6.4 Strategy Engine

* Each strategy is an instance with a parameter set.
* Runs in background workers (FastAPI background tasks or a lightweight task runner like RQ/Celery if needed later). For initial local app, FastAPI background tasks suffice.
* Strategy has lifecycle: `initialized` -> `running` -> `paused` -> `stopped`.
* On each new completed candle or OI update, the strategy evaluates conditions and may emit a trade intent.

### 6.5 Execution Layer

* Receives trade intents, applies risk checks, sequencing (rate limiting, order size limits), then calls SmartAPI REST to place/modify/cancel orders.
* Stores the raw order and response in `orders` table.
* Supports `paper_mode` where orders are logged but not executed.

### 6.6 Storage & Persistence

* SQLite via SQLAlchemy (or `databases` lib) for DB access.
* Local file-store for large assets (CSV exports, logs, chart images).

---

## 7. Frontend (Vue) components & pages

### 7.1 Pages

* **LoginPage** — master login/PIN creation & unlock.
* **AppSelectorPage** — list of configured apps, add/edit/delete, make default, switch app.
* **DashboardPage** — overall app dashboard (blank placeholder initially).
* **StrategyListPage** — lists strategies for current app.
* **StrategyDetailPage** — shows strategy parameters, run controls, logs, and minimal chart overlay.
* **SettingsPage** — global and per-app settings (paper_mode, default lot size, API reauth)

### 7.2 Re-usable components

* `AppCard` (single app row on selector)
* `StrategyCard` (summary in list)
* `IndicatorChart` (candles + overlays)
* `OrderLogTable`
* `Modal` (confirmations)
* `Toast` (notifications)

### 7.3 State management

* Use **Pinia**: store user state, active app, strategies, and live tick cache.
* WebSocket client subscribes to `/ws/live` after an app is active; pushes updates into Pinia store.

### 7.4 Security & Local Storage

* DO NOT store API keys in `localStorage`. The frontend never sees raw API secrets — only encrypted tokens (or a server-generated short-lived session token) are passed to the frontend.

---

## 8. APIs (REST & WebSocket)

### REST (examples)

* `POST /api/login` — authenticate user (local master password). Returns session token.
* `GET /api/apps` — list apps for logged-in user.
* `POST /api/apps` — add a new app (body contains account_id, encrypted api_key blob)
* `POST /api/apps/{id}/switch` — switch active app. Backend will activate app session.
* `GET /api/strategies` — list strategies for active app.
* `POST /api/strategies` — create new strategy.
* `POST /api/strategies/{id}/start` — start strategy.
* `POST /api/strategies/{id}/stop` — stop strategy.
* `GET /api/orders` — fetch orders for active app.

### WebSocket

* `ws://<host>/ws/live` — after authentication (token in query header), server pushes:

  * `tick` messages: `{type: 'tick', symbol, ts, price, volume, oi}`
  * `indicator` messages: `{type: 'indicator', symbol, indicator_name, value, ts}`
  * `signal` messages: `{type: 'signal', strategy_id, action, confidence, ts}`
  * `order_update` messages: `{type: 'order', order_id, status, details}`

---

## 9. Session & App-switch logic (detailed)

1. **App activation**

   * User selects or defaults an app.
   * Backend reads `app_secrets` blob, decrypts credentials using device-key derived from master password, and attempts to `generateSession` with SmartAPI.
   * On success, backend opens websocket subscription(s) for required symbols and loads strategies into memory.

2. **Single-device enforcement**

   * When activating, backend calls SmartAPI session endpoint and checks if the session token indicates another active device (if SmartAPI supports this). If SmartAPI doesn't provide device-level locks, implement a local `activation` flag with a small TTL and rely on the user to deactivate other devices.
   * Optionally maintain a small `activation_log` table with last activation timestamp and device id to detect stale activations.

3. **Switching apps**

   * On `POST /api/apps/{id}/switch`: backend gracefully stops running strategies for the currently active app, persists runtime state, closes WS, revokes tokens if needed, and starts runtime for the new app.
   * Frontend receives `app_switched` event and refreshes UI (strategy list, dashboard).

---

## 10. Indicator computation details

* Use a `IndicatorEngine` module with functions:

  * `compute_pivot(previous_day_ohlc)` -> returns pivot, R1,R2,S1,S2
  * `compute_rsi(series, length=14)` -> numeric
  * `compute_stochastic(h_series, l_series, c_series, k=14, d=3)` -> %K, %D
  * `compute_ma(series, window, type='sma'|'ema')`

* Indicators should be computed on completed candles (preferred) rather than per-tick to avoid unnecessary churn. For OI, you may evaluate on OI-change events as well.

* Provide a small `IndicatorCache` per-symbol to store last N values for fast incremental updates.

---

## 11. Strategy definition model

A strategy is a JSON object with fields like:

```json
{
  "id": "uuid",
  "name": "OI+RSI Breakout",
  "symbol": "NIFTY",
  "timeframe": "5min",
  "params": {
    "rsi_period": 14,
    "rsi_oversold": 30,
    "oi_increase_pct": 3.0,
    "ma_fast": 20,
    "ma_slow": 50,
    "max_qty": 1
  },
  "enabled": false
}
```

* Strategy evaluation will compare indicator outputs on new candles/oi updates and generate trade intents.

---

## 12. Backtesting & Simulation

* Implement a backtest runner that reads stored historical OHLC/OI (or CSV) and simulates the strategy with a configurable fill/slippage model.
* Output: trade log CSV, P&L summary, drawdown, win rate. Provide an import/export option for strategies.

---

## 13. Security & encryption

* Derive a device-specific symmetric key from user master password using PBKDF2 (or Argon2) and use AES-GCM to encrypt `app_secrets` fields before writing to SQLite.
* Use secure random device identifiers for activation records.
* Secure WebSocket with TLS (wss://).
* Store only hashed master password locally (argon2/bcrypt) and never the plaintext.

---

## 14. Logging, monitoring & debugging

* Local log files (rotating) stored per app.
* Structured logs: include timestamps, strategy id, symbol, action, error.
* UI: streaming logs in StrategyDetail page.
* For advanced monitoring, optionally add Sentry integration for error reporting.

---

## 15. Testing

* Unit tests for `IndicatorEngine` functions (edge cases). Use pytest.
* Integration tests for strategy lifecycle (start/stop) in `paper_mode`.
* E2E tests using a mocked SmartAPI server to test login, session, and order flows.

---

## 16. Developer / Folder structure

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
│  │  │   ├─ session_manager.py
│  │  │   ├─ indicator_engine.py
│  │  │   ├─ strategy_engine.py
│  │  │   └─ execution.py
│  │  ├─ models/ (sqlalchemy)
│  │  └─ workers/
│  └─ requirements.txt
├─ infra/
├─ docs/
└─ README.md
```

---

## 17. Deployment & run instructions (local dev)

1. Start backend in a Python virtualenv: `uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm install && npm run dev`
3. Create master password via Login screen and add an Angel One account in AppSelector.
4. Activate app and start a strategy in paper mode for testing.

---

## 18. Roadmap & optional future enhancements

* Replace SQLite with Postgres / TimescaleDB for long-term time-series storage.
* Add multi-device sync via optional cloud account (encrypted vault) and device management UI.
* Add enterprise/per-user rate-limit handling and premium data feeds.
* Add plugins for alternate brokers / data vendors.
* Add mobile-specific optimized UI with React Native or Capacitor/Vue Native.

---

## 19. Appendix: Quick sample REST endpoint implementation (FastAPI)

```python
# app/api/apps.py (simplified)
from fastapi import APIRouter, Depends, HTTPException
from app.models import AppModel, get_db_session
from app.services.session_manager import SessionManager

router = APIRouter(prefix="/api/apps")

@router.post("/add")
async def add_app(payload: dict, db=Depends(get_db_session)):
    # validate payload, encrypt secrets, insert into DB
    pass

@router.post("/{app_id}/switch")
async def switch_app(app_id: int, db=Depends(get_db_session)):
    # call SessionManager.activate(app_id)
    success = await SessionManager.activate(app_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot activate app")
    return {"ok": True}
```

---

## 20. Final notes

* This design emphasizes safety (paper mode, rate-limiting), testability (pure indicator functions), and a smooth UX for switching between multiple Angel One accounts. The SQLite-first approach keeps the app local and simple to start, while the modular backend allows future scaling to cloud or multi-device sync.

If you want, I can now:

* Generate the **full starter project scaffold** (Vue + FastAPI) with the database models and the indicator module implemented (RSI, Stochastic, Pivot, SMA/EMA) and a minimal UI with the pages you requested — ready to run locally.
* Or produce a **detailed API spec (OpenAPI)** and DB migration scripts for the schema above.

---

## 21. Development Progress

**Last Updated:** 2025-01-27

### ✅ Completed

#### Project Setup
- ✅ Created project folder structure (frontend, backend, docs, infra)
- ✅ Set up Vue 3 frontend with Vite and Tailwind CSS
- ✅ Set up FastAPI backend with basic structure
- ✅ Created SQLite database models and schema (SQLAlchemy)
- ✅ Set up basic API routes structure
- ✅ Created initial Vue pages and components structure
- ✅ Set up Pinia store for state management
- ✅ Created requirements.txt and package.json with dependencies

#### Frontend (Vue 3 + Tailwind)
- ✅ **Pages Implemented:**
  - LoginPage - Master login/PIN with authentication
  - AppSelectorPage - List, add, edit, delete apps; switch and set default
  - DashboardPage - Placeholder for future dashboard content
  - StrategyListPage - List strategies with start/stop/delete actions
  - StrategyDetailPage - View strategy details, parameters, and logs
  - SettingsPage - Global settings (paper_mode, default_lot_size)

- ✅ **State Management (Pinia):**
  - `auth` store - User authentication and session management
  - `app` store - Active app and apps list management
  - `strategy` store - Strategies list and active strategy

- ✅ **Infrastructure:**
  - Vue Router configured with all routes
  - Axios API client with interceptors for auth
  - WebSocket client plugin (ready for live data)
  - Tailwind CSS fully configured and integrated

#### Backend (FastAPI)
- ✅ **Database Models (SQLAlchemy):**
  - User model with password hashing
  - App model with user relationship
  - AppSecret model for encrypted credentials
  - Strategy model with params_json
  - StrategyRun model for execution tracking
  - Order model for order logs
  - Setting model for global/per-app settings

- ✅ **API Endpoints:**
  - `/api/login` - User authentication (JWT tokens)
  - `/api/register` - User registration
  - `/api/apps` - CRUD operations for apps
  - `/api/apps/{id}/switch` - Switch active app
  - `/api/apps/{id}/set-default` - Set default app
  - `/api/strategies` - CRUD operations for strategies
  - `/api/strategies/{id}/start` - Start strategy
  - `/api/strategies/{id}/stop` - Stop strategy
  - `/api/strategies/{id}/pause` - Pause strategy
  - `/api/strategies/{id}/run-now` - Single execution
  - `/api/strategies/start-all` - Start all strategies
  - `/api/strategies/stop-all` - Stop all strategies
  - `/api/orders` - List orders for active app
  - `/api/settings` - Get/update global settings

- ✅ **Services:**
  - `indicator_engine.py` - Indicator computation functions:
    - `compute_pivot()` - Pivot points calculation
    - `compute_rsi()` - RSI indicator
    - `compute_stochastic()` - Stochastic oscillator
    - `compute_ma()` - SMA/EMA moving averages
    - `IndicatorCache` - Cache for indicator values
  - `session_manager.py` - Placeholder for SmartAPI session management
  - `strategy_engine.py` - Placeholder for strategy execution lifecycle
  - `execution.py` - Placeholder for order execution with paper_mode support

- ✅ **Security:**
  - JWT token-based authentication
  - Password hashing with bcrypt
  - CORS middleware configured
  - API key encryption structure ready (needs implementation)

### 🚧 In Progress / TODO

#### Backend
- [ ] SmartAPI integration (session management, WebSocket connections)
- [ ] Encryption/decryption for app_secrets (AES-GCM with PBKDF2)
- [ ] WebSocket endpoint for live data streaming (`/ws/live`)
- [ ] Strategy execution engine implementation
- [ ] Real-time indicator computation on market data
- [ ] Order execution with SmartAPI REST API
- [ ] Single-device activation enforcement
- [ ] Background task workers for strategy evaluation

#### Frontend
- [ ] WebSocket integration for live updates
- [ ] Reusable components (AppCard, StrategyCard, IndicatorChart, OrderLogTable, Modal, Toast)
- [ ] Chart visualization for strategy detail page
- [ ] Real-time log streaming
- [ ] Error handling and user feedback improvements

#### Testing
- [ ] Unit tests for indicator_engine functions
- [ ] Integration tests for API endpoints
- [ ] E2E tests with mocked SmartAPI

#### Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] User guide
- [ ] Developer setup guide

### 📝 Notes

- The base project structure is complete and ready for development
- All core pages and API endpoints are scaffolded
- Database models are defined and ready for migrations
- Indicator engine functions are implemented and ready for testing
- SmartAPI integration is the next major milestone
- Paper trading mode is supported in the execution layer structure

### 🎯 Next Steps

1. Implement SmartAPI client library integration
2. Add encryption/decryption for app secrets
3. Implement WebSocket endpoint for live data
4. Build strategy execution engine
5. Add charting library for strategy visualization
6. Implement comprehensive error handling
