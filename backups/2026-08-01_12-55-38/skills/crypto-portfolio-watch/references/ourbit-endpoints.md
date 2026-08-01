# Ourbit API Endpoints Reference

> Source: https://ourbitdevelop.github.io/apidocs/spot_v3_en/
> Source: https://ourbitdevelop.github.io/apidocs/contract_en/

## Spot API

### Base URL
```
https://api.ourbit.com
```

### Authentication (Spot)
- Header: `X-OURBIT-APIKEY: {api_key}`
- Query: `param1=val1&...&timestamp={ms}&recvWindow=5000&signature={sig}`
- Signature: `HMAC-SHA256(query_string, API_SECRET)`
- Signature output: lowercase hex

### Public Endpoints (No Auth)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v3/time` | GET | Server timestamp (ms) |
| `/api/v3/exchangeInfo` | GET | Exchange info, symbol list |

### Private Endpoints (Auth Required)

| Endpoint | Method | Permission | Description |
|----------|--------|-----------|-------------|
| `/api/v3/myTrades` | GET | Trade history | Recent trades (requires `symbol`) |
| `/api/v3/allOrders` | GET | Order history | All orders 7d (requires `symbol`) |
| `/api/v3/openOrders` | GET | Order status | Open orders (requires `symbol`) |
| ~~`/api/v3/account`~~ | ~~GET~~ | ~~Account~~ | **Returns 700007 — No permission** |

### Rate Limits
- `/api/v3/myTrades`: Weight varies by limit
- `/api/v3/allOrders`: Weight 10
- `/api/v3/openOrders`: Weight 3

### Spot Error Codes
| Code | Description |
|------|-------------|
| 700001 | Invalid signature |
| 700002 | Invalid API key |
| 700003 | Invalid timestamp |
| 700004 | Invalid recvWindow |
| 700005 | recvWindow must be < 60000 |
| 700006 | IP not whitelisted |
| 700007 | No permission to access endpoint |

---

## Futures API

### Base URL
```
https://futures.ourbit.com
```

### Authentication (Futures) — DIFFERENT FROM SPOT
- Headers: `ApiKey`, `Request-Time`, `Signature`, `Content-Type: application/json`
- Signature string: `accessKey + timestamp + parameterString`
- Signature: `HMAC-SHA256(sign_string, API_SECRET)`
- Parameters: snake_case (GET), camelCase (POST)
- POST body: JSON

### Public Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/public/time` | GET | Server timestamp |

### Private Endpoints

| Endpoint | Method | Permission | Rate Limit |
|----------|--------|-----------|------------|
| `/api/v1/private/order/list/history_orders` | GET | Futures read | 20/2s |
| `/api/v1/private/order/list/order_deals` | GET | Futures read | 20/2s |

### history_orders Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | No | Contract symbol |
| states | string | No | 1=pending,2=incomplete,3=completed,4=cancelled,5=invalid |
| category | int | No | 1=limit,2=liquidation,4=ADL |
| start_time | long | No | Start (ms), max 180d range |
| end_time | long | No | End (ms) |
| side | int | No | 1=open long,2=close short,3=open short,4=close long |
| page_num | int | **Yes** | Page number (default 1) |
| page_size | int | **Yes** | Page size (default 20, max 100) |

### order_deals Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | No | Contract symbol |
| start_time | long | No | Start (ms) |
| end_time | long | No | End (ms) |
| page_num | int | **Yes** | Page number |
| page_size | int | **Yes** | Page size (max 100) |

### Futures Error Codes
| Code | Description |
|------|-------------|
| 0 | Success |
| 511 | Endpoint access forbidden |
| 513 | Invalid request time |
| 514 | Invalid signature |
| 515 | Invalid API key |

---

## Key Differences: Spot vs Futures

| Feature | Spot | Futures |
|---------|------|---------|
| Base URL | `api.ourbit.com` | `futures.ourbit.com` |
| Signature location | Query string | Header |
| Signature input | Query string only | accessKey + timestamp + params |
| Param case | camelCase | snake_case (GET) |
| Content-Type | Not required | `application/json` |
| Time validation | recvWindow 5000 | 10s default, max 60s |
