"""Chapter 6: error budget and burn-rate calculator.

usage:
    python error_budget.py --slo 99.9                       # budget for a 30-day window
    python error_budget.py --slo 99.9 --requests 12000000   # also in requests
    python error_budget.py --slo 99.9 --error-rate 0.5      # how fast a 0.5% error rate burns it
"""
import argparse


def budget_minutes(slo_percent: float, window_days: float = 30) -> float:
    """Minutes of full downtime the SLO allows over the window."""
    return (1 - slo_percent / 100) * window_days * 24 * 60


def budget_requests(slo_percent: float, total_requests: int) -> int:
    """Failed requests the SLO allows over the window."""
    return int(round((1 - slo_percent / 100) * total_requests))


def burn_rate(slo_percent: float, error_rate_percent: float) -> float:
    """1.0 consumes exactly the whole budget over the window; 14.4 consumes it 14.4x faster."""
    return (error_rate_percent / 100) / (1 - slo_percent / 100)


def hours_to_exhaustion(slo_percent: float, error_rate_percent: float, window_days: float = 30) -> float:
    rate = burn_rate(slo_percent, error_rate_percent)
    return float("inf") if rate == 0 else window_days * 24 / rate


def alert_threshold(slo_percent: float, rate: float) -> float:
    """Error ratio that triggers an alert at a given burn rate (the value in the PromQL rule)."""
    return rate * (1 - slo_percent / 100)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--slo", type=float, required=True, help="SLO in percent, e.g. 99.9")
    p.add_argument("--window-days", type=float, default=30)
    p.add_argument("--requests", type=int, help="requests expected over the window")
    p.add_argument("--error-rate", type=float, help="current error rate in percent")
    a = p.parse_args()

    minutes = budget_minutes(a.slo, a.window_days)
    print(f"SLO {a.slo}% over {a.window_days:g} days")
    print(f"  error budget: {minutes:.1f} minutes of full downtime ({minutes / 60:.2f} hours)")
    if a.requests:
        print(f"  error budget: {budget_requests(a.slo, a.requests):,} failed requests out of {a.requests:,}")
    print("  alert thresholds (error ratio to put in the PromQL rule):")
    for rate, label in [(14.4, "page, 1h/5m windows"), (6, "page, 6h/30m windows"), (1, "ticket, 3d/6h windows")]:
        print(f"    burn rate {rate:>4}: error ratio > {alert_threshold(a.slo, rate):.4%}  ({label})")
    if a.error_rate is not None:
        rate = burn_rate(a.slo, a.error_rate)
        print(f"  at {a.error_rate}% errors: burn rate {rate:.1f}, budget gone in "
              f"{hours_to_exhaustion(a.slo, a.error_rate, a.window_days):.1f} hours")


if __name__ == "__main__":
    main()
