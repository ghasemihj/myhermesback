# Ourbit Exchange API Reference

## Base URL

```
https://api.ourbit.com
```

## Documentation

- Official docs: https://ourbitdevelop.github.io/apidocs/spot_v3_en/

## Authentication

- Header: `X-OURBIT-APIKEY: <API_KEY>`
- Signed endpoints require: `timestamp` (Unix ms) + `recvWindow` (default 5000) + `signature`
- Signature: HMAC-SHA256 of query string (without `signature` param), using API Secret as key, output as lowercase hex.

## Endpoints (from docs)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v3/time` | No | Server timestamp (public) |
| GET | `/api/v3/account` | Signed | Account info, balances, permissions |
| GET | `/api/v3/allOrders` | Signed | All orders (last 24h by default) |
| GET | `/api/v3/myTrades` | Signed | Trade history |
| GET | `/api/v3/order` | Signed | Single order query |

## Error Codes

| Code | Meaning |
|------|---------|
| 700001 | Invalid signature |
| 700002 | Invalid timestamp (too old/future) |
| 700003 | Invalid parameter |
| 700004 | Invalid IP (not whitelisted) |
| 700005 | recvWindow too large (max 60000) |
| 700006 | IP not in whitelist |
| 700007 | No permission to access endpoint |

## Known Quirks

- Public endpoints (`/api/v3/time`) return 403 to `urllib.request` without a `User-Agent` header. Use `curl` with `-H "User-Agent: Mozilla/5.0"` or set a UA in Python requests.
- `account` endpoint requires the API Key to have "Enable Reading" permission in the exchange's API management page.
- `account` response includes `permissions` array (e.g., `["SPOT", "MARGIN"]`), `accountType`, and `balances` array with `asset`/`free`/`locked` fields.

## Test Results — Spot (2026-07-31)

- Time sync: ✅ (114ms drift)
- Signature accepted: ✅ (error code returned, not generic auth failure)
- `/api/v3/account`: ❌ code 700007 — permission denied
- `/api/v3/myTrades`: ✅ works (tested with GIGGLEUSDT, limit=1)
- `/api/v3/openOrders`: ✅ works (tested with GIGGLEUSDT)
- `/api/v3/allOrders`: ✅ works (tested with GIGGLEUSDT, limit=5)

---

# Futures API (separate base URL and auth)

## Base URL

```
https://futures.ourbit.com
```

## Documentation

- Official docs: `https://ourbitdevelop.github.io/apidocs/contract_en/`
- Change log says released 2026-07-08

## Authentication (DIFFERENT from Spot)

Headers required (not query string):
- `ApiKey`: The access key part of the API key
- `Request-Time`: Millisecond timestamp string
- `Signature`: HMAC-SHA256 signature
- `Content-Type`: `application/json` (for POST)

### Signature calculation

```
sign_str = accessKey + timestamp + parameterString
signature = HMAC-SHA256(sign_str, secretKey)  → lowercase hex
```

- **GET/DELETE**: parameterString = params sorted alphabetically, joined with `&`
- **POST**: parameterString = the JSON body string (no sorting)
- Null business params are excluded from signing
- Path params are excluded from signing

### Timing

- `Request-Time` header: millisecond timestamp string
- Server validates: request time must be within ±10 seconds of server time
- Optional `Recv-Window` header (max 60, but >30 not recommended)

## Response Format

```json
{
  "success": true,
  "code": 0,
  "data": { ... }
}
```

Error:
```json
{
  "success": false,
  "code": 500,
  "message": "Internal system error!"
}
```

## Endpoints (from docs)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `api/v1/private/order/list/history_orders` | Signed | Historical orders (has `profit` field) |
| GET | `api/v1/private/order/list/order_deals` | Signed | Historical deals/fills |

Rate limit: 20 requests per 2 seconds.

### history_orders — Request Params

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | string | No | Contract symbol (e.g., `GIGGLEUSDT`) |
| `states` | string | No | Order status: `1`=pending, `2`=incomplete, `3`=completed, `4`=cancelled, `5`=invalid; comma-separated |
| `category` | int | No | `1`=limit, `2`=liquidation, `4`=ADL; comma-separated |
| `start_time` | long | No | Start time ms (max 180-day range) |
| `end_time` | long | No | End time ms |
| `side` | int | No | `1`=open long, `2`=close short, `3`=open short, `4`=close long |
| `page_num` | int | **Yes** | Page number (default 1) |
| `page_size` | int | **Yes** | Page size (default 20, max 100) |

### history_orders — Response Fields

`orderId`, `symbol`, `positionId`, `price`, `vol`, `leverage`, `side`, `category`, `orderType`, `dealAvgPrice`, `dealVol`, `orderMargin`, `takerFee`, `makerFee`, **`profit`** (realized PnL), `feeCurrency`, `openType` (1=isolated, 2=cross), `state`, `errorCode`, `externalOid`, `usedMargin`, `createTime`, `updateTime`

### order_deals — Request Params

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | string | No | Contract symbol |
| `start_time` | long | No | Start time ms |
| `end_time` | long | No | End time ms |
| `page_num` | int | **Yes** | Page number |
| `page_size` | int | **Yes** | Page size |

### order_deals — Response Fields

`symbol`, `side`, `vol`, `price`, `fee`, `feeCurrency`, **`profit`** (PnL), `orderId`, `timestamp`, `positionMode`, `taker` (bool)

## Futures Error Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 511 | Endpoint access forbidden |
| 513 | Invalid request time |

## Futures Limitations (as of 2026-07-31)

The docs only document 2 endpoints. **Not available** in official API:
- Open positions query
- Account/margin balance query
- Open orders query
- Funding fee query
