import math

from error_budget import (alert_threshold, budget_minutes, budget_requests, burn_rate,
                          hours_to_exhaustion)


def test_budget_minutes_match_the_book_table():
    assert math.isclose(budget_minutes(99.0), 432.0)        # 7 h 12 min
    assert math.isclose(budget_minutes(99.5), 216.0)        # 3 h 36 min
    assert math.isclose(budget_minutes(99.9), 43.2)
    assert math.isclose(budget_minutes(99.95), 21.6)
    assert math.isclose(budget_minutes(99.99), 4.32)


def test_budget_requests():
    assert budget_requests(99.9, 1_000_000) == 1_000


def test_burn_rate_of_one_uses_the_whole_window():
    assert math.isclose(burn_rate(99.9, 0.1), 1.0)
    assert math.isclose(hours_to_exhaustion(99.9, 0.1), 720.0)


def test_fast_burn_threshold_matches_the_prometheus_rule():
    # 14.4 * 0.001 in the book's alert expression
    assert math.isclose(alert_threshold(99.9, 14.4), 0.0144)
    # 14.4x burn for one hour consumes 2% of a 30-day budget
    assert math.isclose(14.4 * 1 / 720, 0.02)
