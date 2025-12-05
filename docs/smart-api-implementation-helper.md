# Angel One SmartAPI - Complete Implementation Helper

**Version:** 1.0  
**Last Updated:** 2025-01-03  
**Base URL:** `https://apiconnect.angelbroking.com`

---

## Table of Contents

1. [Response Structure](#response-structure)
2. [Header Parameters](#header-parameters)
3. [Authentication Flow](#authentication-flow)
4. [API Endpoints Reference](#api-endpoints-reference)
5. [Code Implementation Examples](#code-implementation-examples)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [Common Issues & Solutions](#common-issues--solutions)

---

## Response Structure

### Successful Request

All successful API responses follow this structure:

```json
{
  "status": true,
  "message": "SUCCESS",
  "errorcode": "",
  "data": {}
}
```

**Key Points:**
- `status`: Boolean `true` for success
- `message`: Usually "SUCCESS" for successful requests
- `errorcode`: Empty string for successful requests
- `data`: Contains the actual response payload (varies by endpoint)
- Content-Type: `application/json`
- HTTP Status: `200 OK`

### Failed Request

All failed API responses follow this structure:

```json
{
  "status": false,
  "message": "Login Id or password is invalid",
  "errorcode": "AB1007",
  "data": null
}
```

**Key Points:**
- `status`: Boolean `false` for failures
- `message`: Human-readable error description
- `errorcode`: Error code (e.g., "AB1007")
- `data`: Usually `null` or empty for errors
- HTTP Status: Usually `400`, `401`, `403`, `500`, etc.

---

## Header Parameters

**IMPORTANT:** Every POST request to SmartAPI must include the following headers:

| Header Name | Value | Description | Required |
|------------|-------|-------------|----------|
| `Content-Type` | `application/json` | Request content type | ✅ Yes |
| `Accept` | `application/json` | Expected response format | ✅ Yes |
| `X-ClientLocalIP` | `CLIENT_LOCAL_IP` | System Local IP Address | ✅ Yes |
| `X-ClientPublicIP` | `CLIENT_PUBLIC_IP` | Public IP Address | ✅ Yes |
| `X-MACAddress` | `MAC_ADDRESS` | System MAC Address | ✅ Yes |
| `X-PrivateKey` | `api_key` | API KEY from SmartAPI dashboard | ✅ Yes |
| `X-UserType` | `USER` | Must be "USER" | ✅ Yes |
| `X-SourceID` | `WEB` | Must be "WEB" | ✅ Yes |
| `Authorization` | `Bearer {jwt_token}` | JWT token (for authenticated endpoints) | ⚠️ Required for all APIs except login |

### Header Implementation Example

```python
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-UserType": "USER",
    "X-SourceID": "WEB",
    "X-ClientLocalIP": "192.168.1.1",  # Get actual local IP
    "X-ClientPublicIP": "203.0.113.1",  # Get actual public IP
    "X-MACAddress": "00:00:00:00:00:00",  # Can be dummy for web apps
    "X-PrivateKey": "YOUR_API_KEY"
}
```

**For Authenticated Requests:**
```python
headers["Authorization"] = f"Bearer {access_token}"
```

---

## Authentication Flow

### Step 1: Generate Session (Login)

**Endpoint:** `POST /rest/auth/angelbroking/user/v1/loginByMPIN`

**Note:** `loginByPassword` is deprecated. Always use `loginByMPIN`.

**Request Body:**
```json
{
  "clientcode": "YOUR_CLIENT_ID",
  "mpin": "1234",
  "totp": "123456"
}
```

**Response:**
```json
{
  "status": true,
  "message": "SUCCESS",
  "errorcode": "",
  "data": {
    "jwtToken": "eyJhbGciOiJIUzUxMiJ9...",
    "refreshToken": "eyJhbGciOiJIUzUxMiJ9...",
    "feedToken": "eyJhbGciOiJIUzUxMiJ9...",
    "state": null
  }
}
```

**Tokens:**
- `jwtToken` (access_token): Valid for 24 hours, used for all authenticated API calls
- `refreshToken`: Used to refresh access token without TOTP
- `feedToken`: Used for WebSocket market data feeds

### Step 2: Refresh Token (Optional)

**Endpoint:** `POST /rest/auth/angelbroking/jwt/v1/generateTokens`

**Headers:**
```python
{
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {refresh_token}"
}
```

**Request Body:** None (empty body)

**Response:**
```json
{
  "status": true,
  "message": "SUCCESS",
  "data": {
    "jwtToken": "new_access_token...",
    "feedToken": "new_feed_token..."
  }
}
```

### Step 3: Logout

**Endpoint:** `POST /rest/secure/angelbroking/user/v1/logout`

**Headers:** Include `Authorization: Bearer {access_token}`

---

## API Endpoints Reference

### Authentication Endpoints

#### 1. Login by MPIN
- **Method:** `POST`
- **URL:** `/rest/auth/angelbroking/user/v1/loginByMPIN`
- **Auth Required:** No
- **Body:**
  ```json
  {
    "clientcode": "V50055868",
    "mpin": "1234",
    "totp": "123456"
  }
  ```

#### 2. Refresh Token
- **Method:** `POST`
- **URL:** `/rest/auth/angelbroking/jwt/v1/generateTokens`
- **Auth Required:** Yes (refresh token in Authorization header)
- **Body:** None

#### 3. Logout
- **Method:** `POST`
- **URL:** `/rest/secure/angelbroking/user/v1/logout`
- **Auth Required:** Yes (access token)

---

### User Profile Endpoints

#### Get Profile
- **Method:** `GET`
- **URL:** `/rest/secure/angelbroking/user/v1/getProfile`
- **Auth Required:** Yes
- **Response:**
  ```json
  {
    "status": true,
    "data": {
      "clientcode": "V50055868",
      "email": "user@example.com",
      "name": "User Name",
      ...
    }
  }
  ```

---

### Order Management Endpoints

#### 1. Place Order
- **Method:** `POST`
- **URL:** `/rest/secure/angelbroking/order/v1/placeOrder`
- **Auth Required:** Yes
- **Body:**
  ```json
  {
    "variety": "NORMAL",
    "tradingsymbol": "NIFTY",
    "symboltoken": "99926000",
    "transactiontype": "BUY",
    "exchange": "NFO",
    "ordertype": "MARKET",
    "producttype": "INTRADAY",
    "duration": "DAY",
    "price": "0",
    "squareoff": "0",
    "stoploss": "0",
    "quantity": "50"
  }
  ```

**Order Types:**
- `MARKET`: Market order
- `LIMIT`: Limit order
- `STOPLOSS_LIMIT`: Stop loss limit order
- `STOPLOSS_MARKET`: Stop loss market order

**Product Types:**
- `INTRADAY`: Intraday
- `DELIVERY`: Delivery
- `MARGIN`: Margin

**Transaction Types:**
- `BUY`: Buy order
- `SELL`: Sell order

#### 2. Modify Order
- **Method:** `POST`
- **URL:** `/rest/secure/angelbroking/order/v1/modifyOrder`
- **Auth Required:** Yes
- **Body:**
  ```json
  {
    "variety": "NORMAL",
    "orderid": "ORDER_ID",
    "ordertype": "LIMIT",
    "producttype": "INTRADAY",
    "duration": "DAY",
    "price": "19500",
    "quantity": "50"
  }
  ```

#### 3. Cancel Order
- **Method:** `POST`
- **URL:** `/rest/secure/angelbroking/order/v1/cancelOrder`
- **Auth Required:** Yes
- **Body:**
  ```json
  {
    "variety": "NORMAL",
    "orderid": "ORDER_ID"
  }
  ```

#### 4. Get Order Book
- **Method:** `GET`
- **URL:** `/rest/secure/angelbroking/order/v1/getOrderBook`
- **Auth Required:** Yes
- **Response:** List of all orders (pending, executed, cancelled)

#### 5. Get Trade Book
- **Method:** `GET`
- **URL:** `/rest/secure/angelbroking/order/v1/getTradeBook`
- **Auth Required:** Yes
- **Response:** List of executed trades

---

### Portfolio Endpoints

#### 1. Get Positions
- **Method:** `GET`
- **URL:** `/rest/secure/angelbroking/portfolio/v1/getPosition`
- **Auth Required:** Yes
- **Response:** Current intraday positions

#### 2. Get Holdings
- **Method:** `GET`
- **URL:** `/rest/secure/angelbroking/portfolio/v1/getHolding`
- **Auth Required:** Yes
- **Response:** Delivery holdings

#### 3. Get Funds (RMS)
- **Method:** `GET`
- **URL:** `/rest/secure/angelbroking/user/v1/getRMS`
- **Auth Required:** Yes
- **Response:** Available funds and margin details

---

### Market Data Endpoints

#### 1. Get Historical Candle Data
- **Method:** `POST`
- **URL:** `/rest/secure/angelbroking/historical/v1/getCandleData`
- **Auth Required:** Yes
- **Body:**
  ```json
  {
    "exchange": "NSE",
    "symboltoken": "3045",
    "interval": "ONE_MINUTE",
    "fromdate": "2024-01-01 09:15",
    "todate": "2024-01-01 15:30"
  }
  ```

**Intervals:**
- `ONE_MINUTE`
- `THREE_MINUTE`
- `FIVE_MINUTE`
- `TEN_MINUTE`
- `FIFTEEN_MINUTE`
- `THIRTY_MINUTE`
- `ONE_HOUR`
- `ONE_DAY`
- `ONE_WEEK`
- `ONE_MONTH`

#### 2. Get Market Status
- **Method:** `GET`
- **URL:** `/rest/secure/angelbroking/market/v1/getMarketStatus`
- **Auth Required:** Yes
- **Response:** Market open/close status

#### 3. Get Quote
- **Method:** `POST`
- **URL:** `/rest/secure/angelbroking/market/v1/getQuote`
- **Auth Required:** Yes
- **Body:**
  ```json
  {
    "mode": "FULL",
    "exchangeTokens": {
      "NSE": ["3045", "11536"]
    }
  }
  ```

**Modes:**
- `FULL`: Full quote with all details
- `LTP`: Last traded price only

#### 4. Get Symbol Master
- **Method:** `GET`
- **URL:** `/rest/secure/angelbroking/market/v1/getSymbolMaster`
- **Auth Required:** Yes
- **Response:** Large file with all symbol information
- **Note:** Download and cache locally, don't fetch repeatedly

---

## Code Implementation Examples

### Python (httpx) - Complete Client Example

```python
import httpx
import socket
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class SmartAPIClient:
    def __init__(self, api_key: str, secret_key: str, client_id: str, mpin: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.client_id = client_id
        self.mpin = mpin
        self.base_url = "https://apiconnect.angelbroking.com"
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.feed_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
    
    def _get_local_ip(self) -> str:
        """Get local IP address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "192.168.1.1"
    
    async def _get_public_ip(self) -> str:
        """Get public IP address."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("https://api.ipify.org")
                if response.status_code == 200:
                    return response.text.strip()
        except Exception:
            pass
        return self._get_local_ip()
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers for authenticated requests."""
        if not self.access_token:
            raise ValueError("No access token. Please login first.")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": self._get_local_ip(),
            "X-ClientPublicIP": self._get_local_ip(),  # Update in async methods
            "X-MACAddress": "00:00:00:00:00:00",
            "X-PrivateKey": self.api_key
        }
    
    async def login(self, totp: str) -> Dict[str, Any]:
        """Login and generate session."""
        url = f"{self.base_url}/rest/auth/angelbroking/user/v1/loginByMPIN"
        
        local_ip = self._get_local_ip()
        public_ip = await self._get_public_ip()
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": local_ip,
            "X-ClientPublicIP": public_ip,
            "X-MACAddress": "00:00:00:00:00:00",
            "X-PrivateKey": self.api_key
        }
        
        payload = {
            "clientcode": self.client_id,
            "mpin": self.mpin,
            "totp": totp
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") and data.get("data"):
                session = data["data"]
                self.access_token = session.get("jwtToken")
                self.refresh_token = session.get("refreshToken")
                self.feed_token = session.get("feedToken")
                self.token_expiry = datetime.now() + timedelta(hours=24)
                
                return {
                    "success": True,
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                    "feed_token": self.feed_token
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Login failed")
                }
    
    async def refresh_token(self) -> Dict[str, Any]:
        """Refresh access token."""
        if not self.refresh_token:
            return {"success": False, "error": "No refresh token available"}
        
        url = f"{self.base_url}/rest/auth/angelbroking/jwt/v1/generateTokens"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.refresh_token}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") and data.get("data"):
                session = data["data"]
                self.access_token = session.get("jwtToken")
                self.feed_token = session.get("feedToken")
                self.token_expiry = datetime.now() + timedelta(hours=24)
                
                return {"success": True, "access_token": self.access_token}
            else:
                return {"success": False, "error": data.get("message", "Token refresh failed")}
    
    async def place_order(
        self,
        symbol: str,
        exchange: str,
        transaction_type: str,
        order_type: str,
        quantity: int,
        price: float = 0.0,
        product_type: str = "INTRADAY"
    ) -> Dict[str, Any]:
        """Place an order."""
        url = f"{self.base_url}/rest/secure/angelbroking/order/v1/placeOrder"
        
        payload = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": "",  # Fetch from symbol master if needed
            "transactiontype": transaction_type,
            "exchange": exchange,
            "ordertype": order_type,
            "producttype": product_type,
            "duration": "DAY",
            "price": str(price),
            "squareoff": "0",
            "stoploss": "0",
            "quantity": str(quantity)
        }
        
        async with httpx.AsyncClient() as client:
            local_ip = self._get_local_ip()
            public_ip = await self._get_public_ip()
            
            headers = self._get_auth_headers()
            headers["X-ClientLocalIP"] = local_ip
            headers["X-ClientPublicIP"] = public_ip
            
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
    
    async def get_positions(self) -> Dict[str, Any]:
        """Get current positions."""
        url = f"{self.base_url}/rest/secure/angelbroking/portfolio/v1/getPosition"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._get_auth_headers(), timeout=30.0)
            response.raise_for_status()
            return response.json()
    
    async def get_order_book(self) -> Dict[str, Any]:
        """Get order book."""
        url = f"{self.base_url}/rest/secure/angelbroking/order/v1/getOrderBook"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._get_auth_headers(), timeout=30.0)
            response.raise_for_status()
            return response.json()
```

### JavaScript/TypeScript Example

```typescript
class SmartAPIClient {
  private apiKey: string;
  private clientId: string;
  private baseUrl: string = "https://apiconnect.angelbroking.com";
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor(apiKey: string, clientId: string) {
    this.apiKey = apiKey;
    this.clientId = clientId;
  }

  private getHeaders(includeAuth: boolean = false): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "Accept": "application/json",
      "X-UserType": "USER",
      "X-SourceID": "WEB",
      "X-ClientLocalIP": "192.168.1.1", // Get actual IP
      "X-ClientPublicIP": "192.168.1.1", // Get actual IP
      "X-MACAddress": "00:00:00:00:00:00",
      "X-PrivateKey": this.apiKey
    };

    if (includeAuth && this.accessToken) {
      headers["Authorization"] = `Bearer ${this.accessToken}`;
    }

    return headers;
  }

  async login(mpin: string, totp: string): Promise<any> {
    const url = `${this.baseUrl}/rest/auth/angelbroking/user/v1/loginByMPIN`;
    
    const response = await fetch(url, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        clientcode: this.clientId,
        mpin: mpin,
        totp: totp
      })
    });

    const data = await response.json();
    
    if (data.status && data.data) {
      this.accessToken = data.data.jwtToken;
      this.refreshToken = data.data.refreshToken;
      return { success: true, data: data.data };
    } else {
      return { success: false, error: data.message };
    }
  }

  async placeOrder(orderData: any): Promise<any> {
    if (!this.accessToken) {
      throw new Error("Not authenticated. Please login first.");
    }

    const url = `${this.baseUrl}/rest/secure/angelbroking/order/v1/placeOrder`;
    
    const response = await fetch(url, {
      method: "POST",
      headers: this.getHeaders(true),
      body: JSON.stringify(orderData)
    });

    return await response.json();
  }
}
```

---

## Error Handling

### Common Error Codes

| Error Code | Description | Solution |
|-----------|-------------|----------|
| `AB1007` | Invalid login credentials | Check client ID, MPIN, and TOTP |
| `AB1008` | Invalid TOTP | Generate new TOTP from authenticator app |
| `AB1009` | Session expired | Refresh token or login again |
| `AB1010` | IP not whitelisted | Add IP to SmartAPI dashboard |
| `AB1011` | Invalid API key | Verify API key in SmartAPI dashboard |
| `AB1012` | Insufficient funds | Check account balance |
| `AB1013` | Invalid symbol | Verify symbol token and exchange |

### Error Handling Best Practices

```python
async def make_api_call(self, url: str, method: str = "GET", payload: dict = None):
    """Generic API call with error handling."""
    try:
        headers = self._get_auth_headers()
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers, timeout=30.0)
            else:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            
            # Check HTTP status
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "status_code": response.status_code
                }
            
            data = response.json()
            
            # Check API response status
            if not data.get("status"):
                return {
                    "success": False,
                    "error": data.get("message", "API call failed"),
                    "errorcode": data.get("errorcode", ""),
                    "data": data.get("data")
                }
            
            return {
                "success": True,
                "data": data.get("data")
            }
            
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP {e.response.status_code}: {e.response.text}",
            "status_code": e.response.status_code
        }
    except httpx.RequestError as e:
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }
```

### Token Expiry Handling

```python
def is_token_valid(self) -> bool:
    """Check if token is still valid."""
    if not self.access_token or not self.token_expiry:
        return False
    return datetime.now() < self.token_expiry

async def ensure_valid_token(self) -> bool:
    """Ensure we have a valid token, refresh if needed."""
    if self.is_token_valid():
        return True
    
    # Try to refresh
    if self.refresh_token:
        result = await self.refresh_token()
        if result.get("success"):
            return True
    
    # Need to login again
    return False
```

---

## Best Practices

### 1. IP Address Management

- **Always get real IP addresses** - Don't hardcode IPs
- **Whitelist your IP** in SmartAPI dashboard before testing
- **Handle IP changes** - If your IP changes, update whitelist

### 2. Token Management

- **Store tokens securely** - Encrypt tokens in database
- **Refresh before expiry** - Check token validity before each API call
- **Handle refresh failures** - Prompt for TOTP if refresh fails

### 3. Rate Limiting

- **Respect rate limits** - SmartAPI has rate limits per IP
- **Implement retry logic** - With exponential backoff
- **Cache responses** - Cache symbol master, market status, etc.

### 4. Error Handling

- **Always check `status` field** - Don't assume success
- **Log error codes** - For debugging and support
- **Handle network errors** - Implement retry logic
- **Validate inputs** - Before making API calls

### 5. Security

- **Never expose API keys** - Keep in environment variables or encrypted storage
- **Use HTTPS only** - Never use HTTP
- **Validate TOTP** - Always require TOTP for initial login
- **Encrypt credentials** - Encrypt API keys, MPIN, tokens in database

### 6. Symbol Token Management

- **Download symbol master once** - It's a large file
- **Cache symbol tokens** - Map symbols to tokens locally
- **Update periodically** - Refresh symbol master weekly

### 7. Order Management

- **Validate orders** - Check funds, symbol validity before placing
- **Track order status** - Poll order book for status updates
- **Handle partial fills** - Be prepared for partial executions
- **Implement order timeouts** - Cancel orders that don't fill

---

## Common Issues & Solutions

### Issue 1: "Request Rejected" or 403 Forbidden

**Cause:** IP address not whitelisted

**Solution:**
1. Get your public IP: `curl https://api.ipify.org`
2. Log in to SmartAPI dashboard: https://smartapi.angelone.in/
3. Navigate to API Management → IP Whitelist
4. Add your IP address
5. Wait 2-3 minutes for changes to propagate

### Issue 2: "Invalid TOTP" or "TOTP Required"

**Cause:** TOTP expired or incorrect

**Solution:**
1. Generate fresh TOTP from authenticator app
2. Ensure system time is synchronized (TOTP is time-based)
3. Enter TOTP within 30 seconds of generation

### Issue 3: "Session Expired"

**Cause:** Access token expired (24 hours)

**Solution:**
1. Try refreshing token first (no TOTP needed)
2. If refresh fails, login again with TOTP
3. Implement automatic token refresh before expiry

### Issue 4: "Invalid Symbol Token"

**Cause:** Symbol token not found or incorrect

**Solution:**
1. Download symbol master: `GET /getSymbolMaster`
2. Search for symbol by name
3. Get correct `symboltoken` and `exchange`
4. Cache symbol mappings locally

### Issue 5: Empty Response or Connection Timeout

**Cause:** Network issues or API downtime

**Solution:**
1. Check API status: https://smartapi.angelone.in/
2. Verify base URL: `https://apiconnect.angelbroking.com`
3. Check firewall/proxy settings
4. Implement retry logic with backoff

### Issue 6: "Insufficient Funds"

**Cause:** Not enough margin for order

**Solution:**
1. Check available funds: `GET /getRMS`
2. Verify order quantity and price
3. Check margin requirements for product type

---

## Testing Checklist

Before going live, test:

- [ ] Login with MPIN and TOTP
- [ ] Token refresh
- [ ] Get profile
- [ ] Get market status
- [ ] Get symbol master
- [ ] Get quote
- [ ] Get positions
- [ ] Get holdings
- [ ] Get funds
- [ ] Get order book
- [ ] Get trade book
- [ ] Place order (paper trading first!)
- [ ] Modify order
- [ ] Cancel order
- [ ] Error handling for all scenarios
- [ ] Token expiry handling
- [ ] IP whitelisting

---

## Additional Resources

- **SmartAPI Dashboard:** https://smartapi.angelone.in/
- **API Documentation:** Available in SmartAPI dashboard
- **Postman Collection:** See `docs/angel-one-smartapi.postman_collection.json`
- **Support:** Contact Angel One support for API issues

---

## Quick Reference Card

### Authentication
```
POST /rest/auth/angelbroking/user/v1/loginByMPIN
Body: {clientcode, mpin, totp}
```

### Orders
```
POST /rest/secure/angelbroking/order/v1/placeOrder
GET  /rest/secure/angelbroking/order/v1/getOrderBook
POST /rest/secure/angelbroking/order/v1/cancelOrder
```

### Portfolio
```
GET /rest/secure/angelbroking/portfolio/v1/getPosition
GET /rest/secure/angelbroking/portfolio/v1/getHolding
GET /rest/secure/angelbroking/user/v1/getRMS
```

### Market Data
```
POST /rest/secure/angelbroking/historical/v1/getCandleData
GET  /rest/secure/angelbroking/market/v1/getMarketStatus
POST /rest/secure/angelbroking/market/v1/getQuote
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-03  
**Maintained by:** AlgoPilot Development Team

