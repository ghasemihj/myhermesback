---
name: crypto-portfolio-watch
description: Daily crypto portfolio collection and report from Ourbit exchange (read-only).
version: 1.0.0
tags: [crypto, portfolio, ourbit, daily-report]
---

# crypto-portfolio-watch

Daily read-only collection and reporting of crypto portfolio activity on Ourbit exchange.

## Trigger

Use when:
- User asks about crypto portfolio, Ourbit holdings, or daily crypto report
- Cron `crypto-portfolio-daily` fires
- User says "گزارش سبد", "portfolio report", "crypto daily"

## Architecture

```
Collection (07:30 IRST) → normalized → Daily Report (08:00 IRST)
```

- **Skill path:** `~/.hermes/skills/crypto-portfolio-watch/`
- **Data root:** `/data/.hermes/reports/crypto-portfolio-watch/`
- **Scripts:** `scripts/collect_ourbit.py`, `scripts/generate_report.py`

## Data Sources

| API | Endpoint | Auth |
|-----|----------|------|
| Spot | `GET /api/v3/myTrades` | Spot HMAC (Query) |
| Spot | `GET /api/v3/allOrders` | Spot HMAC (Query) |
| Spot | `GET /api/v3/openOrders` | Spot HMAC (Query) |
| Spot | `GET /api/v3/time` | None |
| Spot | `GET /api/v3/exchangeInfo` | None |
| Futures | `GET /api/v1/private/order/list/history_orders` | Futures HMAC (Header) |
| Futures | `GET /api/v1/private/order/list/order_deals` | Futures HMAC (Header) |
| Futures | `GET /api/v1/public/time` | None |

## Forbidden Endpoints

- `GET /api/v3/account` — returns 700007 (No permission)
- No POST, PUT, DELETE, PATCH on any endpoint
- No order creation, cancellation, transfer, or withdrawal

## Authentication

### Spot (myTrades, allOrders, openOrders)
- Base URL: `https://api.ourbit.com`
- Header: `X-OURBIT-APIKEY: {key}`
- Query: `param1=val1&param2=val2&timestamp={ms}&signature={sig}`
- Signature: `HMAC-SHA256(query_string_without_signature, OURBIT_API_SECRET)`
- `recvWindow=5000`

### Futures (history_orders, order_deals)
- Base URL: `https://futures.ourbit.com`
- Headers: `ApiKey`, `Request-Time`, `Signature`, `Content-Type: application/json`
- Signature string: `accessKey + timestamp + parameterString`
- Signature: `HMAC-SHA256(sign_string, OURBIT_API_SECRET)`
- Parameters: snake_case, sorted alphabetically, joined with `&`

## Storage Structure

```
/data/.hermes/reports/crypto-portfolio-watch/
  raw/{YYYY-MM-DD}/          # Raw API responses (7 day retention)
  normalized/{YYYY-MM-DD}/   # Cleaned + deduped data (30 day retention)
  daily/{YYYY-MM-DD}.md      # Daily reports (30 report retention)
  state/
    symbol_registry.json     # Known symbols with validation status
    dedup_hashes.json        # Seen record hashes
  latest.md                 # Symlink/copy of most recent report
```

## Retention

- `raw/`: 7 days
- `normalized/`: 30 days
- `daily/`: 30 reports
- `state/`: Permanent (with size control)

## Dedup Strategy

- Spot trade: `SHA256("spot_trade:" + trade_id)`
- Spot order: `SHA256("spot_order:" + order_id)` — excludes status/state for update detection
- Futures order: `SHA256("futures_order:" + order_id)` — excludes state
- Futures deal: `SHA256("futures_deal:" + deal_id)`
- Fallback hash from stable fields if ID missing: `dedup_confidence: "fallback"`
- IDs (orderId, clientOrderId, etc.) never stored in normalized/report — only hashes

## Report Language Rules

### Allowed phrases
- فعالیت معاملاتی ثبت‌شده
- خرید و فروش مشاهده‌شده
- سفارش باز مشاهده‌شده
- سود و زیان ثبت‌شده Futures
- داده ناقص یا غیرقابل دریافت

### Forbidden phrases (without direct data)
- موجودی فعلی قطعی
- ارزش کل قطعی سبد
- پوزیشن باز قطعی Futures
- مارجین فعلی حساب

## Known Limitations

1. `/api/v3/account` returns 700007 — no direct balance
2. Futures position listing not in official docs
3. Futures margin/balance not in official docs
4. Data window limited to ~7 days from API
5. Deposits, withdrawals, transfers not visible
6. Airdrops not visible

## Symbol Registry

Symbols must be validated against `exchangeInfo` before use.
Invalid symbols are logged but do not stop execution.
See `state/symbol_registry.json` for current list.

## Security Rules

1. API Key only from env `OURBIT_API_KEY`
2. Secret only from env `OURBIT_API_SECRET`
3. Env values never written to files, logs, or output
4. Signature, auth headers, signed queries never saved or printed
5. Raw private responses sanitized before storage
6. IDs removed or hashed in raw storage
7. Only GET requests — no POST/PUT/PATCH/DELETE
8. No trading, cancellation, transfer, withdrawal, or leverage changes
9. No self-improvement or auto-patching
10. No modification to other Skills
