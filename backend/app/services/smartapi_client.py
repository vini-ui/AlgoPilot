"""
SmartAPI Client - Handles Angel One SmartAPI authentication and API calls
"""
import httpx
import json
import socket
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


class SmartAPIClient:
    """
    Client for Angel One SmartAPI integration.
    Handles authentication, session management, and API calls.
    """
    
    BASE_URL_WS = "wss://smartapisocket.angelone.in/smart-stream"
    
    def __init__(self, api_key: str, secret_key: str, client_id: str, mpin: str, base_url: str = "https://apiconnect.angelbroking.com"):
        """
        Initialize SmartAPI client.
        
        Args:
            api_key: SmartAPI API Key
            secret_key: SmartAPI Secret Key
            client_id: Angel One Client ID (Client Code)
            mpin: Angel One MPIN (Mobile Personal Identification Number)
            base_url: SmartAPI base URL (default: https://apiconnect.angelbroking.com)
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.client_id = client_id
        self.mpin = mpin
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.feed_token: Optional[str] = None
        self._public_ip: Optional[str] = None
        self._local_ip: Optional[str] = None
    
    def _get_local_ip(self) -> str:
        """Get local IP address."""
        if self._local_ip:
            return self._local_ip
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self._local_ip = s.getsockname()[0]
            s.close()
            return self._local_ip
        except Exception:
            return "192.168.1.1"
    
    async def _get_public_ip(self) -> str:
        """Get public IP address."""
        if self._public_ip:
            return self._public_ip
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try multiple services to get public IP
                services = [
                    "https://api.ipify.org",
                    "https://ifconfig.me/ip",
                    "https://icanhazip.com"
                ]
                for service in services:
                    try:
                        response = await client.get(service)
                        if response.status_code == 200:
                            self._public_ip = response.text.strip()
                            return self._public_ip
                    except Exception:
                        continue
        except Exception:
            pass
        # Fallback to local IP if public IP cannot be determined
        return self._get_local_ip()
        
    async def generate_session_by_password(self, totp: str) -> Dict[str, Any]:
        """
        Generate user session using password (MPIN) and TOTP via loginByPassword endpoint.
        
        Args:
            totp: Time-based One-Time Password from authenticator app
            
        Returns:
            Session data including access_token, refresh_token, feed_token
        """
        url = f"{self.base_url}/rest/auth/angelbroking/user/v1/loginByPassword"
        
        payload = {
            "clientcode": self.client_id,
            "password": self.mpin,  # MPIN is used as password
            "totp": totp
        }
        
        return await self._make_auth_request(url, payload)
    
    async def generate_session(self, totp: str) -> Dict[str, Any]:
        """
        Generate user session using MPIN and TOTP (legacy method, uses loginByMPIN).
        
        Args:
            totp: Time-based One-Time Password from authenticator app
            
        Returns:
            Session data including access_token, refresh_token, feed_token
        """
        url = f"{self.base_url}/rest/auth/angelbroking/user/v1/loginByMPIN"
        
        payload = {
            "clientcode": self.client_id,
            "mpin": self.mpin,
            "totp": totp
        }
        
        return await self._make_auth_request(url, payload)
    
    async def _make_auth_request(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Common method to make authentication requests.
        
        Args:
            url: API endpoint URL
            payload: Request payload
            
        Returns:
            Session data or error response
        """
        
        # Get actual IP addresses
        local_ip = self._get_local_ip()
        public_ip = await self._get_public_ip()
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": local_ip,
            "X-ClientPublicIP": public_ip,
            "X-MACAddress": "00:00:00:00:00:00",  # MAC address not critical
            "X-PrivateKey": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                
                # Log for debugging
                print(f"API Request URL: {url}")
                print(f"API Response Status: {response.status_code}")
                print(f"API Response Headers: {dict(response.headers)}")
                
                # Try to parse JSON response first
                # If that fails, get the text for error reporting
                try:
                    data = response.json()
                except (ValueError, json.JSONDecodeError) as json_err:
                    # If JSON parsing fails, get the raw text for error reporting
                    try:
                        response_text = response.text
                    except Exception:
                        response_text = ""
                    
                    print(f"JSON parsing error: {json_err}")
                    print(f"Response text (first 500 chars): {response_text[:500] if response_text else '(empty)'}")
                    
                    # Check if response is empty
                    if not response_text or not response_text.strip():
                        return {
                            "success": False,
                            "error": f"Empty response from API (Status: {response.status_code}). Please check your API credentials, base URL ({self.base_url}), and ensure your IP is whitelisted.",
                            "status_code": response.status_code,
                            "requires_totp": True
                        }
                    
                    # Return error with raw response
                    return {
                        "success": False,
                        "error": f"Invalid JSON response from API. Status: {response.status_code}, Response: {response_text[:500]}",
                        "status_code": response.status_code,
                        "raw_response": response_text[:500],
                        "requires_totp": True
                    }
                
                # Check response status
                if response.status_code != 200:
                    error_msg = data.get("message", f"HTTP {response.status_code}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "status_code": response.status_code,
                        "data": data,
                        "requires_totp": response.status_code == 401 or "totp" in str(data).lower()
                    }
                
                if data.get("status") and data.get("data"):
                    session_data = data["data"]
                    self.access_token = session_data.get("jwtToken")
                    self.refresh_token = session_data.get("refreshToken")
                    self.feed_token = session_data.get("feedToken")
                    
                    # Token expiry (typically 24 hours, but check response)
                    # SmartAPI tokens usually expire in 24 hours
                    self.token_expiry = datetime.now() + timedelta(hours=24)
                    
                    return {
                        "success": True,
                        "access_token": self.access_token,
                        "refresh_token": self.refresh_token,
                        "feed_token": self.feed_token,
                        "expiry": self.token_expiry.isoformat() if self.token_expiry else None
                    }
                else:
                    error_msg = data.get("message", "Failed to generate session")
                    return {
                        "success": False,
                        "error": error_msg,
                        "data": data,
                        "requires_totp": "totp" in error_msg.lower() or "otp" in error_msg.lower()
                    }
            except httpx.HTTPStatusError as e:
                # Try to get error text
                try:
                    error_text = e.response.text
                    error_data = e.response.json() if e.response.text else {}
                except (ValueError, json.JSONDecodeError):
                    error_text = e.response.text or "No error message"
                    error_data = {}
                
                # Check for IP whitelisting error
                if "rejected" in error_text.lower() or e.response.status_code == 403:
                    return {
                        "success": False,
                        "error": f"Request rejected. This usually means:\n"
                                f"1. Your IP address ({public_ip}) is not whitelisted in SmartAPI dashboard\n"
                                f"2. Go to SmartAPI dashboard and add your IP to whitelist\n"
                                f"3. Support ID: {error_text}",
                        "status_code": e.response.status_code,
                        "public_ip": public_ip,
                        "requires_ip_whitelist": True
                    }
                
                error_msg = error_data.get("message", error_text) if error_data else error_text
                return {
                    "success": False,
                    "error": f"HTTP {e.response.status_code}: {error_msg}",
                    "status_code": e.response.status_code,
                    "public_ip": public_ip,
                    "requires_totp": e.response.status_code == 401 or "totp" in error_msg.lower()
                }
            except httpx.RequestError as e:
                return {
                    "success": False,
                    "error": f"Request failed: {str(e)}",
                    "requires_totp": True
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "requires_totp": True
                }
    
    async def refresh_session(self) -> Dict[str, Any]:
        """
        Refresh the access token using refresh token.
        
        Returns:
            Updated session data
        """
        if not self.refresh_token:
            return {
                "success": False,
                "error": "No refresh token available"
            }
        
        url = f"{self.base_url}/rest/auth/angelbroking/jwt/v1/generateTokens"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.refresh_token}"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") and data.get("data"):
                    session_data = data["data"]
                    self.access_token = session_data.get("jwtToken")
                    self.feed_token = session_data.get("feedToken")
                    self.token_expiry = datetime.now() + timedelta(hours=24)
                    
                    return {
                        "success": True,
                        "access_token": self.access_token,
                        "feed_token": self.feed_token,
                        "expiry": self.token_expiry.isoformat() if self.token_expiry else None
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("message", "Failed to refresh session")
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
    
    def is_token_valid(self) -> bool:
        """Check if the current access token is still valid."""
        if not self.access_token or not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers with authentication token."""
        if not self.access_token:
            raise ValueError("No access token available. Please generate session first.")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "192.168.1.1",
            "X-ClientPublicIP": "192.168.1.1",
            "X-MACAddress": "00:00:00:00:00:00",
            "X-PrivateKey": self.api_key
        }
    
    async def get_profile(self) -> Dict[str, Any]:
        """Get user profile information."""
        url = f"{self.base_url}/rest/secure/angelbroking/user/v1/getProfile"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self._get_auth_headers(), timeout=30.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def place_order(
        self,
        symbol: str,
        exchange: str,
        transaction_type: str,  # BUY or SELL
        order_type: str,  # MARKET, LIMIT, STOPLOSS_LIMIT, etc.
        quantity: int,
        price: float = 0.0,
        product_type: str = "INTRADAY",  # INTRADAY, DELIVERY, MARGIN, etc.
        validity: str = "DAY"  # DAY, IOC, etc.
    ) -> Dict[str, Any]:
        """
        Place an order.
        
        Args:
            symbol: Trading symbol (e.g., "NIFTY", "RELIANCE")
            exchange: Exchange (NSE, BSE, NFO, etc.)
            transaction_type: BUY or SELL
            order_type: MARKET, LIMIT, STOPLOSS_LIMIT, etc.
            quantity: Order quantity
            price: Order price (0 for MARKET orders)
            product_type: INTRADAY, DELIVERY, MARGIN, etc.
            validity: DAY, IOC, etc.
        """
        url = f"{self.base_url}/rest/secure/angelbroking/order/v1/placeOrder"
        
        payload = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": "",  # Will be fetched from symbol master if needed
            "transactiontype": transaction_type,
            "exchange": exchange,
            "ordertype": order_type,
            "producttype": product_type,
            "duration": validity,
            "price": str(price),
            "squareoff": "0",
            "stoploss": "0",
            "quantity": str(quantity)
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_auth_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def get_positions(self) -> Dict[str, Any]:
        """Get current positions."""
        url = f"{self.base_url}/rest/secure/angelbroking/portfolio/v1/getPosition"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self._get_auth_headers(), timeout=30.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def get_holdings(self) -> Dict[str, Any]:
        """Get holdings."""
        url = f"{self.base_url}/rest/secure/angelbroking/portfolio/v1/getHolding"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self._get_auth_headers(), timeout=30.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def get_order_book(self) -> Dict[str, Any]:
        """Get order book."""
        url = f"{self.base_url}/rest/secure/angelbroking/order/v1/getOrderBook"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self._get_auth_headers(), timeout=30.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def get_trade_book(self) -> Dict[str, Any]:
        """Get trade book (executed orders)."""
        url = f"{self.base_url}/rest/secure/angelbroking/order/v1/getTradeBook"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self._get_auth_headers(), timeout=30.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def cancel_order(self, order_id: str, variety: str = "NORMAL") -> Dict[str, Any]:
        """Cancel an order."""
        url = f"{self.base_url}/rest/secure/angelbroking/order/v1/cancelOrder"
        
        payload = {
            "variety": variety,
            "orderid": order_id
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_auth_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def modify_order(
        self,
        order_id: str,
        order_type: str,
        product_type: str,
        duration: str,
        price: str,
        quantity: str,
        variety: str = "NORMAL"
    ) -> Dict[str, Any]:
        """Modify an existing order."""
        url = f"{self.base_url}/rest/secure/angelbroking/order/v1/modifyOrder"
        
        payload = {
            "variety": variety,
            "orderid": order_id,
            "ordertype": order_type,
            "producttype": product_type,
            "duration": duration,
            "price": price,
            "quantity": quantity
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_auth_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def get_funds(self) -> Dict[str, Any]:
        """Get available funds and margin details (RMS)."""
        url = f"{self.base_url}/rest/secure/angelbroking/user/v1/getRMS"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self._get_auth_headers(), timeout=30.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def get_market_status(self) -> Dict[str, Any]:
        """Get market status (open/close)."""
        url = f"{self.base_url}/rest/secure/angelbroking/market/v1/getMarketStatus"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self._get_auth_headers(), timeout=30.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def get_quote(
        self,
        mode: str = "FULL",
        exchange_tokens: Dict[str, List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get real-time quote for symbols.
        
        Args:
            mode: Quote mode (FULL, LTP, etc.)
            exchange_tokens: Dict mapping exchange to list of symbol tokens
                Example: {"NSE": ["3045", "11536"]}
        """
        url = f"{self.base_url}/rest/secure/angelbroking/market/v1/getQuote"
        
        payload = {
            "mode": mode,
            "exchangeTokens": exchange_tokens or {}
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_auth_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def get_symbol_master(self) -> Dict[str, Any]:
        """Get symbol master data for all exchanges. Large file, use for reference."""
        url = f"{self.base_url}/rest/secure/angelbroking/market/v1/getSymbolMaster"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self._get_auth_headers(), timeout=60.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def logout(self) -> Dict[str, Any]:
        """Logout and invalidate current session."""
        url = f"{self.base_url}/rest/secure/angelbroking/user/v1/logout"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self._get_auth_headers(), timeout=30.0)
                response.raise_for_status()
                # Clear tokens on successful logout
                self.access_token = None
                self.refresh_token = None
                self.feed_token = None
                self.token_expiry = None
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def get_market_data(
        self,
        exchange: str,
        symbol_token: str,
        interval: str = "ONE_MINUTE"
    ) -> Dict[str, Any]:
        """
        Get historical market data.
        
        Args:
            exchange: Exchange (NSE, BSE, NFO, etc.)
            symbol_token: Symbol token
            interval: ONE_MINUTE, FIVE_MINUTE, etc.
        """
        url = f"{self.base_url}/rest/secure/angelbroking/historical/v1/getCandleData"
        
        payload = {
            "exchange": exchange,
            "symboltoken": symbol_token,
            "interval": interval,
            "fromdate": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M"),
            "todate": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_auth_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}

