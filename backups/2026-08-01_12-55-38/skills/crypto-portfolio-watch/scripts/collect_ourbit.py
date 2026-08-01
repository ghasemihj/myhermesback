#!/usr/bin/env python3
"""
collect_ourbit.py — Read-only data collection for Ourbit crypto portfolio.

Spot API:    HMAC-SHA256 on query string
Futures API: HMAC-SHA256 on header (accessKey + timestamp + params)

SECURITY:
- API Key/Secret read ONLY from environment variables
- Never printed, logged, or written to any file
- Only GET requests — no POST/PUT/PATCH/DELETE
- No trading, transfer, or withdrawal operations
"""

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

# ── Configuration ──────────────────────────────────────────────

DATA_ROOT = os.environ.get(
    "CRYPTO_WATCH_DATA_ROOT",
    "/data/.hermes/reports/crypto-portfolio-watch",
)
STATE_DIR = os.path.join(DATA_ROOT, "state")
RAW_DIR = os.path.join(DATA_ROOT, "raw")
NORM_DIR = os.path.join(DATA_ROOT, "normalized")

SPOT_BASE = "https://api.ourbit.com"
FUTURES_BASE = "https://futures.ourbit.com"

USER_AGENT = "Mozilla/5.0"
RECV_WINDOW = "5000"
FUTURES_RECV_WINDOW = "60"

MAX_RETRIES = 3
RETRY_DELAY = [0, 3, 5]  # seconds per attempt
PAGE_SIZE = 100  # Spot max
FUTURES_PAGE_SIZE = 100  # Futures max

# Test mode config (set by --test flag)
TEST_MODE = False
TEST_SYMBOL = "GIGGLEUSDT"
TEST_MAX_RECORDS = 5
TEST_MAX_PAGES = 1

IRST = timezone(timedelta(hours=3, minutes=30))

# Sensitive ID fields to strip from raw storage
SENSITIVE_FIELDS = {
    "orderId", "clientOrderId", "externalOid", "positionId",
    "orderListId", "id",
}


# ── Utilities ──────────────────────────────────────────────────

def now_irst():
    return datetime.now(IRST)


def today_str():
    return now_irst().strftime("%Y-%m-%d")


def now_iso():
    return now_irst().isoformat()


def sha256_hex(data_str):
    return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


def get_env(key):
    val = os.environ.get(key, "")
    if not val:
        print(f"[FATAL] Environment variable {key} not set", file=sys.stderr)
        sys.exit(1)
    return val


def ensure_dirs():
    for d in [DATA_ROOT, STATE_DIR, RAW_DIR, NORM_DIR,
              os.path.join(RAW_DIR, today_str()),
              os.path.join(NORM_DIR, today_str())]:
        os.makedirs(d, exist_ok=True)


