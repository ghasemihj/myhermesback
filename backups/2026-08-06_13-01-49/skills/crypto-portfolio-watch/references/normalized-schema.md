# Normalized Data Schema Reference

## Directory Structure

```
normalized/{YYYY-MM-DD}/
  manifest.json
  spot_trades.json
  spot_orders.json
  spot_open_orders.json
  futures_orders.json
  futures_deals.json
```

---

## manifest.json

```json
{
  "collected_at": "ISO-8601",
  "date": "YYYY-MM-DD",
  "endpoints": {
    "spot_mytrades": {
      "requested": "GET /api/v3/myTrades",
      "success": true,
      "http_status": 200,
      "api_code": null,
      "records_received": 42,
      "pages_received": 1,
      "complete": true,
      "error_type": null,
      "collected_at": "ISO-8601"
    }
  },
  "valid_symbols": 19,
  "invalid_symbols": 0,
  "total_normalized": {
    "spot_trades": 42,
    "spot_orders": 15,
    "spot_open_orders": 3,
    "futures_orders": 8,
    "futures_deals": 5
  }
}
```

---

## spot_trades.json

```json
{
  "collected_at": "ISO-8601",
  "trades": [
    {
      "trade_hash": "sha256-hex",
      "dedup_confidence": "id | fallback",
      "symbol": "GIGGLEUSDT",
      "price": "1.234",
      "qty": "100",
      "quoteQty": "123.40",
      "commission": "0.1",
      "commissionAsset": "USDT",
      "isBuyer": true,
      "isMaker": false,
      "time": 1785511886883
    }
  ],
  "total_count": 1
}
```

### Dedup Hash
- Primary: `SHA256("spot_trade:" + trade_id)`
- Fallback: `SHA256("spot_trade:fb:symbol|price|qty|time|isBuyer")`

---

## spot_orders.json

```json
{
  "collected_at": "ISO-8601",
  "orders": [
    {
      "order_hash": "sha256-hex",
      "dedup_confidence": "id | fallback",
      "symbol": "GIGGLEUSDT",
      "side": "BUY",
      "type": "LIMIT",
      "status": "FILLED",
      "origQty": "100",
      "executedQty": "100",
      "cummulativeQuoteQty": "123.40",
      "time": 1785511886883,
      "updateTime": 1785518886883
    }
  ],
  "status_changes": [
    {
      "hash": "sha256-hex",
      "old": "NEW",
      "new": "FILLED"
    }
  ],
  "total_count": 1
}
```

### Dedup Hash
- Primary: `SHA256("spot_order:" + orderId)`
- **Excludes status** — allows update detection
- Fallback: `SHA256("spot_order:fb:symbol|side|type|origQty|time")`

---

## spot_open_orders.json

```json
{
  "collected_at": "ISO-8601",
  "orders": [
    {
      "symbol": "GIGGLEUSDT",
      "side": "BUY",
      "type": "LIMIT",
      "origQty": "100",
      "price": "1.200",
      "time": 1785511886883
    }
  ],
  "total_count": 1
}
```

Note: Open orders are a current snapshot — no dedup applied.

---

## futures_orders.json

```json
{
  "collected_at": "ISO-8601",
  "orders": [
    {
      "order_hash": "sha256-hex",
      "dedup_confidence": "id | fallback",
      "symbol": "BTC_USDT",
      "price": "68000",
      "vol": "1",
      "leverage": 20,
      "side": 1,
      "category": 1,
      "orderType": 1,
      "dealAvgPrice": "68050",
      "dealVol": "1",
      "orderMargin": "3.4",
      "profit": "0.5",
      "feeCurrency": "USDT",
      "openType": 2,
      "state": 3,
      "usedMargin": "3.4",
      "createTime": "ISO-8601",
      "updateTime": "ISO-8601"
    }
  ],
  "state_changes": [
    {
      "hash": "sha256-hex",
      "old": 2,
      "new": 3
    }
  ],
  "total_count": 1
}
```

### Dedup Hash
- Primary: `SHA256("futures_order:" + orderId)`
- **Excludes state** — allows state change detection
- Fallback: `SHA256("futures_order:fb:symbol|price|vol|side|createTime")`

### State Values
| Value | Name |
|-------|------|
| 1 | Pending |
| 2 | Incomplete |
| 3 | Completed |
| 4 | Cancelled |
| 5 | Invalid |

### Side Values
| Value | Name |
|-------|------|
| 1 | Open Long |
| 2 | Close Short |
| 3 | Open Short |
| 4 | Close Long |

### OpenType Values
| Value | Name |
|-------|------|
| 1 | Isolated |
| 2 | Cross |

---

## futures_deals.json

```json
{
  "collected_at": "ISO-8601",
  "deals": [
    {
      "deal_hash": "sha256-hex",
      "dedup_confidence": "id | fallback",
      "symbol": "BTC_USDT",
      "price": "68050",
      "vol": 1,
      "fee": "0.034",
      "feeCurrency": "USDT",
      "profit": "0.5",
      "side": 1,
      "category": 1,
      "taker": true,
      "timestamp": 1785511886883
    }
  ],
  "total_count": 1
}
```

### Dedup Hash
- Primary: `SHA256("futures_deal:" + deal_id)`
- Fallback: `SHA256("futures_deal:fb:symbol|price|vol|side|timestamp")`

---

## Raw Storage

Files in `raw/{date}/` contain sanitized data where sensitive IDs are replaced:
- `orderId` → `orderId_hash` (SHA256)
- `clientOrderId` → `clientOrderId_hash`
- `positionId` → `positionId_hash`
- `externalOid` → `externalOid_hash`
- `id` → `id_hash`

All other fields are preserved as-is from the API response.
