"""
Session Manager - Handles SmartAPI connections and per-app runtime sessions
"""
from typing import Optional, Dict
from app.models import App, AppSecret


class SessionManager:
    """
    Manages active app sessions and SmartAPI connections.
    Only one app session can be active at a time.
    """
    _instance = None
    _active_app_id: Optional[int] = None
    _active_session: Optional[Dict] = None

    def __init__(self):
        if SessionManager._instance is not None:
            raise Exception("SessionManager is a singleton")
        SessionManager._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def activate(self, app_id: int, app: App, secrets: AppSecret) -> bool:
        """
        Activate an app session.
        - Decrypts credentials
        - Connects to SmartAPI
        - Opens WebSocket for market data
        - Loads strategies into memory
        """
        # TODO: Implement SmartAPI connection
        # 1. Decrypt secrets using device key
        # 2. Call SmartAPI generateSession
        # 3. Open WebSocket subscriptions
        # 4. Load strategies
        
        self._active_app_id = app_id
        self._active_session = {
            "app_id": app_id,
            "token": None,  # Will be set after SmartAPI login
            "ws_connection": None
        }
        
        return True

    async def deactivate(self):
        """
        Gracefully stop the active session.
        - Stop running strategies
        - Close WebSocket
        - Persist state
        """
        if self._active_session:
            # TODO: Implement graceful shutdown
            self._active_app_id = None
            self._active_session = None

    def get_active_app_id(self) -> Optional[int]:
        return self._active_app_id

    def is_active(self) -> bool:
        return self._active_app_id is not None