def load_json(path, default=None):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def http_request(url, headers=None, timeout=15):
    """Make a GET request. Returns (status_code, body_dict) or raises."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        body = json.loads(resp.read().decode("utf-8"))
        return resp.getcode(), body
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8", errors="replace"))
        except Exception:
            body = {"error": str(e)}
        return e.code, body
    except Exception as e:
        return 0, {"error": str(e)}


def request_with_retry(url, headers=None, label="request"):
    """Retry logic. Returns (status, body, attempt)."""
    for attempt in range(MAX_RETRIES):
        if attempt > 0:
            time.sleep(RETRY_DELAY[min(attempt, len(RETRY_DELAY) - 1)])
        status, body = http_request(url, headers=headers)
        if status == 200:
            if isinstance(body, dict) and body.get("success") is False:
                return status, body, attempt + 1
            return status, body, attempt + 1
        if status == 429:
            continue  # rate limit, retry
        if status >= 500:
            continue  # server error, retry
        return status, body, attempt + 1
    return status, body, attempt + 1


# ── Spot Authentication ────────────────────────────────────────

def spot_sign(api_key, api_secret, params_dict):
    """Sign Spot request: HMAC-SHA256(query_string, secret)."""
    qs = urllib.parse.urlencode(sorted(params_dict.items()))
    sig = hmac.new(
        api_secret.encode("utf-8"),
        qs.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return qs + "&signature=" + sig


def spot_request(api_key, api_secret, path, extra_params=None):
    """Make authenticated Spot GET request."""
    params = {
        "timestamp": str(int(time.time() * 1000)),
        "recvWindow": RECV_WINDOW,
    }
    if extra_params:
        params.update(extra_params)
    full_qs = spot_sign(api_key, api_secret, params)
    url = f"{SPOT_BASE}{path}?{full_qs}"
    headers = {"X-OURBIT-APIKEY": api_key}
    return request_with_retry(url, headers=headers, label=f"spot:{path}")


def spot_public_request(path, params=None):
    """Make unauthenticated Spot GET request."""
    qs = urllib.parse.urlencode(params or {})
    url = f"{SPOT_BASE}{path}" + (f"?{qs}" if qs else "")
    return request_with_retry(url, label=f"spot_public:{path}")


# ── Futures Authentication ─────────────────────────────────────

def futures_sign(api_key, api_secret, timestamp, param_string):
    """Sign Futures request: HMAC-SHA256(accessKey + timestamp + params, secret)."""
    sign_input = api_key + timestamp + param_string
    return hmac.new(
        api_secret.encode("utf-8"),
        sign_input.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def futures_request(api_key, api_secret, path, params=None):
    """Make authenticated Futures GET request."""
    ts = str(int(time.time() * 1000))
    if params:
        param_string = urllib.parse.urlencode(sorted(params.items()))
    else:
        param_string = ""
    sig = futures_sign(api_key, api_secret, ts, param_string)
    qs = ("?" + param_string) if param_string else ""
    url = f"{FUTURES_BASE}{path}{qs}"
    headers = {
        "ApiKey": api_key,
        "Request-Time": ts,
        "Signature": sig,
        "Content-Type": "application/json",
    }
    return request_with_retry(url, headers=headers, label=f"futures:{path}")


def futures_public_request(path):
    """Make unauthenticated Futures GET request."""
    url = f"{FUTURES_BASE}{path}"
    return request_with_retry(url, label=f"futures_public:{path}")


# ── Pagination Helpers ─────────────────────────────────────────

def fetch_spot_paginated(api_key, api_secret, path, symbol, max_pages=20):
    """Fetch all pages from a Spot endpoint requiring symbol."""
    if TEST_MODE:
        max_pages = TEST_MAX_PAGES
    all_records = []
    pages_received = 0
    limit = str(TEST_MAX_RECORDS if TEST_MODE else PAGE_SIZE)
    for page in range(1, max_pages + 1):
        params = {"symbol": symbol, "limit": limit}
        status, body, _ = spot_request(api_key, api_secret, path, params)
        if status != 200 or not isinstance(body, list):
            break
        pages_received += 1
        all_records.extend(body)
        if len(body) < int(limit):
            break
    return all_records, pages_received


def fetch_spot_open_orders_all(api_key, api_secret, symbols):
    """Fetch open orders for all valid symbols."""
    all_records = []
    pages = 0
    for sym in symbols:
        status, body, _ = spot_request(
            api_key, api_secret, "/api/v3/openOrders", {"symbol": sym}
        )
        if status == 200 and isinstance(body, list):
            all_records.extend(body)
            pages += 1
        if TEST_MODE:
            break  # only first symbol in test
    if TEST_MODE and len(all_records) > TEST_MAX_RECORDS:
        all_records = all_records[:TEST_MAX_RECORDS]
    return all_records, pages


def fetch_futures_paginated(api_key, api_secret, path, max_pages=20):
    """Fetch all pages from a Futures endpoint (no symbol required)."""
    if TEST_MODE:
        max_pages = TEST_MAX_PAGES
    all_records = []
    pages_received = 0
    page_size = str(TEST_MAX_RECORDS if TEST_MODE else FUTURES_PAGE_SIZE)
    for page in range(1, max_pages + 1):
        params = {"page_num": str(page), "page_size": page_size}
        status, body, _ = futures_request(api_key, api_secret, path, params)
        if status != 200 or not isinstance(body, dict) or not body.get("success"):
            break
        pages_received += 1
        data = body.get("data", {})
        records = data.get("list", []) if isinstance(data, dict) else data
        if isinstance(records, list):
            all_records.extend(records)
        if len(records) < int(page_size):
            break
    return all_records, pages_received


# ── Dedup ──────────────────────────────────────────────────────

def make_dedup_hash(prefix, record_id, fallback_fields=None, fallback_vals=None):
    """Create dedup hash. If record_id exists, use it. Otherwise use fallback fields."""
    if record_id:
        return sha256_hex(f"{prefix}:{record_id}"), "id"
    if fallback_fields and fallback_vals:
        fallback_str = "|".join(str(fallback_vals.get(f, "")) for f in fallback_fields)
        return sha256_hex(f"{prefix}:fb:{fallback_str}"), "fallback"
    return None, "none"


def load_dedup_state():
    return load_json(os.path.join(STATE_DIR, "dedup_hashes.json"), {
        "spot_trades": [], "spot_orders": [],
        "futures_orders": [], "futures_deals": [],
    })


def save_dedup_state(state):
    # Compose: keep only last 10000 hashes per category
    for key in state:
        if isinstance(state[key], list) and len(state[key]) > 10000:
            state[key] = state[key][-10000:]
    save_json(os.path.join(STATE_DIR, "dedup_hashes.json"), state)


# ── Symbol Validation ──────────────────────────────────────────

def load_symbol_registry():
    return load_json(os.path.join(STATE_DIR, "symbol_registry.json"), {"symbols": {}})


def save_symbol_registry(reg):
    save_json(os.path.join(STATE_DIR, "symbol_registry.json"), reg)


def validate_symbols(registry):
    """Validate all symbols against exchangeInfo. Update registry status."""
    status, body, _ = spot_public_request("/api/v3/exchangeInfo")
    if status != 200 or not isinstance(body, dict):
        print(f"[WARN] exchangeInfo fetch failed (HTTP {status})")
        return registry

    valid_symbols = set()
    for s in body.get("symbols", []):
        valid_symbols.add(s.get("symbol", ""))

    for sym in list(registry.get("symbols", {}).keys()):
        if sym in valid_symbols:
            registry["symbols"][sym]["status"] = "valid"
            registry["symbols"][sym]["last_validated"] = now_iso()
        else:
            old_status = registry["symbols"][sym].get("status", "unknown")
            registry["symbols"][sym]["status"] = "invalid"
            registry["symbols"][sym]["last_validated"] = now_iso()
            if old_status == "valid":
                print(f"[WARN] Symbol {sym} was valid but now invalid")
    return registry


# ── Raw Storage Sanitization ──────────────────────────────────

def sanitize_raw_record(record):
    """Remove sensitive IDs from raw record. Returns copy."""
    clean = {}
    for k, v in record.items():
        if k in SENSITIVE_FIELDS:
            # Keep hash only
            clean[k + "_hash"] = sha256_hex(str(v))
        else:
            clean[k] = v
    return clean


def save_raw(date_str, name, data):
    """Save sanitized raw data."""
    path = os.path.join(RAW_DIR, date_str, f"{name}.json")
    if isinstance(data, list):
        cleaned = [sanitize_raw_record(r) for r in data]
    elif isinstance(data, dict):
        cleaned = {k: sanitize_raw_record(v) if isinstance(v, dict) else v
                   for k, v in data.items()}
    else:
        cleaned = data
    save_json(path, cleaned)


# ── Collection: Spot ───────────────────────────────────────────

def collect_spot_mytrades(api_key, api_secret, symbols):
    """Collect all Spot trades across symbols."""
    all_trades = []
    pages_total = 0
    manifest = {
        "requested": "GET /api/v3/myTrades",
        "success": False, "http_status": 0, "api_code": None,
        "records_received": 0, "pages_received": 0, "complete": False,
        "error_type": None, "collected_at": now_iso(),
    }

    for sym in symbols:
        records, pages = fetch_spot_paginated(
            api_key, api_secret, "/api/v3/myTrades", sym
        )
        pages_total += pages
        all_trades.extend(records)

    if all_trades:
        manifest["success"] = True
        manifest["http_status"] = 200
        manifest["records_received"] = len(all_trades)
        manifest["pages_received"] = pages_total
        manifest["complete"] = True
    else:
        manifest["success"] = True  # Empty is valid
        manifest["http_status"] = 200
        manifest["records_received"] = 0
        manifest["pages_received"] = pages_total
        manifest["complete"] = True
        manifest["error_type"] = "empty"

    save_raw(today_str(), "spot_mytrades_raw", all_trades)
    return all_trades, manifest


def collect_spot_allorders(api_key, api_secret, symbols):
    """Collect all Spot orders across symbols."""
    all_orders = []
    pages_total = 0
    manifest = {
        "requested": "GET /api/v3/allOrders",
        "success": False, "http_status": 0, "api_code": None,
        "records_received": 0, "pages_received": 0, "complete": False,
        "error_type": None, "collected_at": now_iso(),
    }

    for sym in symbols:
        records, pages = fetch_spot_paginated(
            api_key, api_secret, "/api/v3/allOrders", sym
        )
        pages_total += pages
        all_orders.extend(records)

    if all_orders or pages_total > 0:
        manifest["success"] = True
        manifest["http_status"] = 200
        manifest["records_received"] = len(all_orders)
        manifest["pages_received"] = pages_total
        manifest["complete"] = True
    else:
        manifest["success"] = True
        manifest["http_status"] = 200
        manifest["records_received"] = 0
        manifest["pages_received"] = 0
        manifest["complete"] = True
        manifest["error_type"] = "empty"

    save_raw(today_str(), "spot_allorders_raw", all_orders)
    return all_orders, manifest


def collect_spot_openorders(api_key, api_secret, symbols):
    """Collect open orders across all valid symbols."""
    all_orders, pages = fetch_spot_open_orders_all(api_key, api_secret, symbols)
    manifest = {
        "requested": "GET /api/v3/openOrders",
        "success": True, "http_status": 200, "api_code": None,
        "records_received": len(all_orders), "pages_received": pages,
        "complete": True, "error_type": None, "collected_at": now_iso(),
    }
    save_raw(today_str(), "spot_openorders_raw", all_orders)
    return all_orders, manifest


# ── Collection: Futures ────────────────────────────────────────

def collect_futures_history_orders(api_key, api_secret):
    """Collect Futures order history."""
    records, pages = fetch_futures_paginated(
        api_key, api_secret, "/api/v1/private/order/list/history_orders"
    )
    manifest = {
        "requested": "GET /api/v1/private/order/list/history_orders",
        "success": True, "http_status": 200, "api_code": None,
        "records_received": len(records), "pages_received": pages,
        "complete": True, "error_type": None, "collected_at": now_iso(),
    }
    if not records:
        manifest["error_type"] = "empty"
    save_raw(today_str(), "futures_history_orders_raw", records)
    return records, manifest


def collect_futures_order_deals(api_key, api_secret):
    """Collect Futures deal history."""
    records, pages = fetch_futures_paginated(
        api_key, api_secret, "/api/v1/private/order/list/order_deals"
    )
    manifest = {
        "requested": "GET /api/v1/private/order/list/order_deals",
        "success": True, "http_status": 200, "api_code": None,
        "records_received": len(records), "pages_received": pages,
        "complete": True, "error_type": None, "collected_at": now_iso(),
    }
    if not records:
        manifest["error_type"] = "empty"
    save_raw(today_str(), "futures_order_deals_raw", records)
    return records, manifest


# ── Normalization ──────────────────────────────────────────────

def normalize_spot_trades(trades, dedup_state):
    """Normalize and dedup Spot trades."""
    normalized = []
    new_hashes = []
    for t in trades:
        trade_id = t.get("id") or t.get("trade_id")
        fb_fields = ["symbol", "price", "qty", "time", "isBuyer"]
        h, conf = make_dedup_hash("spot_trade", trade_id, fb_fields, t)
        if not h:
            continue
        if h in dedup_state["spot_trades"]:
            continue
        dedup_state["spot_trades"].append(h)
        new_hashes.append(h)
        normalized.append({
            "trade_hash": h,
            "dedup_confidence": conf,
            "symbol": t.get("symbol", ""),
            "price": t.get("price", ""),
            "qty": t.get("qty", ""),
            "quoteQty": t.get("quoteQty", ""),
            "commission": t.get("commission", ""),
            "commissionAsset": t.get("commissionAsset", ""),
            "isBuyer": t.get("isBuyer", None),
            "isMaker": t.get("isMaker", None),
            "time": t.get("time", 0),
        })
    return normalized


def normalize_spot_orders(orders, dedup_state):
    """Normalize and dedup Spot orders. Track status changes."""
    normalized = []
    new_hashes = []
    changes = []
    for o in orders:
        order_id = o.get("orderId") or o.get("id")
        # Hash WITHOUT status/state for update detection
        fb_fields = ["symbol", "side", "type", "origQty", "time"]
        h, conf = make_dedup_hash("spot_order", order_id, fb_fields, o)
        if not h:
            continue
        status = o.get("status", "")
        existing = dedup_state.get("_spot_order_status", {}).get(h)
        if existing and existing != status:
            changes.append({"hash": h, "old": existing, "new": status})
        dedup_state.setdefault("_spot_order_status", {})[h] = status
        if h in dedup_state["spot_orders"]:
            continue
        dedup_state["spot_orders"].append(h)
        new_hashes.append(h)
        normalized.append({
            "order_hash": h,
            "dedup_confidence": conf,
            "symbol": o.get("symbol", ""),
            "side": o.get("side", ""),
            "type": o.get("type", ""),
            "status": status,
            "origQty": o.get("origQty", ""),
            "executedQty": o.get("executedQty", ""),
            "cummulativeQuoteQty": o.get("cummulativeQuoteQty", ""),
            "time": o.get("time", 0),
            "updateTime": o.get("updateTime", 0),
        })
    return normalized, changes


def normalize_spot_open_orders(orders):
    """Normalize open orders (no dedup — always current snapshot)."""
    normalized = []
    for o in orders:
        normalized.append({
            "symbol": o.get("symbol", ""),
            "side": o.get("side", ""),
            "type": o.get("type", ""),
            "origQty": o.get("origQty", ""),
            "price": o.get("price", ""),
            "time": o.get("time", 0),
        })
    return normalized


def normalize_futures_orders(orders, dedup_state):
    """Normalize and dedup Futures orders. Track state changes."""
    normalized = []
    changes = []
    for o in orders:
        order_id = o.get("orderId")
        fb_fields = ["symbol", "price", "vol", "side", "createTime"]
        h, conf = make_dedup_hash("futures_order", order_id, fb_fields, o)
        if not h:
            continue
        state = o.get("state")
        existing = dedup_state.get("_futures_order_state", {}).get(h)
        if existing is not None and existing != state:
            changes.append({"hash": h, "old": existing, "new": state})
        dedup_state.setdefault("_futures_order_state", {})[h] = state
        dedup_state["futures_orders"].append(h)
        normalized.append({
            "order_hash": h,
            "dedup_confidence": conf,
            "symbol": o.get("symbol", ""),
            "price": o.get("price", ""),
            "vol": o.get("vol", ""),
            "leverage": o.get("leverage", ""),
            "side": o.get("side", ""),
            "category": o.get("category", ""),
            "orderType": o.get("orderType", ""),
            "dealAvgPrice": o.get("dealAvgPrice", ""),
            "dealVol": o.get("dealVol", ""),
            "orderMargin": o.get("orderMargin", ""),
            "profit": o.get("profit", ""),
            "feeCurrency": o.get("feeCurrency", ""),
            "openType": o.get("openType", ""),
            "state": state,
            "usedMargin": o.get("usedMargin", ""),
            "createTime": o.get("createTime", ""),
            "updateTime": o.get("updateTime", ""),
        })
    return normalized, changes


def normalize_futures_deals(deals, dedup_state):
    """Normalize and dedup Futures deals."""
    normalized = []
    for d in deals:
        deal_id = d.get("id")
        fb_fields = ["symbol", "price", "vol", "side", "timestamp"]
        h, conf = make_dedup_hash("futures_deal", deal_id, fb_fields, d)
        if not h:
            continue
        if h in dedup_state["futures_deals"]:
            continue
        dedup_state["futures_deals"].append(h)
        normalized.append({
            "deal_hash": h,
            "dedup_confidence": conf,
            "symbol": d.get("symbol", ""),
            "price": d.get("price", ""),
            "vol": d.get("vol", ""),
            "fee": d.get("fee", ""),
            "feeCurrency": d.get("feeCurrency", ""),
            "profit": d.get("profit", ""),
            "side": d.get("side", ""),
            "category": d.get("category", ""),
            "taker": d.get("taker", None),
            "timestamp": d.get("timestamp", 0),
        })
    return normalized


# ── Retention Cleanup ──────────────────────────────────────────

def cleanup_retention():
    """Remove old data based on retention policy."""
    now = now_irst()

    # raw: 7 days
    _cleanup_dir(RAW_DIR, days=7, now=now)
    # normalized: 30 days
    _cleanup_dir(NORM_DIR, days=30, now=now)
    # daily reports: 30 files
    _cleanup_daily_reports(keep=30)


def _cleanup_dir(base_dir, days, now):
    cutoff = now - timedelta(days=days)
    for name in os.listdir(base_dir):
        try:
            dir_date = datetime.strptime(name, "%Y-%m-%d").replace(tzinfo=IRST)
            if dir_date < cutoff:
                import shutil
                shutil.rmtree(os.path.join(base_dir, name))
        except (ValueError, OSError):
            pass


def _cleanup_daily_reports(keep):
    daily_dir = os.path.join(DATA_ROOT, "daily")
    files = sorted(
        [f for f in os.listdir(daily_dir) if f.endswith(".md")],
        reverse=True,
    )
    for f in files[keep:]:
        try:
            os.remove(os.path.join(daily_dir, f))
        except OSError:
            pass


# ── Main Collection ────────────────────────────────────────────

def collect(test_mode=False):
    """Main collection routine. Returns (manifest_dict, normalized_dict, changes)."""
    global TEST_MODE
    if test_mode:
        TEST_MODE = True

    print(f"[{now_iso()}] Starting Ourbit collection{' (TEST MODE)' if TEST_MODE else ''}...")

    api_key = get_env("OURBIT_API_KEY")
    api_secret = get_env("OURBIT_API_SECRET")

    ensure_dirs()

    # Load state
    dedup_state = load_dedup_state()
    registry = load_symbol_registry()

    # Validate symbols (skip full validation in test mode, just check one)
    if TEST_MODE:
        valid_symbols = [TEST_SYMBOL]
        invalid_count = 0
        print(f"[INFO] TEST MODE: Using only {TEST_SYMBOL}")
    else:
        print("[INFO] Validating symbols against exchangeInfo...")
        registry = validate_symbols(registry)
        save_symbol_registry(registry)

        valid_symbols = [
            s for s, info in registry.get("symbols", {}).items()
            if info.get("status") == "valid"
        ]
        invalid_count = sum(
            1 for info in registry.get("symbols", {}).values()
            if info.get("status") == "invalid"
        )
        print(f"[INFO] Valid symbols: {len(valid_symbols)}, Invalid: {invalid_count}")

    manifests = {}
    all_changes = []

    # ── Spot Collection ──
    print("[INFO] Collecting Spot myTrades...")
    trades, m = collect_spot_mytrades(api_key, api_secret, valid_symbols)
    manifests["spot_mytrades"] = m
    norm_trades = normalize_spot_trades(trades, dedup_state)

    print("[INFO] Collecting Spot allOrders...")
    orders, m = collect_spot_allorders(api_key, api_secret, valid_symbols)
    manifests["spot_allorders"] = m
    norm_orders, order_changes = normalize_spot_orders(orders, dedup_state)
    all_changes.extend(order_changes)

    print("[INFO] Collecting Spot openOrders...")
    open_orders, m = collect_spot_openorders(api_key, api_secret, valid_symbols)
    manifests["spot_openorders"] = m
    norm_open = normalize_spot_open_orders(open_orders)

    # ── Futures Collection ──
    print("[INFO] Collecting Futures history_orders...")
    f_orders, m = collect_futures_history_orders(api_key, api_secret)
    manifests["futures_history_orders"] = m
    norm_f_orders, f_changes = normalize_futures_orders(f_orders, dedup_state)
    all_changes.extend(f_changes)

    print("[INFO] Collecting Futures order_deals...")
    f_deals, m = collect_futures_order_deals(api_key, api_secret)
    manifests["futures_order_deals"] = m
    norm_f_deals = normalize_futures_deals(f_deals, dedup_state)

    # ── Save normalized ──
    norm_date = today_str()
    norm_path = lambda n: os.path.join(NORM_DIR, norm_date, f"{n}.json")

    save_json(norm_path("spot_trades"), {
        "collected_at": now_iso(),
        "trades": norm_trades,
        "total_count": len(norm_trades),
    })
    save_json(norm_path("spot_orders"), {
        "collected_at": now_iso(),
        "orders": norm_orders,
        "status_changes": all_changes,
        "total_count": len(norm_orders),
    })
    save_json(norm_path("spot_open_orders"), {
        "collected_at": now_iso(),
        "orders": norm_open,
        "total_count": len(norm_open),
    })
    save_json(norm_path("futures_orders"), {
        "collected_at": now_iso(),
        "orders": norm_f_orders,
        "state_changes": f_changes,
        "total_count": len(norm_f_orders),
    })
    save_json(norm_path("futures_deals"), {
        "collected_at": now_iso(),
        "deals": norm_f_deals,
        "total_count": len(norm_f_deals),
    })

    # ── Save manifest ──
    save_json(norm_path("manifest"), {
        "collected_at": now_iso(),
        "date": norm_date,
        "endpoints": manifests,
        "valid_symbols": len(valid_symbols),
        "invalid_symbols": invalid_count,
        "total_normalized": {
            "spot_trades": len(norm_trades),
            "spot_orders": len(norm_orders),
            "spot_open_orders": len(norm_open),
            "futures_orders": len(norm_f_orders),
            "futures_deals": len(norm_f_deals),
        },
    })

    # ── Save dedup state ──
    dedup_state["last_updated"] = now_iso()
    # Trim status tracking maps to avoid unbounded growth
    for key in ["_spot_order_status", "_futures_order_state"]:
        if key in dedup_state and len(dedup_state[key]) > 5000:
            dedup_state[key] = dict(list(dedup_state[key].items())[-5000:])
    save_dedup_state(dedup_state)

    # ── Retention cleanup ──
    cleanup_retention()

    print(f"[{now_iso()}] Collection complete.")
    print(f"  Spot trades: {len(norm_trades)} new")
    print(f"  Spot orders: {len(norm_orders)} new ({len(all_changes)} status changes)")
    print(f"  Spot open: {len(norm_open)}")
    print(f"  Futures orders: {len(norm_f_orders)} ({len(f_changes)} state changes)")
    print(f"  Futures deals: {len(norm_f_deals)} new")

    return manifests, {
        "spot_trades": norm_trades,
        "spot_orders": norm_orders,
        "spot_open_orders": norm_open,
        "futures_orders": norm_f_orders,
        "futures_deals": norm_f_deals,
        "order_changes": all_changes,
        "futures_state_changes": f_changes,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ourbit portfolio data collector (read-only)")
    parser.add_argument("--test", action="store_true",
                        help="Limited test: GIGGLEUSDT only, max 5 records, 1 page")
    args = parser.parse_args()
    collect(test_mode=args.test)
