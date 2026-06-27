from __future__ import annotations

import argparse
import json
import math
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

JsonFetcher = Callable[[str, dict[str, str] | None], Any]
TextFetcher = Callable[[str, dict[str, str] | None], str]

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; market-dashboard/0.1; +https://github.com/ghostang/market-dashboard)",
    "Referer": "https://m.stock.naver.com/",
}

SEC_HEADERS = {
    "User-Agent": "market-dashboard contact@example.com",
}

NAVER_SERIES = [
    {
        "id": "KOSPI",
        "name": "KOSPI",
        "ticker": "KOSPI",
        "kind": "index",
        "currency": "KRW",
        "url": "https://api.stock.naver.com/chart/domestic/index/KOSPI/day?startDateTime={start}&endDateTime={end}",
        "source_name": "Naver Stock index chart API",
        "source_url": "https://m.stock.naver.com/domestic/index/KOSPI",
    },
    {
        "id": "005930",
        "name": "삼성전자",
        "ticker": "005930",
        "kind": "stock",
        "currency": "KRW",
        "url": "https://api.stock.naver.com/chart/domestic/item/005930/day?startDateTime={start}&endDateTime={end}",
        "source_name": "Naver Stock domestic chart API",
        "source_url": "https://m.stock.naver.com/domestic/stock/005930",
    },
    {
        "id": "000660",
        "name": "SK하이닉스",
        "ticker": "000660",
        "kind": "stock",
        "currency": "KRW",
        "url": "https://api.stock.naver.com/chart/domestic/item/000660/day?startDateTime={start}&endDateTime={end}",
        "source_name": "Naver Stock domestic chart API",
        "source_url": "https://m.stock.naver.com/domestic/stock/000660",
    },
    {
        "id": "009150",
        "name": "삼성전기",
        "ticker": "009150",
        "kind": "stock",
        "currency": "KRW",
        "url": "https://api.stock.naver.com/chart/domestic/item/009150/day?startDateTime={start}&endDateTime={end}",
        "source_name": "Naver Stock domestic chart API",
        "source_url": "https://m.stock.naver.com/domestic/stock/009150",
    },
]

