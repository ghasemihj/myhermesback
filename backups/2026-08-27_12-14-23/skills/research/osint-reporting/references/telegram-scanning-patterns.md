# Telegram Channel Scanning Patterns

## Basic Scan

```bash
curl -sL "https://t.me/s/<channel>" -H "User-Agent: Mozilla/5.0" 2>/dev/null | \
  sed 's/<[^>]*>//g' | sed '/^[[:space:]]*$/d' | \
  grep -i '<keywords>' | head -N
```

## Multi-Keyword Scan (Arabic)

```bash
curl -sL "https://t.me/s/<channel>" -H "User-Agent: Mozilla/5.0" 2>/dev/null | \
  sed 's/<[^>]*>//g' | sed '/^[[:space:]]*$/d' | \
  grep -i 'عاجل\|هجوم\|حرب\|إيران\|أمريكا\|إسرائيل\|هرمز\|إمارات' | head -8
```

## Multi-Keyword Scan (Persian)

```bash
curl -sL "https://t.me/s/<channel>" -H "User-Agent: Mozilla/5.0" 2>/dev/null | \
  sed 's/<[^>]*>//g' | sed '/^[[:space:]]*$/d' | \
  grep -i 'حمله\|جنگ\|آمریکا\|ترامپ\|هرمز\|توافق\|سپاه\|موشک' | head -8
```

## Extract Latest Posts (with timestamps)

```bash
curl -sL "https://t.me/s/<channel>" -H "User-Agent: Mozilla/5.0" 2>/dev/null | \
  sed 's/<[^>]*>//g' | sed '/^[[:space:]]*$/d' | \
  grep -v '^$' | grep -v 'TWeb\|user-color\|css\|script' | tail -15
```

## Common Channels

| Channel | Language | Keywords |
|---------|----------|----------|
| @alonews | Persian | ترامپ, حمله, جنگ, ایران, آمریکا, هرمز |
| @EabriLive | Arabic/Hebrew | إيران,هجوم,حرب,هرمز,أمريكا |
| @RasadAlmedan | Arabic | عاجل,إيران,هجوم,غارة,هرمز |
| @alibk3 | Arabic | حادث,صناعي,جبل,علي,انفجار,سماء |
| @ourwarstoday | English | Iran, Kuwait, Bahrain, Hormuz, strike |

## Pitfalls

1. **Empty output**: Channel may be geo-restricted or rate-limited
2. **HTML entities**: `&amp;` = `&`, `&nbsp;` = space
3. **Duplicate content**: Same post appears multiple times — deduplicate
4. **Old posts**: Always check timestamps before reporting as "breaking"
