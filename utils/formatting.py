"""Number, CTR, and position formatting utilities."""

from typing import Union


def format_number(n: Union[int, float]) -> str:
    """Format a number with K/M suffixes for display."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return f"{int(n):,}"


def format_ctr(ctr: float) -> str:
    """Format CTR as a percentage string."""
    return f"{ctr * 100:.2f}%"


def format_position(pos: float) -> str:
    """Format average position."""
    return f"{pos:.1f}"


def format_delta(current: float, previous: float) -> str:
    """Format a delta value for KPI cards."""
    if previous == 0:
        return "N/A"
    change = ((current - previous) / previous) * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.1f}%"


def format_ctr_delta(current: float, previous: float) -> str:
    """Format CTR delta in percentage points."""
    diff = (current - previous) * 100
    sign = "+" if diff >= 0 else ""
    return f"{sign}{diff:.2f}pp"


def format_position_delta(current: float, previous: float) -> str:
    """Format position delta (lower is better, so invert sign for display)."""
    diff = previous - current  # Positive = improvement
    sign = "+" if diff >= 0 else ""
    return f"{sign}{diff:.1f}"
