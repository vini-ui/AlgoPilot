"""
SmartAPI Client - Handles Angel One SmartAPI authentication and API calls
"""
import httpx
import json
import socket
import re
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
            "X-ClientLocalIP": self._get_local_ip(),
            "X-ClientPublicIP": self._get_local_ip(),  # Will be updated in async methods
            "X-MACAddress": "00:00:00:00:00:00",
            "X-PrivateKey": self.api_key
        }
    
    async def get_profile(self) -> Dict[str, Any]:
        """Get user profile information."""
        url = f"{self.base_url}/rest/secure/angelbroking/user/v1/getProfile"
        
        async with httpx.AsyncClient() as client:
            try:
                # Get real IP addresses for this request
                local_ip = self._get_local_ip()
                public_ip = await self._get_public_ip()
                
                headers = self._get_auth_headers()
                headers["X-ClientLocalIP"] = local_ip
                headers["X-ClientPublicIP"] = public_ip
                
                response = await client.get(url, headers=headers, timeout=30.0)
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
        print("-" * 80)
        print("SMARTAPI CLIENT: get_positions() called")
        
        # Use apiconnect.angelone.in for positions endpoint if base_url is angelbroking.com
        base_url_for_request = self.base_url
        if self.base_url == "https://apiconnect.angelbroking.com":
            base_url_for_request = "https://apiconnect.angelone.in"
        
        url = f"{base_url_for_request}/rest/secure/angelbroking/portfolio/v1/getPosition"
        print(f"Base URL: {self.base_url}")
        print(f"Request Base URL: {base_url_for_request}")
        print(f"Full URL: {url}")
        
        # Check token before making request
        if not self.access_token:
            print("ERROR: No access token available")
            return {
                "success": False,
                "error": "No access token available. Please login first."
            }
        
        if not self.is_token_valid():
            print("ERROR: Access token expired")
            return {
                "success": False,
                "error": "Access token expired. Please refresh session."
            }
        
        print(f"Access token valid: {self.is_token_valid()}")
        print(f"Access token (first 20 chars): {self.access_token[:20]}...")
        
        async with httpx.AsyncClient() as client:
            try:
                # Get real IP addresses for this request
                local_ip = self._get_local_ip()
                public_ip = await self._get_public_ip()
                print(f"Local IP: {local_ip}, Public IP: {public_ip}")
                
                headers = self._get_auth_headers()
                headers["X-ClientLocalIP"] = local_ip
                headers["X-ClientPublicIP"] = public_ip
                
                print(f"Request headers keys: {list(headers.keys())}")
                print(f"Authorization header present: {'Authorization' in headers}")
                print(f"X-PrivateKey present: {'X-PrivateKey' in headers}")
                
                print("Making GET request to SmartAPI...")
                response = await client.get(url, headers=headers, timeout=30.0)
                
                # Log response for debugging
                print(f"Response received - Status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                print(f"Response content length: {len(response.content) if response.content else 0}")
                print(f"Response text length: {len(response.text) if response.text else 0}")
                
                # Check HTTP status
                if response.status_code != 200:
                    # Check if response is HTML (indicates request was rejected by proxy/firewall)
                    if response.text and response.text.strip().startswith('<html'):
                        error_text = response.text[:500] if response.text else "No error message"
                        print(f"Positions API: Request rejected (HTML response): {error_text}")
                        # Extract support ID from HTML if present
                        support_id_match = re.search(r'support ID is:\s*(\d+)', error_text, re.IGNORECASE)
                        support_id = support_id_match.group(1) if support_id_match else "N/A"
                        
                        return {
                            "success": False,
                            "error": f"Request was rejected. Please check: 1) Your IP is whitelisted in SmartAPI dashboard, 2) Your API key is correct, 3) Your session is valid. Support ID: {support_id}",
                            "status_code": response.status_code
                        }
                    
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", f"HTTP {response.status_code}")
                        print(f"Positions API Error Response: {error_data}")
                        return {
                            "success": False,
                            "error": error_msg,
                            "status_code": response.status_code
                        }
                    except (ValueError, json.JSONDecodeError):
                        error_text = response.text[:500] if response.text else "No error message"
                        print(f"Positions API Error Text: {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status_code}: {error_text}",
                            "status_code": response.status_code
                        }
                
                # Check if response has content
                if not response.text or not response.text.strip():
                    print("Positions API: Empty response received")
                    return {
                        "success": False,
                        "error": "Empty response from API. Please check your session and try again.",
                        "status_code": response.status_code
                    }
                
                # Try to parse JSON
                try:
                    print("Attempting to parse JSON response...")
                    result = response.json()
                    print(f"JSON parsed successfully")
                    print(f"Response type: {type(result)}")
                    if isinstance(result, dict):
                        print(f"Response keys: {list(result.keys())}")
                        print(f"Response status: {result.get('status')}")
                        print(f"Response message: {result.get('message')}")
                        print(f"Response errorcode: {result.get('errorcode')}")
                        data = result.get('data')
                        if data is not None:
                            print(f"Response data type: {type(data)}")
                            if isinstance(data, list):
                                print(f"Response data length: {len(data)}")
                            else:
                                print(f"Response data: {str(data)[:200]}")
                        else:
                            print("Response data is None")
                    else:
                        print(f"Response is not a dict: {result}")
                except (ValueError, json.JSONDecodeError) as json_err:
                    response_text = response.text[:1000] if response.text else "(empty)"
                    print(f"JSON PARSING ERROR: {type(json_err).__name__}: {str(json_err)}")
                    print(f"Response text (first 1000 chars): {response_text}")
                    print(f"Response status code: {response.status_code}")
                    print(f"Response headers: {dict(response.headers)}")
                    return {
                        "success": False,
                        "error": f"Invalid JSON response: {str(json_err)}. Response: {response_text[:200]}",
                        "status_code": response.status_code
                    }
                
                if result.get("status") and result.get("data") is not None:
                    data = result.get("data", [])
                    print(f"SUCCESS: Returning {len(data) if isinstance(data, list) else 'non-list'} positions")
                    print("-" * 80)
                    return {
                        "success": True,
                        "data": data
                    }
                else:
                    error_msg = result.get("message", "Failed to fetch positions")
                    errorcode = result.get("errorcode", "")
                    print(f"ERROR: API returned failure")
                    print(f"  Status: {result.get('status')}")
                    print(f"  Message: {error_msg}")
                    print(f"  Error code: {errorcode}")
                    print(f"  Full response: {result}")
                    print("-" * 80)
                    return {
                        "success": False,
                        "error": error_msg,
                        "errorcode": errorcode
                    }
            except httpx.HTTPStatusError as e:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("message", f"HTTP {e.response.status_code}")
                except (ValueError, json.JSONDecodeError):
                    error_msg = f"HTTP {e.response.status_code}: {e.response.text[:200] if e.response.text else 'No error message'}"
                print(f"Positions API HTTPStatusError: {error_msg}")
                return {"success": False, "error": error_msg, "status_code": e.response.status_code}
            except httpx.RequestError as e:
                error_msg = f"Request failed: {str(e)}"
                print(f"Positions API RequestError: {error_msg}")
                return {"success": False, "error": error_msg}
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                print(f"Positions API Exception: {error_msg}")
                import traceback
                traceback.print_exc()
                return {"success": False, "error": error_msg}
    
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
                # Get real IP addresses for this request
                local_ip = self._get_local_ip()
                public_ip = await self._get_public_ip()
                
                headers = self._get_auth_headers()
                headers["X-ClientLocalIP"] = local_ip
                headers["X-ClientPublicIP"] = public_ip
                
                response = await client.get(url, headers=headers, timeout=30.0)
                
                # Check HTTP status
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", f"HTTP {response.status_code}")
                        return {
                            "success": False,
                            "error": error_msg,
                            "status_code": response.status_code
                        }
                    except (ValueError, json.JSONDecodeError):
                        error_text = response.text[:500] if response.text else "No error message"
                        return {
                            "success": False,
                            "error": f"HTTP {response.status_code}: {error_text}",
                            "status_code": response.status_code
                        }
                
                result = response.json()
                
                if result.get("status") and result.get("data"):
                    return {
                        "success": True,
                        "data": result.get("data", [])
                    }
                else:
                    error_msg = result.get("message", "Failed to fetch order book")
                    return {
                        "success": False,
                        "error": error_msg,
                        "errorcode": result.get("errorcode", "")
                    }
            except httpx.HTTPStatusError as e:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("message", f"HTTP {e.response.status_code}")
                except (ValueError, json.JSONDecodeError):
                    error_msg = f"HTTP {e.response.status_code}: {e.response.text[:200] if e.response.text else 'No error message'}"
                return {"success": False, "error": error_msg, "status_code": e.response.status_code}
            except httpx.RequestError as e:
                return {"success": False, "error": f"Request failed: {str(e)}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get order details by order ID."""
        url = f"{self.base_url}/rest/secure/angelbroking/order/v1/details/{order_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                # Get real IP addresses for this request
                local_ip = self._get_local_ip()
                public_ip = await self._get_public_ip()
                
                headers = self._get_auth_headers()
                headers["X-ClientLocalIP"] = local_ip
                headers["X-ClientPublicIP"] = public_ip
                
                response = await client.get(url, headers=headers, timeout=30.0)
                
                # Check HTTP status
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", f"HTTP {response.status_code}")
                        return {
                            "success": False,
                            "error": error_msg,
                            "status_code": response.status_code
                        }
                    except (ValueError, json.JSONDecodeError):
                        error_text = response.text[:500] if response.text else "No error message"
                        return {
                            "success": False,
                            "error": f"HTTP {response.status_code}: {error_text}",
                            "status_code": response.status_code
                        }
                
                result = response.json()
                
                if result.get("status") and result.get("data"):
                    return {
                        "success": True,
                        "data": result.get("data")
                    }
                else:
                    error_msg = result.get("message", "Failed to fetch order details")
                    return {
                        "success": False,
                        "error": error_msg,
                        "errorcode": result.get("errorcode", "")
                    }
            except httpx.HTTPStatusError as e:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("message", f"HTTP {e.response.status_code}")
                except (ValueError, json.JSONDecodeError):
                    error_msg = f"HTTP {e.response.status_code}: {e.response.text[:200] if e.response.text else 'No error message'}"
                return {"success": False, "error": error_msg, "status_code": e.response.status_code}
            except httpx.RequestError as e:
                return {"success": False, "error": f"Request failed: {str(e)}"}
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
                # Get real IP addresses for this request
                local_ip = self._get_local_ip()
                public_ip = await self._get_public_ip()
                
                headers = self._get_auth_headers()
                headers["X-ClientLocalIP"] = local_ip
                headers["X-ClientPublicIP"] = public_ip
                
                response = await client.get(url, headers=headers, timeout=30.0)
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
    
    async def get_top_gainers_losers(
        self,
        datatype: str = "PercPriceGainers",
        expirytype: str = "NEAR",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get top gainers and losers using SmartAPI gainersLosers endpoint.
        
        Args:
            datatype: Type of data (PercPriceGainers, PercPriceLosers, PercOIGainers, PercOILosers)
            expirytype: Expiry type (NEAR, NEXT, FAR)
            limit: Number of results to return (default: 20)
            
        Returns:
            Dict with success status and data list
        """
        # The gainersLosers endpoint might only be available on angelone.in domain
        # Try to use angelone.in if the base_url is angelbroking.com
        if "angelbroking.com" in self.base_url:
            # Use angelone.in for this specific endpoint
            url = f"https://apiconnect.angelone.in/rest/secure/angelbroking/marketData/v1/gainersLosers"
        else:
            url = f"{self.base_url}/rest/secure/angelbroking/marketData/v1/gainersLosers"
        
        payload = {
            "datatype": datatype,
            "expirytype": expirytype
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Get real IP addresses for this request
                local_ip = self._get_local_ip()
                public_ip = await self._get_public_ip()
                
                # Check if we have a valid token
                if not self.access_token:
                    return {
                        "success": False,
                        "error": "No access token available. Please login first."
                    }
                
                if not self.is_token_valid():
                    return {
                        "success": False,
                        "error": "Access token expired. Please refresh session."
                    }
                
                headers = self._get_auth_headers()
                headers["X-ClientLocalIP"] = local_ip
                headers["X-ClientPublicIP"] = public_ip
                
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                # Log response for debugging
                print(f"GainersLosers API Request URL: {url}")
                print(f"GainersLosers API Request Payload: {payload}")
                print(f"GainersLosers API Response Status: {response.status_code}")
                
                # Check HTTP status
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", f"HTTP {response.status_code}")
                        print(f"GainersLosers API Error Response: {error_data}")
                        return {
                            "success": False,
                            "error": error_msg,
                            "status_code": response.status_code
                        }
                    except (ValueError, json.JSONDecodeError):
                        error_text = response.text[:500] if response.text else "No error message"
                        print(f"GainersLosers API Error Text: {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status_code}: {error_text}",
                            "status_code": response.status_code
                        }
                
                result = response.json()
                print(f"GainersLosers API Response Data: {result}")
                
                if result.get("status") and result.get("data"):
                    # Limit results
                    data_list = result.get("data", [])[:limit]
                    
                    # Transform data to match expected format
                    transformed_data = []
                    for item in data_list:
                        transformed_data.append({
                            "symbol": item.get("tradingSymbol", "N/A"),
                            "symboltoken": item.get("symbolToken", ""),
                            "percentChange": round(item.get("percentChange", 0), 2),
                            "opnInterest": item.get("opnInterest", 0),
                            "netChangeOpnInterest": item.get("netChangeOpnInterest", 0)
                        })
                    
                    return {
                        "success": True,
                        "data": transformed_data,
                        "datatype": datatype,
                        "expirytype": expirytype,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_msg = result.get("message", "Failed to fetch gainers/losers")
                    print(f"GainersLosers API Error: {error_msg}, Full response: {result}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "errorcode": result.get("errorcode", "")
                    }
            except httpx.HTTPStatusError as e:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("message", f"HTTP {e.response.status_code}")
                except (ValueError, json.JSONDecodeError):
                    error_msg = f"HTTP {e.response.status_code}: {e.response.text[:200] if e.response.text else 'No error message'}"
                print(f"GainersLosers API HTTPStatusError: {error_msg}")
                return {"success": False, "error": error_msg, "status_code": e.response.status_code}
            except httpx.RequestError as e:
                error_msg = f"Request failed: {str(e)}"
                print(f"GainersLosers API RequestError: {error_msg}")
                return {"success": False, "error": error_msg}
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                print(f"GainersLosers API Exception: {error_msg}")
                import traceback
                traceback.print_exc()
                return {"success": False, "error": error_msg}

