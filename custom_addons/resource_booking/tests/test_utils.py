from datetime import datetime
from utils import check_overlap

def test_check_overlap_overlapping():
    start1 = datetime(2025, 1, 1, 10, 0)
    end1 = datetime(2025, 1, 1, 12, 0)
    start2 = datetime(2025, 1, 1, 11, 0)
    end2 = datetime(2025, 1, 1, 13, 0)
    assert check_overlap(start1, end1, start2, end2) is True

def test_check_overlap_non_overlapping():
    start1 = datetime(2025, 1, 1, 10, 0)
    end1 = datetime(2025, 1, 1, 12, 0)
    start2 = datetime(2025, 1, 1, 12, 0)
    end2 = datetime(2025, 1, 1, 14, 0)
    assert check_overlap(start1, end1, start2, end2) is False

def test_check_overlap_completely_inside():
    start1 = datetime(2025, 1, 1, 10, 0)
    end1 = datetime(2025, 1, 1, 14, 0)
    start2 = datetime(2025, 1, 1, 11, 0)
    end2 = datetime(2025, 1, 1, 12, 0)
    assert check_overlap(start1, end1, start2, end2) is True
