# Angel One SmartAPI Integration

## Overview

This document describes the Angel One SmartAPI integration implemented in AlgoPilot.

## Login Flow

### Authentication Process

1. **Initial Setup**: When adding a new app, the following credentials are required:
   - **App Name**: Friendly name for the account
   - **Client ID**: Your Angel One Client Code
   - **API Key**: SmartAPI API Key (from SmartAPI dashboard)
   - **Secret Key**: SmartAPI Secret Key (from SmartAPI dashboard)
   - **MPIN**: Your Angel One MPIN (4-digit Mobile Personal Identification Number)

2. **Session Generation**: When switching to an app, the system:
   - Retrieves stored credentials (encrypted in production)
   - Creates a SmartAPI client instance
   - Generates a session using MPIN and TOTP (Time-based One-Time Password)
   - Uses `loginByMPIN` endpoint (password-based login is no longer supported)
   - Stores access token, refresh token, and feed token

3. **TOTP Requirement**: 
   - TOTP is required for initial login or when session expires
   - TOTP is generated from an authenticator app (Google Authenticator, etc.)
   - TOTP is entered at runtime, not stored

4. **Token Refresh**: 
   - Access tokens expire after 24 hours
   - Refresh token can be used to get new access token without TOTP
   - Automatic refresh is attempted before manual TOTP entry

## Required Fields for App Creation

When adding a new Angel One account, the following fields must be provided:

| Field | Description | Source |
|-------|-------------|--------|
| `name` | Friendly name for the account | User input |
| `account_id` | Angel One Client Code | Your Angel One account |
| `api_key` | SmartAPI API Key | SmartAPI Dashboard |
| `secret_key` | SmartAPI Secret Key | SmartAPI Dashboard |
| `mpin` | Angel One MPIN (4-digit) | Your Angel One account settings |

### Where to Find Credentials

1. **Client ID (Client Code)**: 
   - Log in to Angel One website
   - Found in account details or profile section

2. **API Key & Secret Key**:
   - Log in to SmartAPI dashboard: https://smartapi.angelone.in/
   - Navigate to API Management
   - Generate or view your API credentials

3. **MPIN**:
   - Your 4-digit MPIN (Mobile Personal Identification Number)
   - Set up in Angel One account settings
   - **Note**: Password-based login is no longer supported. You must use MPIN.

4. **TOTP**:
   - Set up 2FA on your Angel One account
   - Use authenticator app to generate TOTP codes
   - Required each time you switch apps (if session expired)

## Database Schema

### App Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `name`: App name
- `account_id`: Client ID (Client Code)
- `is_default`: Boolean flag for default app

### AppSecret Table
- `id`: Primary key
- `app_id`: Foreign key to apps table (unique)
- `api_key`: Encrypted SmartAPI API Key
- `secret_key`: Encrypted SmartAPI Secret Key
- `mpin`: Encrypted Angel One MPIN (4-digit)
- `refresh_token`: Encrypted refresh token (stored after login)

## API Endpoints

### App Management

#### Create App
```
POST /api/apps
Body: {
  "name": "My Trading Account",
  "account_id": "YOUR_CLIENT_ID",
  "api_key": "YOUR_API_KEY",
  "secret_key": "YOUR_SECRET_KEY",
  "mpin": "1234"
}
```

#### Switch App
```
POST /api/apps/{app_id}/switch
Body (optional): {
  "totp": "123456"  // Required if session expired
}
```

## SmartAPI Client

The `SmartAPIClient` class (`backend/app/services/smartapi_client.py`) provides:

### Methods

- `generate_session(totp)`: Generate new session with MPIN and TOTP (uses loginByMPIN endpoint)
- `refresh_session()`: Refresh access token using refresh token
- `is_token_valid()`: Check if current token is valid
- `get_profile()`: Get user profile
- `place_order(...)`: Place trading orders
- `get_positions()`: Get current positions
- `get_holdings()`: Get holdings
- `get_order_book()`: Get order book
- `get_trade_book()`: Get trade book
- `cancel_order(order_id)`: Cancel an order
- `get_market_data(...)`: Get historical market data

## Postman Collection

A complete Postman collection is available at:
`docs/angel-one-smartapi.postman_collection.json`

### Import Instructions

1. Open Postman
2. Click "Import"
3. Select `docs/angel-one-smartapi.postman_collection.json`
4. Set up environment variables:
   - `base_url`: `https://apiconnect.angelbroking.com`
   - `api_key`: Your SmartAPI API Key
   - `client_id`: Your Client ID
   - `mpin`: Your 4-digit MPIN
   - `totp`: Current TOTP (from authenticator app)

### Collection Structure

- **Authentication**: Login by MPIN, Refresh Token, Logout
- **User Profile**: Get Profile
- **Orders**: Place, Modify, Cancel, Get Order Book, Get Trade Book
- **Portfolio**: Get Positions, Get Holdings, Get Funds
- **Market Data**: Historical Candles, Market Status, Get Quote
- **Symbol Master**: Get Symbol Master

## Security Notes

⚠️ **IMPORTANT**: Currently, credentials are stored in plaintext in the database. This is **NOT SECURE** for production.

### TODO: Encryption Implementation

1. Derive device-specific key from master password using PBKDF2
2. Encrypt all sensitive fields (api_key, secret_key, password) using AES-GCM
3. Store encrypted blobs in database
4. Decrypt only when needed for API calls
5. Never log or expose plaintext credentials

## Testing

1. **Add App**: Use the frontend form to add a new app with all required fields
2. **Switch App**: Click "Switch to App" - if TOTP is required, you'll be prompted
3. **Verify Session**: Check that session is active and tokens are stored
4. **Test API Calls**: Use Postman collection to test various endpoints

## Error Handling

- **Missing Credentials**: App cannot be switched without credentials
- **Invalid TOTP**: Session generation fails with error message
- **Expired Token**: Automatic refresh attempted, TOTP required if refresh fails
- **Network Errors**: Proper error messages returned to frontend

## Next Steps

1. Implement encryption for stored credentials
2. Add WebSocket connection for live market data
3. Implement automatic token refresh
4. Add session timeout handling
5. Add comprehensive error handling and logging

