def check_overlap(start1, end1, start2, end2):
    """Check if two time intervals overlap.

    Args:
        start1 (datetime): Start datetime of the first interval.
        end1 (datetime): End datetime of the first interval.
        start2 (datetime): Start datetime of the second interval.
        end2 (datetime): End datetime of the second interval.

    Returns:
        bool: True if the intervals overlap, False otherwise.
    """
    return start1 < end2 and start2 < end1