YAHOO_SERIES = [
    {"id": "NVDA", "name": "NVIDIA", "ticker": "NVDA", "currency": "USD", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/NVDA"},
    {"id": "AMD", "name": "AMD", "ticker": "AMD", "currency": "USD", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/AMD"},
    {"id": "AVGO", "name": "Broadcom", "ticker": "AVGO", "currency": "USD", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/AVGO"},
    {"id": "MRVL", "name": "Marvell", "ticker": "MRVL", "currency": "USD", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/MRVL"},
    {"id": "QCOM", "name": "Qualcomm", "ticker": "QCOM", "currency": "USD", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/QCOM"},
    {"id": "ARM", "name": "Arm", "ticker": "ARM", "currency": "USD", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/ARM"},
    {"id": "2330.TW", "name": "TSMC", "ticker": "2330.TW", "currency": "TWD", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/2330.TW"},
    {"id": "TSM", "name": "TSMC ADR", "ticker": "TSM", "currency": "USD", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/TSM"},
    {"id": "INTC", "name": "Intel", "ticker": "INTC", "currency": "USD", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/INTC"},
    {"id": "MU", "name": "Micron", "ticker": "MU", "currency": "USD", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/MU"},
    {"id": "4062.T", "name": "Ibiden", "ticker": "4062.T", "currency": "JPY", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/4062.T"},
    {"id": "3037.TW", "name": "Unimicron", "ticker": "3037.TW", "currency": "TWD", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/3037.TW"},
    {"id": "4063.T", "name": "Shin-Etsu Chemical", "ticker": "4063.T", "currency": "JPY", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/4063.T"},
    {"id": "^SOX", "name": "SOX 지수", "ticker": "^SOX", "currency": "USD", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/%5ESOX"},
    {"id": "KRW=X", "name": "USD/KRW", "ticker": "KRW=X", "currency": "KRW", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/KRW=X"},
    {"id": "^TNX", "name": "미국 10년물", "ticker": "^TNX", "currency": "%", "source_name": "Yahoo Finance chart API", "source_url": "https://finance.yahoo.com/quote/%5ETNX"},
]

SEC_COMPANIES = [
    {"company": "NVIDIA", "cik": "0001045810", "source_url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json"},
    {"company": "AMD", "cik": "0000002488", "source_url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0000002488.json"},
    {"company": "Broadcom", "cik": "0001730168", "source_url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0001730168.json"},
    {"company": "Micron", "cik": "0000723125", "source_url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0000723125.json"},
    {"company": "Qualcomm", "cik": "0000804328", "source_url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0000804328.json"},
    {"company": "Marvell", "cik": "0001835632", "source_url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0001835632.json"},
    {"company": "Intel", "cik": "0000050863", "source_url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0000050863.json"},
]

VALUE_CHAIN_THEMES = [
    {
        "theme": "fabless",
        "label": "팹리스/설계",
        "description": "GPU, AI accelerator, ASIC, 네트워크 칩 설계",
        "representative_ids": ["NVDA", "AMD", "AVGO", "MRVL", "QCOM", "ARM"],
    },
    {
        "theme": "foundry",
        "label": "파운드리/생산",
        "description": "첨단 공정 제조와 패키징 capacity",
        "representative_ids": ["2330.TW", "TSM", "005930", "INTC"],
    },
    {
        "theme": "memory",
        "label": "메모리/HBM/DRAM/NAND",
        "description": "HBM, DRAM, NAND, enterprise SSD",
        "representative_ids": ["000660", "005930", "MU"],
    },
    {
        "theme": "substrate_materials",
        "label": "기판/소재·부품",
        "description": "FC-BGA, ABF substrate, MLCC, 패키징/공정 소재·부품",
        "representative_ids": ["009150", "4062.T", "3037.TW", "4063.T"],
    },
]

SHUKA_RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=UCsJ6RuBiTVWRX156FVbeaGg"

MANUAL_OR_PAID_SOURCES = [
    {
        "area": "메모리 가격",
        "refresh_status": "manual_required",
        "source_type": "paid_or_manual_real_source_required",
        "source_name": "TrendForce/DRAMeXchange 등 유료 또는 수동 입력",
        "note": "무료 공개 엔드포인트로 DRAM/NAND spot/contract 가격을 안정적으로 자동 수집하지 않는다. 운영 화면에서는 fake 가격을 넣지 않고 수동/유료 필요로 표시한다.",
    },
    {
        "area": "포트폴리오",
        "refresh_status": "manual_required",
        "source_type": "local_private_csv_required",
        "source_name": "사용자 로컬 CSV",
        "note": "GitHub Pages에 개인 보유내역 JSON을 배포하지 않는다. 브라우저 로컬 import 또는 비공개 배포 정책 확정 후 연결한다.",
    },
]


def fetch_json(url: str, headers: dict[str, str] | None = None) -> Any:
    merged = dict(DEFAULT_HEADERS)
    if headers:
        merged.update(headers)
    req = urllib.request.Request(url, headers=merged)
    with urllib.request.urlopen(req, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return json.loads(response.read().decode(charset, "replace"))


def fetch_text(url: str, headers: dict[str, str] | None = None) -> str:
    merged = dict(DEFAULT_HEADERS)
    if headers:
        merged.update(headers)
    req = urllib.request.Request(url, headers=merged)
    with urllib.request.urlopen(req, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, "replace")


def normalize_naver_series(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in payload:
        local_date = str(row["localDate"])
        rows.append({
            "date": f"{local_date[:4]}-{local_date[4:6]}-{local_date[6:8]}",
            "close": float(row["closePrice"]),
            "open": float(row.get("openPrice") or row["closePrice"]),
            "high": float(row.get("highPrice") or row["closePrice"]),
            "low": float(row.get("lowPrice") or row["closePrice"]),
            "volume": int(float(row.get("accumulatedTradingVolume") or 0)),
        })
    return rows


def normalize_yahoo_chart(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    chart = payload.get("chart", {})
    if chart.get("error"):
        raise ValueError(str(chart["error"]))
    result = (chart.get("result") or [])[0]
    timestamps = result.get("timestamp") or []
    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    meta = result.get("meta", {})
    rows: list[dict[str, Any]] = []
    for idx, ts in enumerate(timestamps):
        close = _safe_index(quote.get("close"), idx)
        if close is None or (isinstance(close, float) and math.isnan(close)):
            continue
        rows.append({
            "date": datetime.fromtimestamp(int(ts), tz=timezone.utc).date().isoformat(),
            "close": float(close),
            "open": _float_or_none(_safe_index(quote.get("open"), idx)),
            "high": _float_or_none(_safe_index(quote.get("high"), idx)),
            "low": _float_or_none(_safe_index(quote.get("low"), idx)),
            "volume": int(_safe_index(quote.get("volume"), idx) or 0),
        })
    return rows, meta


def extract_sec_company_metrics(payload: dict[str, Any], company: str, source_url: str) -> dict[str, Any]:
    facts = payload.get("facts", {}).get("us-gaap", {})
    metric_specs = {
        "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"],
        "gross_profit": ["GrossProfit"],
        "net_income": ["NetIncomeLoss"],
    }
    metrics: dict[str, Any] = {}
    for key, tags in metric_specs.items():
        fact = None
        tag_used = None
        for tag in tags:
            units = facts.get(tag, {}).get("units", {})
            usd_facts = units.get("USD") or []
            candidates = [row for row in usd_facts if row.get("form") in {"10-Q", "10-K"} and row.get("val") is not None and row.get("end")]
            if candidates:
                fact = sorted(candidates, key=lambda row: (str(row.get("end")), str(row.get("filed", ""))))[-1]
                tag_used = tag
                break
        if fact:
            metrics[key] = {
                "value": fact.get("val"),
                "unit": "USD",
                "period": f"{fact.get('fy')} {fact.get('fp')}",
                "end": fact.get("end"),
                "form": fact.get("form"),
                "tag": tag_used,
            }
    return {
        "company": company,
        "source_name": "SEC EDGAR companyfacts API",
        "source_url": source_url,
        "source_type": "official_public_api",
        "refresh_status": "ok" if metrics else "unavailable",
        "metrics": metrics,
        "quality_note": "SEC XBRL companyfacts에서 최신 10-Q/10-K USD fact를 선택함. 기업 발표 segment/AI revenue 코멘트와는 다를 수 있음.",
    }


def parse_youtube_rss_items(xml_text: str, fetched_at: str, limit: int = 8) -> list[dict[str, Any]]:
    root = ET.fromstring(xml_text)
    ns = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
    items: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", ns)[:limit]:
        title = _xml_text(entry, "atom:title", ns) or "제목 없음"
        video_id = _xml_text(entry, "yt:videoId", ns)
        published = _xml_text(entry, "atom:published", ns)
        link_el = entry.find("atom:link[@rel='alternate']", ns) or entry.find("atom:link", ns)
        url = link_el.attrib.get("href") if link_el is not None else (f"https://www.youtube.com/watch?v={video_id}" if video_id else SHUKA_RSS_URL)
        items.append({
            "source_key": "shuka_world",
            "source_name": "슈카월드 YouTube RSS",
            "item_id": video_id or url,
            "title": title,
            "published_at": published,
            "url": url,
            "tags": _keyword_tags(title),
            "summary_short": "YouTube RSS 제목 기반 favorite source 항목. 원문 확인 필요.",
            "related_companies": _related_companies(title),
            "related_themes": _related_themes(title),
            "source_type": "commentary_no_key_rss",
            "fetched_at": fetched_at,
            "refresh_status": "ok",
            "quality_note": "YouTube RSS에서 가져온 해설/동영상 소스이며 공식 수치 원천이 아님.",
        })
    return items


def _xml_text(entry: ET.Element, path: str, ns: dict[str, str]) -> str | None:
    el = entry.find(path, ns)
    return el.text.strip() if el is not None and el.text else None


def _keyword_tags(title: str) -> list[str]:
    mapping = {
        "AI": ["AI", "인공지능"],
        "HBM": ["HBM"],
        "반도체": ["반도체", "semiconductor"],
        "GPU": ["GPU"],
        "메모리": ["메모리", "DRAM", "NAND"],
        "파운드리": ["파운드리", "foundry", "TSMC"],
        "수출": ["수출"],
        "금리": ["금리", "Treasury"],
    }
    lower = title.lower()
    tags = [tag for tag, needles in mapping.items() if any(needle.lower() in lower for needle in needles)]
    return tags or ["favorite"]


def _related_companies(title: str) -> list[str]:
    mapping = {
        "NVIDIA": ["nvidia", "엔비디아"],
        "TSMC": ["tsmc"],
        "SK hynix": ["하이닉스", "hynix"],
        "Samsung": ["삼성", "samsung"],
        "Micron": ["마이크론", "micron"],
        "Broadcom": ["브로드컴", "broadcom"],
    }
    lower = title.lower()
    return [name for name, needles in mapping.items() if any(needle.lower() in lower for needle in needles)]


def _related_themes(title: str) -> list[str]:
    tags = set(_keyword_tags(title))
    themes = []
    if tags & {"AI", "GPU"}:
        themes.append("fabless")
    if tags & {"파운드리"}:
        themes.append("foundry")
    if tags & {"HBM", "메모리"}:
        themes.append("memory")
    if "반도체" in tags and not themes:
        themes.append("semiconductor_general")
    return themes


def _safe_index(values: Any, idx: int) -> Any:
    if not isinstance(values, list) or idx >= len(values):
        return None
    return values[idx]


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _card_from_rows(config: dict[str, Any], rows: list[dict[str, Any]], source_type: str, fetched_at: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    if len(rows) < 1:
        raise ValueError("no price rows returned")
    latest = rows[-1]
    prev = rows[-2] if len(rows) >= 2 else rows[-1]
    close = latest["close"]
    prev_close = prev["close"]
    change = close - prev_close
    pct = (change / prev_close * 100.0) if prev_close else None
    first = rows[-22]["close"] if len(rows) >= 22 else rows[0]["close"]
    period_pct = (close / first - 1.0) * 100.0 if first else None
    currency = (meta or {}).get("currency") or config.get("currency")
    return {
        "id": config["id"],
        "name": config["name"],
        "ticker": config["ticker"],
        "currency": currency,
        "latest_date": latest["date"],
        "value": round(close, 4),
        "change": round(change, 4),
        "change_pct": round(pct, 4) if pct is not None else None,
        "period_change_pct": round(period_pct, 4) if period_pct is not None else None,
        "series": rows[-80:],
        "source_name": config["source_name"],
        "source_url": config["source_url"],
        "source_type": source_type,
        "fetched_at": fetched_at,
        "refresh_status": "ok",
        "quality_note": "실제 외부 소스 응답에서 생성. 투자 판단용 공식 보증 데이터는 아니므로 출처 확인 필요.",
    }


def _failed_card(config: dict[str, Any], error: Exception, fetched_at: str, source_type: str) -> dict[str, Any]:
    return {
        "id": config["id"],
        "name": config["name"],
        "ticker": config["ticker"],
        "currency": config.get("currency"),
        "latest_date": None,
        "value": None,
        "change": None,
        "change_pct": None,
        "period_change_pct": None,
        "series": [],
        "source_name": config["source_name"],
        "source_url": config["source_url"],
        "source_type": source_type,
        "fetched_at": fetched_at,
        "refresh_status": "failed",
        "quality_note": f"수집 실패: {type(error).__name__}: {str(error)[:180]}",
    }


def _date_window(now: datetime) -> tuple[str, str]:
    end = now.date()
    start = end.replace(year=end.year - 1)
    return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")


def build_value_chain(cards: list[dict[str, Any]], fetched_at: str) -> dict[str, Any]:
    by_id = {card["id"]: card for card in cards}
    themes = []
    for theme in VALUE_CHAIN_THEMES:
        representatives = []
        ok_periods = []
        for ticker_id in theme["representative_ids"]:
            card = by_id.get(ticker_id)
            if not card:
                continue
            if card.get("refresh_status") == "ok" and card.get("period_change_pct") is not None:
                ok_periods.append(float(card["period_change_pct"]))
            representatives.append({
                "id": card["id"],
                "company": card["name"],
                "ticker": card["ticker"],
                "value": card["value"],
                "return_1d": card["change_pct"],
                "return_1m": card["period_change_pct"],
                "latest_date": card["latest_date"],
                "source_name": card["source_name"],
                "source_url": card["source_url"],
                "source_type": card["source_type"],
                "refresh_status": card["refresh_status"],
            })
        avg = sum(ok_periods) / len(ok_periods) if ok_periods else None
        themes.append({
            "theme": theme["theme"],
            "label": theme["label"],
            "description": theme["description"],
            "basket_return_1m": round(avg, 4) if avg is not None else None,
            "representatives": representatives,
            "source_type": "no_key_auto_provider" if ok_periods else "unavailable",
            "refresh_status": "ok" if ok_periods else "unavailable",
            "fetched_at": fetched_at,
            "quality_note": "Naver/Yahoo no-key provider 가격 series에서 대표 ticker 바스켓 수익률을 계산. 점유율/유료 가격은 만들지 않음.",
        })
    return {"themes": themes, "quality_note": "AI 칩 밸류체인 No-key MVP. 실제 가격 source 기반이며 unavailable 항목은 fake 값으로 채우지 않음."}


def build_favorite_sources(fetch_text_func: TextFetcher | None, fetched_at: str) -> dict[str, Any]:
    sources = [
        {
            "source_key": "bok",
            "source_name": "한국은행 리포트",
            "source_type": "official_no_key_html_or_manual_real",
            "source_url": "https://www.bok.or.kr/portal/main/main.do",
            "refresh_status": "manual_required",
            "fetched_at": fetched_at,
            "quality_note": "BOK 공개 HTML 접근은 가능하나 세부 리포트 게시판 endpoint 확정 전에는 수동/링크 기반으로 표시.",
        },
        {
            "source_key": "shuka_world",
            "source_name": "슈카월드 YouTube RSS",
            "source_type": "commentary_no_key_rss",
            "source_url": SHUKA_RSS_URL,
            "refresh_status": "manual_required" if fetch_text_func is None else "pending",
            "fetched_at": fetched_at,
            "quality_note": "해설/동영상 commentary source. 공식 수치 원천으로 사용하지 않음.",
        },
        {
            "source_key": "toss_securities",
            "source_name": "토스증권 리포트",
            "source_type": "manual_real_bookmark_source",
            "source_url": "https://www.tossinvest.com/",
            "refresh_status": "manual_required",
            "fetched_at": fetched_at,
            "quality_note": "리포트 전용 공개 endpoint 미확정. 자동 수집을 주장하지 않고 manual_real/bookmark로 시작.",
        },
    ]
    items: list[dict[str, Any]] = []
    if fetch_text_func is not None:
        try:
            rss_text = fetch_text_func(SHUKA_RSS_URL, {"User-Agent": DEFAULT_HEADERS["User-Agent"]})
            shuka_items = parse_youtube_rss_items(rss_text, fetched_at=fetched_at)
            items.extend(shuka_items)
            sources[1]["refresh_status"] = "ok" if shuka_items else "unavailable"
            sources[1]["quality_note"] = "YouTube RSS에서 최신 항목을 자동 수집. commentary source로만 표시."
        except Exception as exc:
            sources[1]["refresh_status"] = "failed"
            sources[1]["quality_note"] = f"YouTube RSS 수집 실패: {type(exc).__name__}: {str(exc)[:180]}"
    return {"sources": sources, "items": items}


def build_dashboard(fetch_json: JsonFetcher = fetch_json, fetch_text: TextFetcher | None = None, now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    fetched_at = now.isoformat()
    start, end = _date_window(now)
    cards: list[dict[str, Any]] = []

    for config in NAVER_SERIES:
        try:
            url = config["url"].format(start=start, end=end)
            payload = fetch_json(url, DEFAULT_HEADERS)
            rows = normalize_naver_series(payload)
            cards.append(_card_from_rows(config, rows, "real_market_provider", fetched_at))
        except Exception as exc:
            cards.append(_failed_card(config, exc, fetched_at, "real_market_provider"))

    for config in YAHOO_SERIES:
        try:
            symbol = urllib.parse.quote(config["id"], safe="")
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1y&interval=1d"
            payload = fetch_json(url, {"User-Agent": DEFAULT_HEADERS["User-Agent"]})
            rows, meta = normalize_yahoo_chart(payload)
            cards.append(_card_from_rows(config, rows, "real_market_provider", fetched_at, meta))
        except Exception as exc:
            cards.append(_failed_card(config, exc, fetched_at, "real_market_provider"))

    ok_cards = [c for c in cards if c["refresh_status"] == "ok"]
    value_chain = build_value_chain(cards, fetched_at)
    favorite_sources = build_favorite_sources(fetch_text, fetched_at)
    company_metrics: list[dict[str, Any]] = []
    for config in SEC_COMPANIES:
        try:
            payload = fetch_json(config["source_url"], SEC_HEADERS)
            metric = extract_sec_company_metrics(payload, company=config["company"], source_url=config["source_url"])
            metric["fetched_at"] = fetched_at
            company_metrics.append(metric)
        except Exception as exc:
            company_metrics.append({
                "company": config["company"],
                "source_name": "SEC EDGAR companyfacts API",
                "source_url": config["source_url"],
                "source_type": "official_public_api",
                "refresh_status": "failed",
                "metrics": {},
                "fetched_at": fetched_at,
                "quality_note": f"수집 실패: {type(exc).__name__}: {str(exc)[:180]}",
            })

    source_status = [
        {
            "area": card["name"],
            "refresh_status": card["refresh_status"],
            "source_type": card["source_type"],
            "source_name": card["source_name"],
            "source_url": card["source_url"],
            "as_of_date": card["latest_date"],
            "fetched_at": card["fetched_at"],
            "quality_note": card["quality_note"],
        }
        for card in cards
    ] + [
        {
            "area": metric["company"] + " SEC facts",
            "refresh_status": metric["refresh_status"],
            "source_type": metric["source_type"],
            "source_name": metric["source_name"],
            "source_url": metric["source_url"],
            "as_of_date": max((m.get("end") or "" for m in metric.get("metrics", {}).values()), default=None),
            "fetched_at": metric.get("fetched_at"),
            "quality_note": metric["quality_note"],
        }
        for metric in company_metrics
    ] + [
        {
            "area": "AI 칩 체인 " + theme["label"],
            "refresh_status": theme["refresh_status"],
            "source_type": theme["source_type"],
            "source_name": "Naver/Yahoo no-key provider basket",
            "source_url": "public/data/dashboard.json#value_chain",
            "as_of_date": None,
            "fetched_at": theme["fetched_at"],
            "quality_note": theme["quality_note"],
        }
        for theme in value_chain["themes"]
    ] + [
        {
            "area": "Favorite 소스 " + source["source_name"],
            "refresh_status": source["refresh_status"],
            "source_type": source["source_type"],
            "source_name": source["source_name"],
            "source_url": source["source_url"],
            "as_of_date": None,
            "fetched_at": source["fetched_at"],
            "quality_note": source["quality_note"],
        }
        for source in favorite_sources["sources"]
    ] + MANUAL_OR_PAID_SOURCES

    return {
        "schema_version": 2,
        "mock_data": False,
        "generated_at": fetched_at,
        "dashboard_title": "AI 반도체 투자 대시보드",
        "market_cards": cards,
        "company_metrics": company_metrics,
        "value_chain": value_chain,
        "favorite_sources": favorite_sources,
        "source_status": source_status,
        "market_comparison": _market_comparison(ok_cards),
        "signals": _signals(cards),
        "portfolio": {
            "refresh_status": "manual_required",
            "source_type": "local_private_csv_required",
            "message": "포트폴리오 CSV가 아직 연결되지 않았습니다. GitHub Pages 공개 배포에는 개인 보유내역을 포함하지 않습니다.",
        },
    }


def _market_comparison(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    wanted = {"KOSPI", "^SOX", "005930", "000660", "MU", "AVGO", "2330.TW", "NVDA", "AMD", "009150"}
    return [
        {"id": c["id"], "name": c["name"], "period_change_pct": c["period_change_pct"], "series": c["series"], "currency": c["currency"]}
        for c in cards if c["id"] in wanted and c.get("series")
    ]


def _signals(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {c["id"]: c for c in cards}
    signals = []
    for signal_id, label, card_id in [
        ("fabless_ai", "팹리스/AI 칩 모멘텀", "NVDA"),
        ("foundry", "파운드리 모멘텀", "2330.TW"),
        ("korea_memory_price", "한국 메모리 주가 모멘텀", "000660"),
        ("substrate_materials", "기판/소재 모멘텀", "009150"),
        ("usdkrw", "환율(USD/KRW)", "KRW=X"),
    ]:
        card = by_id.get(card_id)
        if not card or card["refresh_status"] != "ok" or card.get("period_change_pct") is None:
            status = "unavailable"
            reason = "실제 소스 수집 실패 또는 데이터 부족"
        elif card["period_change_pct"] > 5:
            status = "green"
            reason = f"최근 1개월 거래일 기준 +{card['period_change_pct']:.1f}%"
        elif card["period_change_pct"] < -5:
            status = "red"
            reason = f"최근 1개월 거래일 기준 {card['period_change_pct']:.1f}%"
        else:
            status = "yellow"
            reason = f"최근 1개월 거래일 기준 {card['period_change_pct']:.1f}%"
        signals.append({"id": signal_id, "label": label, "status": status, "reason": reason, "source_dependency": card_id})
    signals.append({
        "id": "memory_price",
        "label": "DRAM/NAND/HBM 가격",
        "status": "unavailable",
        "reason": "유료/수동 실제 소스가 필요하므로 임의 가격을 넣지 않음",
        "source_dependency": "paid_or_manual_memory_price",
    })
    return signals


def write_dashboard(path: Path, dashboard: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch real-source semiconductor dashboard data for static GitHub Pages.")
    parser.add_argument("--out", default="public/data/dashboard.json", help="Output dashboard JSON path")
    args = parser.parse_args()
    dashboard = build_dashboard(fetch_text=fetch_text)
    write_dashboard(Path(args.out), dashboard)
    ok = sum(1 for c in dashboard["market_cards"] if c["refresh_status"] == "ok")
    failed = sum(1 for c in dashboard["market_cards"] if c["refresh_status"] == "failed")
    theme_ok = sum(1 for theme in dashboard["value_chain"]["themes"] if theme["refresh_status"] == "ok")
    fav_ok = sum(1 for source in dashboard["favorite_sources"]["sources"] if source["refresh_status"] == "ok")
    print(f"wrote {args.out} with mock_data={dashboard['mock_data']} ok_cards={ok} failed_cards={failed} theme_ok={theme_ok} favorite_ok={fav_ok}")
    return 0 if ok >= 8 and theme_ok == 4 else 2


if __name__ == "__main__":
    raise SystemExit(main())
