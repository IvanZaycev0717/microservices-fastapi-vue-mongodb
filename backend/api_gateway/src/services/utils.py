def convert_minutes_to_seconds(minutes: int) -> int:
    """Convert minutes to seconds.

    Args:
        minutes: Number of minutes to convert.

    Returns:
        Equivalent number of seconds.

    Examples:
        >>> convert_minutes_to_seconds(1)
        60
        >>> convert_minutes_to_seconds(5)
        300
        >>> convert_minutes_to_seconds(0)
        0
        >>> convert_minutes_to_seconds(60)
        3600
    """
    return minutes * 60
