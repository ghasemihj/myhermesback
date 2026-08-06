#!/usr/bin/env python3
"""
generate_report.py — Generate daily markdown report from normalized data.

Reads from: /data/.hermes/reports/crypto-portfolio-watch/normalized/{date}/
Writes to:  /data/.hermes/reports/crypto-portfolio-watch/daily/{date}.latest.md
            /data/.hermes/reports/crypto-portfolio-watch/latest.md

SECURITY: No API calls. No secrets read. Read-only on normalized data.
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

# ── Configuration ──────────────────────────────────────────────

DATA_ROOT = os.environ.get(
    "CRYPTO_WATCH_DATA_ROOT",
    "/data/.hermes/reports/crypto-portfolio-watch",
)
NORM_DIR = os.path.join(DATA_ROOT, "normalized")
DAILY_DIR = os.path.join(DATA_ROOT, "daily")
LATEST_PATH = os.path.join(DATA_ROOT, "latest.md")
STATE_DIR = os.path.join(DATA_ROOT, "state")

IRST = timezone(timedelta(hours=3, minutes=30))

# Jalali month names
JALALI_MONTHS = [
    "", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]


def gregorian_to_jalali(gy, gm, gd):
    """Convert Gregorian date to Jalali (Persian) date."""
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gm > 2:
        gy2 = gy + 1
    else:
        gy2 = gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + \
           ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd


def now_irst():
    return datetime.now(IRST)


def today_jalali():
    n = now_irst()
    jy, jm, jd = gregorian_to_jalali(n.year, n.month, n.day)
    return f"{jy}/{jm:02d}/{jd:02d}"


def today_gregorian():
    return now_irst().strftime("%Y-%m-%d")


def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


# ── Report Generation ──────────────────────────────────────────

def load_normalized_data(date_str):
    """Load all normalized files for a date."""
    norm_dir = os.path.join(NORM_DIR, date_str)
    if not os.path.isdir(norm_dir):
        return None
    data = {}
    for name in ["spot_trades", "spot_orders", "spot_open_orders",
                  "futures_orders", "futures_deals", "manifest"]:
        data[name] = load_json(os.path.join(norm_dir, f"{name}.json"))
    return data


def _record_summary_line(received, new_unique, endpoint_name, is_snapshot=False):
    """Generate the record count summary line for a data source."""
    lines = []
    if received is None:
        lines.append(f"- وضعیت: داده جمع‌آوری نشده")
        return "\n".join(lines)

    if is_snapshot:
        # openOrders: snapshot, no dedup concept
        lines.append(f"- تعداد سفارشات باز فعلی: **{new_unique}**")
        return "\n".join(lines)

    lines.append(f"- رکوردهای دریافتی از API: **{received}**")
    lines.append(f"- رکوردهای جدید (پس از حذف تکرار): **{new_unique}**")

    if received > 0 and new_unique == 0:
        lines.append(f"- داده با موفقیت دریافت شد، اما رکورد جدیدی نسبت به اجراهای قبلی وجود نداشت.")
    elif received == 0:
        lines.append(f"- در این بازه رکوردی از API دریافت نشد.")
    return "\n".join(lines)


def summarize_spot_trades(data, manifest_ep=None):
    """Summarize Spot trade activity."""
    received = manifest_ep.get("records_received") if manifest_ep else None
    if data is None and received is None:
        return "داده معاملات Spot جمع‌آوری نشده است."

    trades = data.get("trades", []) if data else []
    new_unique = len(trades)

    lines = []
    lines.append(_record_summary_line(received, new_unique, "myTrades"))

    if new_unique > 0:
        buys = sum(1 for t in trades if t.get("isBuyer") is True)
        sells = new_unique - buys
        symbols = sorted(set(t.get("symbol", "") for t in trades))
        lines.append(f"- خرید: **{buys}** | فروش: **{sells}**")
        if symbols:
            lines.append(f"- نمادها: {', '.join(symbols)}")

    return "\n".join(lines)


def summarize_spot_orders(data, manifest_ep=None):
    """Summarize Spot order history."""
    received = manifest_ep.get("records_received") if manifest_ep else None
    if data is None and received is None:
        return "داده سفارشات Spot جمع‌آوری نشده است."

    orders = data.get("orders", []) if data else []
    new_unique = len(orders)

    lines = []
    lines.append(_record_summary_line(received, new_unique, "allOrders"))

    if new_unique > 0:
        status_counts = {}
        for o in orders:
            s = o.get("status", "UNKNOWN")
            status_counts[s] = status_counts.get(s, 0) + 1
        for status, count in sorted(status_counts.items()):
            lines.append(f"  - {status}: {count}")

    changes = (data or {}).get("status_changes", [])
    if changes:
        lines.append(f"- تغییرات وضعیت: **{len(changes)}**")
        for c in changes[:5]:
            lines.append(f"  - {c.get('old','')} → {c.get('new','')}")
        if len(changes) > 5:
            lines.append(f"  - و {len(changes)-5} تغییر دیگر")

    return "\n".join(lines)


def summarize_spot_open(data, manifest_ep=None):
    """Summarize current open Spot orders (snapshot — no dedup)."""
    received = manifest_ep.get("records_received") if manifest_ep else None
    if data is None and received is None:
        return "داده سفارشات باز Spot جمع‌آوری نشده است."

    orders = data.get("orders", []) if data else []
    current = len(orders)

    lines = []
    lines.append(_record_summary_line(received, current, "openOrders", is_snapshot=True))

    if current > 0:
        symbols = sorted(set(o.get("symbol", "") for o in orders))
        lines.append(f"- نمادها: {', '.join(symbols)}")

    return "\n".join(lines)


def summarize_futures_orders(data, manifest_ep=None):
    """Summarize Futures order history."""
    received = manifest_ep.get("records_received") if manifest_ep else None
    if data is None and received is None:
        return "داده سفارشات Futures جمع‌آوری نشده است."

    orders = data.get("orders", []) if data else []
    new_unique = len(orders)

    lines = []
    lines.append(_record_summary_line(received, new_unique, "history_orders"))

    if new_unique > 0:
        state_names = {1: "Pending", 2: "Incomplete", 3: "Completed",
                       4: "Cancelled", 5: "Invalid"}
        state_counts = {}
        for o in orders:
            s = o.get("state", 0)
            state_counts[s] = state_counts.get(s, 0) + 1
        for state, count in sorted(state_counts.items()):
            name = state_names.get(state, f"Unknown({state})")
            lines.append(f"  - {name}: {count}")

    changes = (data or {}).get("state_changes", [])
    if changes:
        lines.append(f"- تغییرات وضعیت: **{len(changes)}**")

    return "\n".join(lines)


def summarize_futures_deals(data, manifest_ep=None):
    """Summarize Futures deal history and PnL."""
    received = manifest_ep.get("records_received") if manifest_ep else None
    if data is None and received is None:
        return "داده معاملات Futures جمع‌آوری نشده است."

    deals = data.get("deals", []) if data else []
    new_unique = len(deals)

    lines = []
    lines.append(_record_summary_line(received, new_unique, "order_deals"))

    if new_unique > 0:
        total_profit = 0.0
        total_fee = 0.0
        symbols = set()
        profit_valid = True
        for d in deals:
            raw_profit = d.get("profit")
            if raw_profit is not None and raw_profit != "" and raw_profit != 0:
                try:
                    total_profit += float(raw_profit)
                except (ValueError, TypeError):
                    profit_valid = False
            raw_fee = d.get("fee")
            if raw_fee is not None and raw_fee != "" and raw_fee != 0:
                try:
                    total_fee += float(raw_fee)
                except (ValueError, TypeError):
                    pass
            sym = d.get("symbol", "")
            if sym:
                symbols.add(sym)

        if symbols:
            lines.append(f"- نمادها: {', '.join(sorted(symbols))}")
        if profit_valid and total_profit != 0.0:
            lines.append(f"- سود/زیان ثبت‌شده: **{total_profit:+.4f}**")
        else:
            lines.append(f"- سود/زیان ثبت‌شده: داده کافی نیست")
        if total_fee != 0.0:
            lines.append(f"- کارمزد ثبت‌شده: {total_fee:.4f}")

    return "\n".join(lines)


def generate_report(date_str=None):
    """Generate the daily report. Returns the markdown string."""
    if not date_str:
        date_str = today_gregorian()

    data = load_normalized_data(date_str)
    if not data:
        return f"# ❌ گزارش موجود نیست\n\nداده نرمال‌شده برای {date_str} یافت نشد."

    manifest = data.get("manifest", {})
    endpoints = manifest.get("endpoints", {})
    collected_at = manifest.get("collected_at", None)

    # ── Compute data quality ──
    endpoint_order = [
        "spot_mytrades", "spot_allorders", "spot_openorders",
        "futures_history_orders", "futures_order_deals",
    ]
    success_count = 0
    fail_count = 0
    incomplete_count = 0
    for name in endpoint_order:
        m = endpoints.get(name, {})
        if not m:
            fail_count += 1
            continue
        if m.get("success") and m.get("complete"):
            success_count += 1
        elif m.get("success"):
            incomplete_count += 1
        else:
            fail_count += 1

    if fail_count == 0 and incomplete_count == 0:
        quality_status = "Complete"
    elif success_count > 0:
        quality_status = "Partial"
    else:
        quality_status = "Failed"

    # ── Collect timestamps ──
    first_collected = None
    last_collected = None
    for name in endpoint_order:
        m = endpoints.get(name, {})
        if m and m.get("collected_at"):
            ts = m["collected_at"]
            if first_collected is None or ts < first_collected:
                first_collected = ts
            if last_collected is None or ts > last_collected:
                last_collected = ts

    # Build report
    jalali = today_jalali()
    greg = today_gregorian()
    gen_time = now_irst().strftime("%H:%M IRST")

    lines = []
    lines.append(f"# 📊 گزارش روزانه سبد Ourbit")
    lines.append(f"")
    lines.append(f"**تاریخ:** {jalali} — {greg}")
    lines.append(f"**ساعت تولید:** {gen_time}")
    lines.append(f"")

    # ── Limitations notice ──
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## ⚠️ محدودیت‌های این گزارش")
    lines.append(f"")
    lines.append(f"- موجودی Spot مستقیماً قابل دریافت نیست (API `account` غیرفعال)")
    lines.append(f"- موجودی/پوزیشن باز Futures در endpointهای مستند موجود نیست")
    lines.append(f"- واریز، برداشت، انتقال و ایردراپ ممکن است دیده نشوند")
    lines.append(f"- داده‌ها از آخرین روزهای اخیر API هستند")
    lines.append(f"- ⚠️ **هیچ عددی به‌عنوان موجودی قطعی یا ارزش کل سبد گزارش نمی‌شود**")
    lines.append(f"")

    # ── Data Quality (always shown) ──
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 📋 وضعیت کیفیت داده")
    lines.append(f"")
    lines.append(f"- Overall status: **{quality_status}**")
    lines.append(f"- Successful endpoints: **{success_count}/5**")
    lines.append(f"- Failed endpoints: **{fail_count}/5**")
    lines.append(f"- Incomplete endpoints: **{incomplete_count}/5**")
    lines.append(f"")

    # ── Endpoint Status (always shown) ──
    lines.append(f"## 📡 وضعیت endpointها")
    lines.append(f"")
    endpoint_labels = {
        "spot_mytrades": "Spot — myTrades",
        "spot_allorders": "Spot — allOrders",
        "spot_openorders": "Spot — openOrders",
        "futures_history_orders": "Futures — history_orders",
        "futures_order_deals": "Futures — order_deals",
    }
    lines.append(f"| Endpoint | Success | HTTP | API Code | Records | Pages | Complete | Error |")
    lines.append(f"|---|---|---|---|---|---|---|---|")
    for name in endpoint_order:
        m = endpoints.get(name, {})
        label = endpoint_labels.get(name, name)
        if not m:
            lines.append(f"| {label} | — | — | — | — | — | — | not collected |")
        else:
            succ = "✅" if m.get("success") else "❌"
            http = m.get("http_status", "—")
            code = m.get("api_code", "—")
            if code is None:
                code = "0"
            recs = m.get("records_received", "—")
            pages = m.get("pages_received", "—")
            comp = "✅" if m.get("complete") else "❌"
            err = m.get("error_type", "—")
            if err is None:
                err = "—"
            lines.append(f"| {label} | {succ} | {http} | {code} | {recs} | {pages} | {comp} | {err} |")
    lines.append(f"")

    # ── Timestamps ──
    lines.append(f"## ⏰ زمان‌ها")
    lines.append(f"")
    lines.append(f"- Collection started at: **{first_collected if first_collected else 'Unknown'}**")
    lines.append(f"- Collection completed at: **{last_collected if last_collected else 'Unknown'}**")
    lines.append(f"- Report generated at: **{now_irst().isoformat()}**")
    lines.append(f"- Timezone: **Asia/Tehran (IRST, UTC+3:30)**")
    lines.append(f"")

    # ── Spot Section ──
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 🟢 Spot")
    lines.append(f"")

    lines.append(f"### فعالیت معاملاتی")
    lines.append(f"")
    lines.append(summarize_spot_trades(data.get("spot_trades"), endpoints.get("spot_mytrades")))
    lines.append(f"")

    lines.append(f"### تاریخچه سفارشات")
    lines.append(f"")
    lines.append(summarize_spot_orders(data.get("spot_orders"), endpoints.get("spot_allorders")))
    lines.append(f"")

    lines.append(f"### سفارشات باز فعلی")
    lines.append(f"")
    lines.append(summarize_spot_open(data.get("spot_open_orders"), endpoints.get("spot_openorders")))
    lines.append(f"")

    lines.append(f"> ⚠️ اعداد بالا بر اساس فعالیت ثبت‌شده هستند، نه موجودی واقعی حساب.")
    lines.append(f"")

    # ── Futures Section ──
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 🔵 Futures")
    lines.append(f"")

    lines.append(f"### تاریخچه سفارشات")
    lines.append(f"")
    lines.append(summarize_futures_orders(data.get("futures_orders"), endpoints.get("futures_history_orders")))
    lines.append(f"")

    lines.append(f"### تاریخچه معاملات و سود/زیان")
    lines.append(f"")
    lines.append(summarize_futures_deals(data.get("futures_deals"), endpoints.get("futures_order_deals")))
    lines.append(f"")

    lines.append(f"> ⚠️ پوزیشن باز و موجودی لحظه‌ای Futures قابل دریافت نیست.")
    lines.append(f"")

    # ── Summary ──
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 📈 خلاصه")
    lines.append(f"")

    # Build summary from manifest + normalized
    def _ep_val(ep_name, field, default=0):
        e = endpoints.get(ep_name, {})
        return e.get(field, default) if e else 0

    def _norm_count(data_key, list_key):
        d = data.get(data_key)
        if not d:
            return 0
        return len(d.get(list_key, []))

    lines.append(f"| بخش | دریافتی از API | جدید (پس از حذف تکرار) |")
    lines.append(f"|---|---|---|")
    lines.append(f"| معاملات Spot | {_ep_val('spot_mytrades','records_received')} | {_norm_count('spot_trades','trades')} |")
    lines.append(f"| سفارشات Spot | {_ep_val('spot_allorders','records_received')} | {_norm_count('spot_orders','orders')} |")
    lines.append(f"| سفارشات باز Spot | {_ep_val('spot_openorders','records_received')} | {_norm_count('spot_open_orders','orders')} |")
    lines.append(f"| سفارشات Futures | {_ep_val('futures_history_orders','records_received')} | {_norm_count('futures_orders','orders')} |")
    lines.append(f"| معاملات Futures | {_ep_val('futures_order_deals','records_received')} | {_norm_count('futures_deals','deals')} |")

    # Status changes
    order_changes = data.get("spot_orders", {}).get("status_changes", [])
    f_changes = data.get("futures_orders", {}).get("state_changes", [])
    if order_changes or f_changes:
        lines.append(f"")
        lines.append(f"### تغییرات وضعیت")
        if order_changes:
            lines.append(f"- Spot: {len(order_changes)} تغییر")
        if f_changes:
            lines.append(f"- Futures: {len(f_changes)} تغییر")

    lines.append(f"")
    lines.append(f"---")
    lines.append(f"*تولید شده توسط crypto-portfolio-watch — فقط خواندنی*")

    return "\n".join(lines)


def save_report(date_str=None):
    """Generate and save report. Returns saved paths."""
    if not date_str:
        date_str = today_gregorian()

    report = generate_report(date_str)

    # Save to daily/
    daily_path = os.path.join(DAILY_DIR, f"{date_str}.md")
    save_file(daily_path, report)

    # Update latest.md
    save_file(LATEST_PATH, report)

    return daily_path, LATEST_PATH


if __name__ == "__main__":
    date = sys.argv[1] if len(sys.argv) > 1 else None
    daily_path, latest_path = save_report(date)
    print(f"Report saved:")
    print(f"  Daily:  {daily_path}")
    print(f"  Latest: {latest_path}")
