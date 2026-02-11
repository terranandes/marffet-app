
import pytest
from app.services.split_detector import SplitDetector

class TestSplitDetector:
    
    def test_split_detection_2_to_1(self):
        detector = SplitDetector()
        records = [
            {'date': '2024-01-01', 'close': 100, 'open': 100},
            {'date': '2024-01-02', 'close': 52, 'open': 50} # ~50% drop
        ]
        detector.detect_splits("TEST", records)
        assert len(detector.splits.get("TEST", [])) == 1
        assert detector.splits["TEST"][0]['ratio'] == 2.0

    def test_reverse_split(self):
        # Todo: implementations
        pass
