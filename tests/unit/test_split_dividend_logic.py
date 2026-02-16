"""
Phase 14 Tests: Split vs Dividend Logic Correctness

Verifies that the ROICalculator correctly handles:
1. Stock splits (year-over-year share multiplication)
2. Stock dividends (share addition without triggering split detection)  
3. Combined scenarios (split + dividend in same/consecutive years)

These tests use nominal (unadjusted) price data to match Phase 14's data model.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from app.project_tw.calculator import ROICalculator
from app.services.split_detector import SplitDetector, SplitEvent


# ---------- Helpers ----------

def make_yearly_df(yearly_data: list[dict]) -> pd.DataFrame:
    """
    Create a test DataFrame mimicking yearly price data.
    Each dict: {'year': int, 'open': float, 'high': float, 'low': float, 'close': float}
    Returns 1 row per year with dates on Jan 2.
    """
    rows = []
    for yd in yearly_data:
        rows.append({
            "date": pd.Timestamp(f"{yd['year']}-01-02"),
            "year": yd["year"],
            "open": yd["open"],
            "high": yd.get("high", yd["open"] * 1.05),
            "low": yd.get("low", yd["open"] * 0.95),
            "close": yd["close"],
            "volume": 1_000_000,
        })
    df = pd.DataFrame(rows)
    df.index = pd.DatetimeIndex(df["date"])
    return df


def make_detector_with_split(stock_id: str, split_year: int, ratio: float) -> SplitDetector:
    """Create a SplitDetector with a single known split pre-cached."""
    det = SplitDetector()
    det._cache[stock_id] = [
        SplitEvent(stock_id=stock_id, year=split_year, month=7, ratio=ratio, source="known")
    ]
    return det


# ---------- Test: No Split, No Dividend ----------

class TestNoSplitNoDividend:
    """Baseline: just buying shares, no corporate actions."""

    def test_basic_investment_value(self):
        """Principal 1M + 60K at $100/share for 2 years. Verify share count and value."""
        calc = ROICalculator()
        df = make_yearly_df([
            {"year": 2020, "open": 100, "close": 110},
            {"year": 2021, "open": 110, "close": 120},
        ])
        result = calc.calculate_complex_simulation(
            df, start_year=2020, principal=1_000_000, annual_investment=60_000,
            stock_code="", buy_logic="FIRST_CLOSE"
        )
        assert result.get("finalValue", 0) > 0
        # Year 1: buy at close=110, shares = 1060000/110 ≈ 9636.36
        # Year 2: buy at close=120, shares += 60000/120 = 500
        # Final value = (9636.36 + 500) * 120 = ~1,216,363
        assert result["finalValue"] > 1_200_000


# ---------- Test: Split Only ----------

class TestSplitOnly:
    """Verify that splits correctly multiply existing shares before new purchases."""

    @patch("app.project_tw.calculator._get_detector")
    def test_split_multiplies_pre_split_shares_only(self, mock_get_det):
        """
        Year 1: Buy at $100, price ends at $100. shares = 10600
        Year 2: 1:4 split. Price drops to $25. 
                 Existing shares *= 4 = 42400.
                 Buy 60000/$25 = 2400 new shares.
                 Total = 44800 shares at $25 = $1,120,000
        """
        det = make_detector_with_split("TEST", split_year=2021, ratio=4.0)
        mock_get_det.return_value = det

        calc = ROICalculator()
        df = make_yearly_df([
            {"year": 2020, "open": 100, "close": 100},
            {"year": 2021, "open": 25, "close": 25},  # post-split nominal price
        ])

        result = calc.calculate_complex_simulation(
            df, start_year=2020, principal=1_000_000, annual_investment=60_000,
            stock_code="TEST", buy_logic="FIRST_CLOSE"
        )

        # Year 1: (1M + 60K) / 100 = 10600 shares
        # Year 2: split 1:4 → 10600 * 4 = 42400, then buy 60000/25 = 2400
        # Total: 44800 shares * $25 = $1,120,000
        assert abs(result["finalValue"] - 1_120_000) < 100  # Allow tiny rounding


    @patch("app.project_tw.calculator._get_detector")
    def test_post_split_shares_not_double_counted(self, mock_get_det):
        """
        Critical regression test: ensure shares bought AFTER the split year
        are NOT multiplied by the split ratio.
        """
        det = make_detector_with_split("TEST", split_year=2021, ratio=4.0)
        mock_get_det.return_value = det

        calc = ROICalculator()
        df = make_yearly_df([
            {"year": 2020, "open": 100, "close": 100},
            {"year": 2021, "open": 25, "close": 25},
            {"year": 2022, "open": 30, "close": 30},  # post-split, no more splits
        ])

        result = calc.calculate_complex_simulation(
            df, start_year=2020, principal=1_000_000, annual_investment=60_000,
            stock_code="TEST", buy_logic="FIRST_CLOSE"
        )

        # Year 1: 10600 shares
        # Year 2: split → 42400, buy 2400 → 44800
        # Year 3: no split, buy 60000/30 = 2000 → 46800 shares * $30 = 1,404,000
        assert abs(result["finalValue"] - 1_404_000) < 100


# ---------- Test: Dividend Only ----------

class TestDividendOnly:
    """Verify stock and cash dividends add shares correctly without false split detection."""

    def test_stock_dividend_adds_shares(self):
        """Stock dividend of $1.0 (10% of par $10) should add 10% more shares."""
        calc = ROICalculator()
        df = make_yearly_df([
            {"year": 2020, "open": 50, "close": 50},
        ])

        dividend_data = {2020: {"cash": 0, "stock": 1.0}}

        result = calc.calculate_complex_simulation(
            df, start_year=2020, principal=1_000_000, annual_investment=60_000,
            dividend_data=dividend_data, stock_code="", buy_logic="FIRST_CLOSE"
        )

        # Buy: (1M + 60K) / 50 = 21200 shares
        # Stock div: 21200 * (1.0/10) = 2120 new shares → total 23320
        # Value: 23320 * 50 = 1,166,000
        assert abs(result["finalValue"] - 1_166_000) < 100

    def test_cash_dividend_reinvest(self):
        """Cash dividend of $3 per share should be reinvested at avg price."""
        calc = ROICalculator()
        df = make_yearly_df([
            {"year": 2020, "open": 50, "close": 50},
        ])

        dividend_data = {2020: {"cash": 3.0, "stock": 0}}

        result = calc.calculate_complex_simulation(
            df, start_year=2020, principal=1_000_000, annual_investment=60_000,
            dividend_data=dividend_data, stock_code="", buy_logic="FIRST_CLOSE"
        )

        # Buy: 21200 shares at $50
        # Cash div: 21200 * 3 = $63,600 → reinvest at avg $50 → 1272 shares
        # Total: 22472 * $50 = $1,123,600
        assert abs(result["finalValue"] - 1_123_600) < 100


# ---------- Test: Split + Dividend Combo ----------

class TestSplitAndDividend:
    """Scenarios where splits and dividends overlap."""

    @patch("app.project_tw.calculator._get_detector")
    def test_split_before_dividend_in_same_year(self, mock_get_det):
        """
        Year 1: Buy at $100, (1M+60K)/100 = 10600 shares.
        Year 2: Split 1:4 → 10600*4 = 42400.
                 Buy 60000/$25 = 2400 → 44800.
                 Stock div $2 (20%) on ALL 44800: +8960 → 53760.
                 Value: 53760 * $25 = $1,344,000
        """
        det = make_detector_with_split("TEST", split_year=2021, ratio=4.0)
        mock_get_det.return_value = det

        calc = ROICalculator()
        df = make_yearly_df([
            {"year": 2020, "open": 100, "close": 100},
            {"year": 2021, "open": 25, "close": 25},
        ])

        dividend_data = {2021: {"cash": 0, "stock": 2.0}}

        result = calc.calculate_complex_simulation(
            df, start_year=2020, principal=1_000_000, annual_investment=60_000,
            dividend_data=dividend_data, stock_code="TEST", buy_logic="FIRST_CLOSE"
        )

        assert abs(result["finalValue"] - 1_344_000) < 100


# ---------- Test: SplitDetector Threshold Safety ----------

class TestSplitDetectorThreshold:
    """Verify that stock dividends don't trigger false split detection."""

    def test_small_price_drop_not_flagged_as_split(self):
        """A 10% ex-dividend price drop should NOT be detected as a split."""
        det = SplitDetector()
        history = [
            {"close": 100, "open": 100, "high": 102, "low": 98, "year": 2020},
            {"close": 90, "open": 90, "high": 92, "low": 88, "year": 2021},  # -10%
        ]
        splits = det.detect_splits("SAFE", history)
        assert len(splits) == 0

    def test_genuine_split_detected(self):
        """A 75% price drop (1:4 split) SHOULD be detected."""
        det = SplitDetector()
        history = [
            {"close": 100, "open": 100, "high": 102, "low": 98, "year": 2020},
            {"close": 25, "open": 25, "high": 26, "low": 24, "year": 2021},   # -75%
            {"close": 26, "open": 25, "high": 27, "low": 24, "year": 2022},   # stays low
            {"close": 27, "open": 26, "high": 28, "low": 25, "year": 2023},   # stays low
            {"close": 28, "open": 27, "high": 29, "low": 26, "year": 2024},   # stays low
        ]
        splits = det.detect_splits("SPLIT", history)
        assert len(splits) == 1
        assert splits[0].ratio == 4.0
        assert splits[0].year == 2021


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
