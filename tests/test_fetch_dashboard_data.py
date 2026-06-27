import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fetch_dashboard_data import (
    build_dashboard,
    extract_sec_company_metrics,
    normalize_naver_series,
    normalize_yahoo_chart,
    parse_youtube_rss_items,
)


class FetchDashboardDataTests(unittest.TestCase):
    def test_normalize_naver_series_uses_real_source_payload_shape(self):
        payload = [
            {"localDate": "20250602", "closePrice": 56800.0, "openPrice": 56300.0, "highPrice": 57300.0, "lowPrice": 56200.0, "accumulatedTradingVolume": 12870515},
            {"localDate": "20250603", "closePrice": 57200.0, "openPrice": 56800.0, "highPrice": 57500.0, "lowPrice": 56600.0, "accumulatedTradingVolume": 11111111},
        ]

        rows = normalize_naver_series(payload)

        self.assertEqual(rows, [
            {"date": "2025-06-02", "close": 56800.0, "open": 56300.0, "high": 57300.0, "low": 56200.0, "volume": 12870515},
            {"date": "2025-06-03", "close": 57200.0, "open": 56800.0, "high": 57500.0, "low": 56600.0, "volume": 11111111},
        ])

    def test_normalize_yahoo_chart_uses_real_chart_payload_shape(self):
        payload = {
            "chart": {
                "result": [
                    {
                        "meta": {"currency": "USD", "regularMarketTime": 1716422400},
                        "timestamp": [1716336000, 1716422400],
                        "indicators": {
                            "quote": [
                                {
                                    "open": [10.0, 11.0],
                                    "high": [12.0, 13.0],
                                    "low": [9.5, 10.5],
                                    "close": [11.0, 12.0],
                                    "volume": [100, 200],
                                }
                            ]
                        },
                    }
                ],
                "error": None,
            }
        }

        rows, meta = normalize_yahoo_chart(payload)

        self.assertEqual(meta["currency"], "USD")
        self.assertEqual(rows[-1]["close"], 12.0)
        self.assertEqual(rows[-1]["volume"], 200)
        self.assertEqual(rows[-1]["date"], "2024-05-23")

    def test_build_dashboard_never_uses_mock_when_sources_fail(self):
        def fake_json(url, headers=None):
            if "stock.naver.com" in url:
                return [
                    {"localDate": "20250602", "closePrice": 100.0, "openPrice": 99.0, "highPrice": 101.0, "lowPrice": 98.0, "accumulatedTradingVolume": 1000},
                    {"localDate": "20250603", "closePrice": 103.0, "openPrice": 100.0, "highPrice": 104.0, "lowPrice": 99.0, "accumulatedTradingVolume": 1200},
                ]
            raise RuntimeError("provider unavailable")

        dashboard = build_dashboard(fetch_json=fake_json, now=datetime(2026, 6, 26, 0, 0, tzinfo=timezone.utc))

        self.assertFalse(dashboard["mock_data"])
        self.assertTrue(dashboard["generated_at"].startswith("2026-06-26T00:00:00"))
        self.assertTrue(any(card["ticker"] == "005930" and card["refresh_status"] == "ok" for card in dashboard["market_cards"]))
        failed = [card for card in dashboard["market_cards"] if card["refresh_status"] == "failed"]
        self.assertTrue(failed, "provider failures should be surfaced as failed cards, not replaced with fake values")
        self.assertTrue(all(card.get("source_type") != "mock" for card in dashboard["market_cards"]))

    def test_dashboard_json_is_static_pages_friendly(self):
        def fake_json(url, headers=None):
            return [
                {"localDate": "20250602", "closePrice": 100.0, "openPrice": 99.0, "highPrice": 101.0, "lowPrice": 98.0, "accumulatedTradingVolume": 1000},
                {"localDate": "20250603", "closePrice": 103.0, "openPrice": 100.0, "highPrice": 104.0, "lowPrice": 99.0, "accumulatedTradingVolume": 1200},
            ]

        dashboard = build_dashboard(fetch_json=fake_json, now=datetime(2026, 6, 26, 0, 0, tzinfo=timezone.utc))
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dashboard.json"
            out.write_text(json.dumps(dashboard, ensure_ascii=False), encoding="utf-8")
            loaded = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(loaded["schema_version"], 2)
        self.assertIn("market_cards", loaded)
        self.assertIn("source_status", loaded)

    def test_extract_sec_company_metrics_prefers_latest_10q_or_10k_real_fact(self):
        payload = {
            "facts": {
                "us-gaap": {
                    "RevenueFromContractWithCustomerExcludingAssessedTax": {
                        "units": {
                            "USD": [
                                {"fy": 2025, "fp": "FY", "form": "10-K", "end": "2025-10-31", "val": 1000},
                                {"fy": 2026, "fp": "Q1", "form": "10-Q", "end": "2026-01-31", "val": 350},
                            ]
                        }
                    },
                    "GrossProfit": {
                        "units": {
                            "USD": [
                                {"fy": 2026, "fp": "Q1", "form": "10-Q", "end": "2026-01-31", "val": 120}
                            ]
                        }
                    },
                }
            }
        }

        metrics = extract_sec_company_metrics(payload, company="Micron", source_url="https://data.sec.gov/api/xbrl/companyfacts/CIK0000723125.json")

        self.assertEqual(metrics["company"], "Micron")
        self.assertEqual(metrics["refresh_status"], "ok")
        self.assertEqual(metrics["source_type"], "official_public_api")
        self.assertEqual(metrics["metrics"]["revenue"]["value"], 350)
        self.assertEqual(metrics["metrics"]["gross_profit"]["value"], 120)
        self.assertEqual(metrics["metrics"]["revenue"]["period"], "2026 Q1")

    def test_parse_youtube_rss_items_keeps_real_links_and_tags(self):
        rss = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">
          <entry>
            <yt:videoId>abc123</yt:videoId>
            <title>AI 반도체와 HBM 사이클 점검</title>
            <link rel="alternate" href="https://www.youtube.com/watch?v=abc123"/>
            <published>2026-06-25T10:00:00+00:00</published>
          </entry>
        </feed>
        """

        items = parse_youtube_rss_items(rss, fetched_at="2026-06-26T00:00:00+00:00")

        self.assertEqual(items[0]["source_key"], "shuka_world")
        self.assertEqual(items[0]["source_type"], "commentary_no_key_rss")
        self.assertEqual(items[0]["url"], "https://www.youtube.com/watch?v=abc123")
        self.assertIn("AI", items[0]["tags"])
        self.assertIn("HBM", items[0]["tags"])
        self.assertEqual(items[0]["refresh_status"], "ok")

    def test_dashboard_includes_no_key_ai_chip_chain_and_favorite_sources(self):
        def fake_json(url, headers=None):
            if "stock.naver.com" in url:
                return [
                    {"localDate": "20250602", "closePrice": 100.0, "openPrice": 99.0, "highPrice": 101.0, "lowPrice": 98.0, "accumulatedTradingVolume": 1000},
                    {"localDate": "20250603", "closePrice": 112.0, "openPrice": 100.0, "highPrice": 113.0, "lowPrice": 99.0, "accumulatedTradingVolume": 1200},
                ]
            if "finance.yahoo.com" in url:
                return {
                    "chart": {
                        "result": [{
                            "meta": {"currency": "USD"},
                            "timestamp": [1716336000, 1716422400],
                            "indicators": {"quote": [{"open": [10.0, 11.0], "high": [12.0, 13.0], "low": [9.0, 10.0], "close": [10.0, 12.0], "volume": [100, 200]}]},
                        }],
                        "error": None,
                    }
                }
            if "data.sec.gov" in url:
                return {"facts": {"us-gaap": {"RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": [{"fy": 2026, "fp": "Q1", "form": "10-Q", "end": "2026-03-31", "val": 1000}]}}}}}
            raise RuntimeError(f"unexpected json URL {url}")

        def fake_text(url, headers=None):
            if "youtube.com/feeds/videos.xml" in url:
                return """<?xml version="1.0" encoding="UTF-8"?>
                <feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">
                  <entry><yt:videoId>abc123</yt:videoId><title>HBM과 AI 칩 공급망</title><link rel="alternate" href="https://www.youtube.com/watch?v=abc123"/><published>2026-06-25T10:00:00+00:00</published></entry>
                </feed>
                """
            raise RuntimeError(f"unexpected text URL {url}")

        dashboard = build_dashboard(fetch_json=fake_json, fetch_text=fake_text, now=datetime(2026, 6, 26, 0, 0, tzinfo=timezone.utc))

        self.assertFalse(dashboard["mock_data"])
        themes = {theme["theme"]: theme for theme in dashboard["value_chain"]["themes"]}
        self.assertEqual(set(themes), {"fabless", "foundry", "memory", "substrate_materials"})
        self.assertTrue(all(len(theme["representatives"]) >= 2 for theme in themes.values()))
        self.assertTrue(all(theme["source_type"] == "no_key_auto_provider" for theme in themes.values()))
        favorite_sources = {src["source_key"]: src for src in dashboard["favorite_sources"]["sources"]}
        self.assertEqual(set(favorite_sources), {"bok", "shuka_world", "toss_securities"})
        self.assertEqual(favorite_sources["shuka_world"]["refresh_status"], "ok")
        self.assertEqual(favorite_sources["bok"]["refresh_status"], "manual_required")
        self.assertEqual(favorite_sources["toss_securities"]["refresh_status"], "manual_required")
        self.assertTrue(all(item["source_type"] != "mock" for item in dashboard["favorite_sources"]["items"]))


if __name__ == "__main__":
    unittest.main()
