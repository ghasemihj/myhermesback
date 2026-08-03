---
name: exchange-api-monitoring
description: "Exchange API: read-only auth, balances, positions, reports."
version: 1.0.0
---

# Exchange API Monitoring

Secure read-only integration with cryptocurrency exchange APIs for portfolio monitoring and daily reporting.

## Trigger

When the user asks to connect to, test, query, or build reports from a cryptocurrency exchange API (Ourbit, Binance, etc.).

## Workflow

### 1. Credential Setup

- Credentials are stored as **Railway environment variables** — never in skills, logs, reports, memory, or GitHub.
- Variable naming convention: `<EXCHANGE>_API_KEY` and `<EXCHANGE>_API_SECRET`
- User will confirm when variables are defined. Never ask for actual values.
- Verify presence and non-empty status before any API call.

### 2. Documentation Discovery

- Always locate **official API docs** before making any request. Never guess endpoints or auth methods.
- If docs cannot be found, STOP and report — do not invent endpoints.
- Record the docs URL used in the test report.

### 3. Time Synchronization Check

- Before any signed request, check server time vs local time via the exchange's public time endpoint.
- If time difference exceeds `recvWindow` (typically 5000ms), STOP and report the drift.
- Ourbit time endpoint: `GET /api/v3/time` (public, no auth).

### 4. Authentication Test

- Use **only GET** endpoints for initial testing.
- Build the signed request per the exchange's documented method (typically HMAC-SHA256).
- Test the least-privileged authenticated endpoint first (e.g., account info).
- Report the result in a structured format (see template below).

### 5. Security Report Template

```
- Documentation URL used
- Variables present: Yes/No
- Server-time check: Success/Failed (+ drift in ms)
- Endpoint tested
- HTTP method
- Authentication: Success/Failed
- HTTP status
- Account permissions returned (canTrade, canWithdraw, canDeposit)
- Non-zero assets count
- Three sample asset symbols (no amounts)
- Mutating operation performed: No
- Secret displayed or stored: No
```

## User Security Rules (Jason)

These are non-negotiable when working with Jason's exchange APIs:

1. **NEVER display** API Key or Secret values in any output.
2. **NEVER log** full signed query strings (they contain the signature).
3. **NEVER show** full request headers.
4. **NEVER show** full raw API responses.
5. **NEVER create** POST, PUT, or DELETE requests during testing.
6. **NEVER show** account IDs, wallet addresses, TxIDs, or other sensitive data.
7. **NEVER save** data to disk, skills, logs, or reports during initial testing.
8. Only the explicitly authorized GET endpoint may be called.
9. **NEVER create** Skills, Cron jobs, or automation unless explicitly asked.

## Progressive Testing Workflow

Before building any collection system, test endpoints **one at a time** in this order:

1. **Public endpoint** (time, exchangeInfo) — confirm base URL and connectivity
2. **Time sync check** — verify clock drift within recvWindow
3. **Least-privileged signed endpoint** — test authentication works
4. **Each data endpoint individually** — confirm permissions, response shape, field presence
5. **Only then** build the full collection + report system

The user explicitly directs this workflow. Do NOT skip ahead or batch-test. Each endpoint must be confirmed working before moving to the next.

## Script Patterns

### Test mode (`--test` flag)

Collection scripts should support a `--test` mode for safe manual execution:
- Single symbol only (e.g., GIGGLEUSDT)
- Max 1 page per endpoint
- Max N records (e.g., 5) per endpoint
- Skips full symbol validation
- Adds `test_mode` flag to manifest

Usage: `python3 collect.py --test`

### Error isolation

If one endpoint fails, the entire collection should NOT stop. Each endpoint's result is recorded independently in the manifest. Other endpoints continue.

## Report Generation Rules (User Preference)

These rules are **mandatory** for all daily reports. Never make them conditional:

### Always show (even when complete/empty):
- **Data quality status**: Overall (Complete/Partial/Failed) + counts (X/5 successful)
- **Endpoint status table**: All endpoints with success, HTTP, API code, records, pages, complete, error
- **Timestamps**: Collection start, collection end, report generation time, timezone
- **Received vs new records**: For each data source show BOTH "records received from API" (from manifest) AND "new unique records after dedup" (from normalized). Never confuse the two. Snapshot endpoints (openOrders) show current count directly, not deduped count.

### Language rules:
- Use ONLY approved phrases: "فعالیت معاملاتی ثبت‌شده", "خرید و فروش مشاهده‌شده", "سود و زیان ثبت‌شده"
- NEVER claim: "موجودی فعلی قطعی", "ارزش کل قطعی سبد", "پوزیشن باز قطعی Futures"
- Always include data limitations warning at top
- Exact prices, amounts, and PnL may appear in file reports but NOT in Telegram output

### Data quality calculation:
- **Complete**: All 5 endpoints have success=true AND complete=true
- **Partial**: At least one succeeds but some fail/incomplete
- **Failed**: No endpoint succeeds

## Data Pipeline Pattern

