"""
Session Manager - Handles SmartAPI connections and per-app runtime sessions
"""
from typing import Optional, Dict
from datetime import datetime, timedelta
from app.models import App, AppSecret
from app.services.smartapi_client import SmartAPIClient


class SessionManager:
    """
    Manages active app sessions and SmartAPI connections.
    Only one app session can be active at a time.
    """
    _instance = None
    _active_app_id: Optional[int] = None
    _active_session: Optional[Dict] = None
    _smartapi_client: Optional[SmartAPIClient] = None

    def __init__(self):
        if SessionManager._instance is not None:
            raise Exception("SessionManager is a singleton")
        SessionManager._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def activate(self, app_id: int, app: App, secrets: AppSecret, totp: Optional[str] = None) -> Dict:
        """
        Activate an app session.
        - Decrypts credentials
        - Connects to SmartAPI
        - Opens WebSocket for market data
        - Loads strategies into memory
        
        Args:
            app_id: App ID
            app: App model instance
            secrets: AppSecret model instance
            totp: Time-based One-Time Password (required for first login)
            
        Returns:
            Dict with success status and session info or error message
        """
        try:
            # TODO: Decrypt secrets using device key derived from master password
            # For now, using plaintext (NOT SECURE - needs encryption implementation)
            api_key = secrets.api_key
            secret_key = secrets.secret_key
            mpin = secrets.mpin
            client_id = app.account_id
            
            if not mpin:
                return {
                    "success": False,
                    "error": "MPIN is required for authentication. Please update the app with MPIN."
                }
            
            # Create SmartAPI client
            base_url = secrets.base_url or "https://apiconnect.angelbroking.com"
            self._smartapi_client = SmartAPIClient(
                api_key=api_key,
                secret_key=secret_key,
                client_id=client_id,
                mpin=mpin,
                base_url=base_url
            )
            
            # Generate session if TOTP provided using loginByPassword
            if totp:
                session_result = await self._smartapi_client.generate_session_by_password(totp)
                if not session_result.get("success"):
                    return {
                        "success": False,
                        "error": session_result.get("error", "Failed to generate session"),
                        "requires_totp": session_result.get("requires_totp", True)
                    }
            elif not self._smartapi_client.is_token_valid():
                # Try to refresh if we have refresh token
                if not self._smartapi_client.refresh_token:
                    return {
                        "success": False,
                        "error": "No active session. TOTP required to login.",
                        "requires_totp": True
                    }
                refresh_result = await self._smartapi_client.refresh_session()
                if not refresh_result.get("success"):
                    return {
                        "success": False,
                        "error": "Session expired. TOTP required.",
                        "requires_totp": True
                    }
            else:
                # No TOTP provided and token is valid, but we need to ensure we have tokens
                if not self._smartapi_client.access_token:
                    return {
                        "success": False,
                        "error": "No active session. TOTP required to login.",
                        "requires_totp": True
                    }
            
            self._active_app_id = app_id
            self._active_session = {
                "app_id": app_id,
                "access_token": self._smartapi_client.access_token,
                "feed_token": self._smartapi_client.feed_token,
                "token_expiry": self._smartapi_client.token_expiry.isoformat() if self._smartapi_client.token_expiry else None,
                "ws_connection": None  # TODO: Open WebSocket connection
            }
            
            return {
                "success": True,
                "app_id": app_id,
                "session": self._active_session
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def deactivate(self):
        """
        Gracefully stop the active session.
        - Stop running strategies
        - Close WebSocket
        - Persist state
        """
        if self._active_session:
            # TODO: Close WebSocket connection
            # TODO: Stop running strategies
            self._active_app_id = None
            self._active_session = None
            self._smartapi_client = None

    def get_active_app_id(self) -> Optional[int]:
        return self._active_app_id

    def is_active(self) -> bool:
        return self._active_app_id is not None
    
    def get_smartapi_client(self) -> Optional[SmartAPIClient]:
        """Get the active SmartAPI client instance."""
        return self._smartapi_client
    
    async def restore_session(self, app_id: int, app: App, secrets: AppSecret, session_data: Dict) -> bool:
        """
        Restore a session from stored session data.
        
        Args:
            app_id: App ID
            app: App model instance
            secrets: AppSecret model instance
            session_data: Stored session data with access_token, feed_token, etc.
            
        Returns:
            True if session was restored successfully, False otherwise
        """
        try:
            if not session_data or not session_data.get("access_token"):
                return False
            
            # Create SmartAPI client
            base_url = secrets.base_url or "https://apiconnect.angelbroking.com"
            self._smartapi_client = SmartAPIClient(
                api_key=secrets.api_key,
                secret_key=secrets.secret_key,
                client_id=app.account_id,
                mpin=secrets.mpin,
                base_url=base_url
            )
            
            # Restore tokens from session data
            self._smartapi_client.access_token = session_data.get("access_token")
            self._smartapi_client.refresh_token = session_data.get("refresh_token")
            self._smartapi_client.feed_token = session_data.get("feed_token")
            
            # Parse token expiry
            if session_data.get("token_expiry"):
                try:
                    self._smartapi_client.token_expiry = datetime.fromisoformat(session_data["token_expiry"])
                except:
                    self._smartapi_client.token_expiry = datetime.now() + timedelta(hours=24)
            
            # Check if token is still valid
            if not self._smartapi_client.is_token_valid():
                # Try to refresh if we have refresh token
                if self._smartapi_client.refresh_token:
                    refresh_result = await self._smartapi_client.refresh_session()
                    if not refresh_result.get("success"):
                        return False
                else:
                    return False
            
            # Set active session
            self._active_app_id = app_id
            self._active_session = session_data
            
            return True
        except Exception as e:
            print(f"Error restoring session: {e}")
            return False

