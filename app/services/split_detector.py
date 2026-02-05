"""
Split Detector for Precision Engine

Detects stock splits from price history and provides adjustment factors.
Handles both auto-detected splits and known corporate actions.

Usage:
    from app.services.split_detector import SplitDetector
    
    detector = SplitDetector()
    splits = detector.detect_splits("0050", history)
    adjusted_shares = detector.adjust_shares("0050", shares, buy_year, current_year)
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SplitEvent:
    """Represents a stock split event."""
    stock_id: str
    year: int
    month: int  # 0 if unknown
    ratio: float  # e.g., 4.0 means 1:4 split (4 shares for every 1)
    source: str  # 'detected', 'known', 'manual'


# Known splits that may not be detectable from yearly data
# Format: stock_id -> list of SplitEvents
# NOTE: The "year" field indicates WHEN the split takes effect for share counting
#       (shares held at start of that year get multiplied)
# IMPORTANT: Only add splits that are NOT automatically detectable from price data
#            The detector will auto-detect splits from >40% overnight price drops
KNOWN_SPLITS = {
    "0050": [
        # 2014 split is auto-detected from daily data (2013-12-31 $58.70 -> 2014-01-02 $14.68)
        # 2025 split (if any) will be auto-detected when data reflects it
    ],
    "2330": [
        # TSMC had no splits in 2006-2026 period
    ],
}


class SplitDetector:
    """
    Detects and tracks stock splits for accurate ROI calculations.
    
    The engine uses unadjusted prices, so when calculating total value,
    we need to multiply share count by the cumulative split ratio.
    """
    
    # Threshold for detecting splits (40% overnight drop)
    SPLIT_THRESHOLD = -0.40
    
    def __init__(self):
        self._cache: Dict[str, List[SplitEvent]] = {}
    
    def detect_splits(self, stock_id: str, history: List[Dict]) -> List[SplitEvent]:
        """
        Detect splits from price history.
        Returns list of SplitEvent objects.
        """
        if stock_id in self._cache:
            return self._cache[stock_id]
        
        detected = []
        
        # Check for price drops between consecutive data points
        for i in range(1, len(history)):
            prev = history[i-1]
            curr = history[i]
            
            prev_close = prev.get('close', 0)
            curr_open = curr.get('open', 0)
            
            if prev_close > 0 and curr_open > 0:
                change = (curr_open - prev_close) / prev_close
                
                if change < self.SPLIT_THRESHOLD:
                    # Estimate split ratio
                    ratio = round(prev_close / curr_open)
                    if ratio >= 2:  # Must be at least 1:2
                        detected.append(SplitEvent(
                            stock_id=stock_id,
                            year=curr.get('year', 0),
                            month=0,  # Unknown from yearly data
                            ratio=float(ratio),
                            source='detected'
                        ))
        
        # Merge with known splits (prefer known over detected for same year)
        known = KNOWN_SPLITS.get(stock_id, [])
        merged = self._merge_splits(detected, known)
        
        self._cache[stock_id] = merged
        return merged
    
    def _merge_splits(self, detected: List[SplitEvent], known: List[SplitEvent]) -> List[SplitEvent]:
        """Merge detected and known splits, preferring known for same year."""
        result = {s.year: s for s in detected}
        for s in known:
            result[s.year] = s  # Known overrides detected
        return sorted(result.values(), key=lambda x: x.year)
    
    def get_cumulative_ratio(self, stock_id: str, from_year: int, to_year: int, 
                             history: List[Dict] = None) -> float:
        """
        Get cumulative split ratio between two years.
        
        Example: If there was a 1:4 split in 2013 and 1:2 in 2025,
        get_cumulative_ratio("0050", 2010, 2026) returns 8.0
        (original shares are now worth 8x in count)
        """
        if history:
            splits = self.detect_splits(stock_id, history)
        elif stock_id in self._cache:
            splits = self._cache[stock_id]
        elif stock_id in KNOWN_SPLITS:
            splits = KNOWN_SPLITS[stock_id]
        else:
            return 1.0
        
        ratio = 1.0
        for split in splits:
            if from_year < split.year <= to_year:
                ratio *= split.ratio
        
        return ratio
    
    def adjust_shares(self, stock_id: str, shares: float, buy_year: int, 
                      current_year: int, history: List[Dict] = None) -> float:
        """
        Adjust share count for splits that occurred between buy and current year.
        
        Example:
            shares = 1000, bought in 2010
            After 1:4 split in 2013 and 1:2 in 2025
            adjust_shares("0050", 1000, 2010, 2026) = 8000
        """
        ratio = self.get_cumulative_ratio(stock_id, buy_year, current_year, history)
        return shares * ratio
    
    def get_splits_for_stock(self, stock_id: str) -> List[SplitEvent]:
        """Get known/cached splits for a stock."""
        if stock_id in self._cache:
            return self._cache[stock_id]
        return KNOWN_SPLITS.get(stock_id, [])
    
    def add_known_split(self, stock_id: str, year: int, month: int, ratio: float):
        """Manually add a known split."""
        event = SplitEvent(stock_id, year, month, ratio, "manual")
        if stock_id not in KNOWN_SPLITS:
            KNOWN_SPLITS[stock_id] = []
        KNOWN_SPLITS[stock_id].append(event)
        
        # Invalidate cache
        if stock_id in self._cache:
            del self._cache[stock_id]


# Singleton instance
_detector: Optional[SplitDetector] = None

def get_split_detector() -> SplitDetector:
    """Get singleton SplitDetector instance."""
    global _detector
    if _detector is None:
        _detector = SplitDetector()
    return _detector