### Storage structure
```
reports/{project}/
  raw/{YYYY-MM-DD}/          # Sanitized raw responses (7-day retention)
  normalized/{YYYY-MM-DD}/   # Cleaned + deduped (30-day retention)
  daily/{YYYY-MM-DD}.md      # Reports (30-report retention)
  state/
    symbol_registry.json     # Known symbols + validation status
    dedup_hashes.json        # Seen record hashes
  latest.md                 # Most recent report
```

### Dedup strategy
- **Primary hash**: `SHA256("prefix:" + record_id)` — e.g., trade ID, order ID
- **Fallback hash**: `SHA256("prefix:fb:field1|field2|...")` — when ID missing
- For orders: hash **excludes** status/state to enable change detection
- Track status changes separately for report diffs
- IDs never stored in normalized files — only hashes

### Symbol validation
- Validate all symbols against public `exchangeInfo` endpoint before use
- Invalid symbols logged but do NOT stop execution
- Registry tracks: symbol, status (valid/invalid/pending), last_validated timestamp

### Raw sanitization
- Replace sensitive IDs (orderId, clientOrderId, positionId, etc.) with `_hash` variants
- Keep all other fields as-is
- Never store raw private responses without sanitization

## Pitfalls

### Pagination counter off-by-one
- **Bug**: Using `page - 1` as page count when the loop runs once and breaks early → `pages_received=0` despite successful fetch.
- **Symptom**: Manifest shows `pages_received: 0` but `records_received > 0`.
- **Fix**: Use a separate `pages_received` counter that increments only after a successful page fetch:
  ```python
  pages_received = 0
  for page in range(1, max_pages + 1):
      status, body, _ = request(...)
      if status != 200: break
      pages_received += 1  # increment AFTER success
      records.extend(body)
      if len(body) < limit: break
  return records, pages_received
  ```
- **Applies to**: Both Spot and Futures pagination functions.

### "Collected but empty after dedup" vs "not collected"
- **Bug**: Report says "data not available" when data was actually collected but all records were filtered by dedup.
- **Symptom**: Normalized file has `collected_at` (proving collection happened) but empty list.
- **Fix**: Check `collected_at` in the normalized file:
  - `data is None` → not collected at all
  - `collected_at` present but list empty → collected, all deduped
  - No `collected_at` and empty → genuinely no data
- **Applies to**: Any summarizer/report function reading normalized data.

### execute_code vs terminal for API calls
- `execute_code` sandbox **blocks outgoing network requests** — use `terminal` with Python subprocess for API calls that need network access.
- When using `terminal` with Python heredocs, some exchanges (including Ourbit) return **403 Forbidden** to `urllib.request` without a User-Agent header. Use `curl` via subprocess with `-H "User-Agent: Mozilla/5.0"` instead.

### Error code 700007 (Ourbit-specific)
- Means "No permission to access the endpoint" — the API Key exists and signature is valid, but the Key lacks the required permission scope.
- Fix: User must enable the correct permission (e.g., "Enable Reading") in the exchange's API Key management page.

### Signature verification
- If signature is wrong, exchanges typically return error code `700001` (Invalid signature).
- If you get a *specific* API error code (not a generic auth failure), the signature was accepted — the issue is permissions or parameters.

## Ourbit Futures API (Separate from Spot!)

Ourbit Futures uses a **completely different** authentication and base URL than Spot.

### Key Differences

| Aspect | Spot | Futures |
|--------|------|---------|
| Base URL | `https://api.ourbit.com` | `https://futures.ourbit.com` |
| Auth location | Query string signature | Request headers |
| Header auth | `X-OURBIT-APIKEY` only | `ApiKey`, `Request-Time`, `Signature` |
| Signature input | Query string params | `accessKey + timestamp + paramStr` |
| POST format | N/A | JSON body, `camelCase` |
| GET format | Query params | Query params, `snake_case` |
| Documentation | `spot_v3_en` | `contract_en` |

### Futures Signature Method

For **GET/DELETE**: Sort params alphabetically, join with `&`, then:
```
sign_str = accessKey + timestamp + "param1=val1&param2=val2"
signature = HMAC-SHA256(sign_str, secretKey)  # lowercase hex
```

For **POST**: Use the JSON body string (no sorting needed).

Headers to send: `ApiKey`, `Request-Time` (ms string), `Signature`, `Content-Type: application/json`.

### Futures Documentation

- URL: `https://ourbitdevelop.github.io/apidocs/contract_en/`
- Only **2 read-only endpoints** are documented as of 2026-07-31:
  - `GET api/v1/private/order/list/history_orders` — Order history (has `profit` field)
  - `GET api/v1/private/order/list/order_deals` — Trade/fill history
- Both require: `Futures trading read permission`
- Rate limit: 20 requests per 2 seconds

### Futures Limitations (as of 2026-07-31)

The official Ourbit Futures API docs do **NOT** include endpoints for:
- Open positions (not documented)
- Account/margin balance (not documented)
- Open orders (not documented)
- Funding fees (not documented)

Workaround: Use `history_orders` + `order_deals` for trade history and realized PnL.

## References

- `references/ourbit-api.md` — Ourbit exchange API endpoints, auth method, error codes.
