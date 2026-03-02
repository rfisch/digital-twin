"""Pull analytics data from Google Analytics 4 (GA4).

Connects via service account to the Jacqueline Fisch GA4 property
and provides reports for traffic, content performance, funnel analysis,
and growth opportunities.

Usage:
    python scripts/analytics.py                     # full dashboard (last 30 days)
    python scripts/analytics.py --report traffic    # traffic sources only
    python scripts/analytics.py --report content    # top content only
    python scripts/analytics.py --report funnel     # user journey / funnel
    python scripts/analytics.py --report growth     # growth opportunities
    python scripts/analytics.py --days 90           # last 90 days
    python scripts/analytics.py --compare           # compare to previous period
"""

import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Filter,
    FilterExpression,
    Metric,
    OrderBy,
    RunReportRequest,
)

PROPERTY_ID = "359976766"
CREDENTIALS_PATH = Path("credentials/ga_service_account.json")


def get_client() -> BetaAnalyticsDataClient:
    """Create an authenticated GA4 client."""
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CREDENTIALS_PATH)
    return BetaAnalyticsDataClient()


def run_report(
    client: BetaAnalyticsDataClient,
    dimensions: list[str],
    metrics: list[str],
    date_ranges: list[DateRange],
    order_by: str | None = None,
    order_desc: bool = True,
    limit: int = 50,
    dimension_filter: FilterExpression | None = None,
) -> list[dict]:
    """Run a GA4 report and return rows as dicts."""
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=date_ranges,
        limit=limit,
        dimension_filter=dimension_filter,
    )
    if order_by:
        request.order_bys = [
            OrderBy(
                metric=OrderBy.MetricOrderBy(metric_name=order_by),
                desc=order_desc,
            )
        ]

    response = client.run_report(request)

    rows = []
    for row in response.rows:
        r = {}
        for i, dim in enumerate(dimensions):
            r[dim] = row.dimension_values[i].value
        for i, met in enumerate(metrics):
            r[met] = row.metric_values[i].value
        rows.append(r)
    return rows


def date_ranges_for(days: int, compare: bool = False) -> list[DateRange]:
    """Create date ranges for the report."""
    end = datetime.now().date() - timedelta(days=1)  # yesterday
    start = end - timedelta(days=days - 1)
    ranges = [DateRange(start_date=start.isoformat(), end_date=end.isoformat())]
    if compare:
        prev_end = start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=days - 1)
        ranges.append(DateRange(start_date=prev_start.isoformat(), end_date=prev_end.isoformat()))
    return ranges


def fmt_pct(val: str) -> str:
    """Format a decimal as a percentage."""
    try:
        return f"{float(val) * 100:.1f}%"
    except (ValueError, TypeError):
        return val


def fmt_time(seconds_str: str) -> str:
    """Format seconds as m:ss."""
    try:
        s = int(float(seconds_str))
        return f"{s // 60}:{s % 60:02d}"
    except (ValueError, TypeError):
        return seconds_str


# --- Reports ---


def report_overview(client, date_ranges, compare):
    """High-level site metrics."""
    print("\n=== SITE OVERVIEW ===")

    rows = run_report(
        client,
        dimensions=[],
        metrics=[
            "activeUsers", "newUsers", "sessions",
            "averageSessionDuration", "bounceRate",
            "screenPageViews", "engagedSessions",
        ],
        date_ranges=date_ranges,
    )

    if not rows:
        print("  No data")
        return

    r = rows[0]
    engaged = int(r.get("engagedSessions", "0"))
    sessions = int(r.get("sessions", "0"))
    engagement_rate = f"{engaged / sessions * 100:.1f}%" if sessions else "N/A"

    print(f"  Active users:     {int(r['activeUsers']):,}")
    print(f"  New users:        {int(r['newUsers']):,}")
    print(f"  Sessions:         {int(r['sessions']):,}")
    print(f"  Avg session:      {fmt_time(r['averageSessionDuration'])}")
    print(f"  Bounce rate:      {fmt_pct(r['bounceRate'])}")
    print(f"  Engagement rate:  {engagement_rate}")
    print(f"  Page views:       {int(r['screenPageViews']):,}")

    if compare and len(rows) > 1:
        prev = rows[1] if len(rows) > 1 else None
        # Compare periods would show in separate date range rows
        print("  (comparison data requires multi-range support)")


def report_traffic(client, date_ranges):
    """Traffic sources breakdown."""
    print("\n=== TRAFFIC SOURCES ===")

    rows = run_report(
        client,
        dimensions=["sessionDefaultChannelGroup"],
        metrics=["sessions", "activeUsers", "bounceRate", "averageSessionDuration"],
        date_ranges=date_ranges,
        order_by="sessions",
        limit=15,
    )

    total_sessions = sum(int(r["sessions"]) for r in rows)
    print(f"  {'Channel':<30s} {'Sessions':>8s} {'%':>6s} {'Users':>7s} {'Bounce':>7s} {'Avg Time':>8s}")
    print(f"  {'─' * 30} {'─' * 8} {'─' * 6} {'─' * 7} {'─' * 7} {'─' * 8}")
    for r in rows:
        sessions = int(r["sessions"])
        pct = f"{sessions / total_sessions * 100:.1f}%" if total_sessions else ""
        print(f"  {r['sessionDefaultChannelGroup']:<30s} {sessions:>8,} {pct:>6s} {int(r['activeUsers']):>7,} {fmt_pct(r['bounceRate']):>7s} {fmt_time(r['averageSessionDuration']):>8s}")

    # Source/medium detail
    print("\n  --- Top Sources (detail) ---")
    rows = run_report(
        client,
        dimensions=["sessionSourceMedium"],
        metrics=["sessions", "activeUsers"],
        date_ranges=date_ranges,
        order_by="sessions",
        limit=20,
    )
    for r in rows:
        print(f"  {r['sessionSourceMedium']:<50s} {int(r['sessions']):>6,} sessions  {int(r['activeUsers']):>6,} users")


def report_content(client, date_ranges):
    """Top content performance."""
    print("\n=== TOP CONTENT ===")

    rows = run_report(
        client,
        dimensions=["pageTitle"],
        metrics=["screenPageViews", "activeUsers", "bounceRate", "averageSessionDuration"],
        date_ranges=date_ranges,
        order_by="screenPageViews",
        limit=30,
    )

    print(f"  {'Page Title':<65s} {'Views':>6s} {'Users':>6s} {'Bounce':>7s} {'Time':>6s}")
    print(f"  {'─' * 65} {'─' * 6} {'─' * 6} {'─' * 7} {'─' * 6}")
    for r in rows:
        title = r["pageTitle"][:63]
        print(f"  {title:<65s} {int(r['screenPageViews']):>6,} {int(r['activeUsers']):>6,} {fmt_pct(r['bounceRate']):>7s} {fmt_time(r['averageSessionDuration']):>6s}")

    # Landing pages
    print("\n  --- Top Landing Pages ---")
    rows = run_report(
        client,
        dimensions=["landingPagePlusQueryString"],
        metrics=["sessions", "bounceRate", "averageSessionDuration"],
        date_ranges=date_ranges,
        order_by="sessions",
        limit=20,
    )
    print(f"  {'Landing Page':<65s} {'Sessions':>8s} {'Bounce':>7s} {'Time':>6s}")
    print(f"  {'─' * 65} {'─' * 8} {'─' * 7} {'─' * 6}")
    for r in rows:
        path = r["landingPagePlusQueryString"][:63]
        print(f"  {path:<65s} {int(r['sessions']):>8,} {fmt_pct(r['bounceRate']):>7s} {fmt_time(r['averageSessionDuration']):>6s}")


def report_funnel(client, date_ranges):
    """User journey and engagement analysis."""
    print("\n=== USER JOURNEY / FUNNEL ===")

    # New vs returning
    print("\n  --- New vs Returning ---")
    rows = run_report(
        client,
        dimensions=["newVsReturning"],
        metrics=["activeUsers", "sessions", "bounceRate", "averageSessionDuration"],
        date_ranges=date_ranges,
        order_by="activeUsers",
    )
    for r in rows:
        print(f"  {r['newVsReturning']:<15s} {int(r['activeUsers']):>6,} users  {int(r['sessions']):>6,} sessions  bounce {fmt_pct(r['bounceRate'])}  avg {fmt_time(r['averageSessionDuration'])}")

    # Device breakdown
    print("\n  --- Devices ---")
    rows = run_report(
        client,
        dimensions=["deviceCategory"],
        metrics=["activeUsers", "sessions", "bounceRate"],
        date_ranges=date_ranges,
        order_by="activeUsers",
    )
    for r in rows:
        print(f"  {r['deviceCategory']:<15s} {int(r['activeUsers']):>6,} users  {int(r['sessions']):>6,} sessions  bounce {fmt_pct(r['bounceRate'])}")

    # Pages per session (engaged vs bounced)
    print("\n  --- Engagement Depth ---")
    rows = run_report(
        client,
        dimensions=[],
        metrics=[
            "activeUsers", "sessions", "engagedSessions",
            "screenPageViewsPerSession", "averageSessionDuration",
            "eventCount",
        ],
        date_ranges=date_ranges,
    )
    if rows:
        r = rows[0]
        sessions = int(r["sessions"])
        engaged = int(r["engagedSessions"])
        bounced = sessions - engaged
        print(f"  Total sessions:      {sessions:,}")
        print(f"  Engaged sessions:    {engaged:,} ({engaged / sessions * 100:.1f}%)")
        print(f"  Bounced sessions:    {bounced:,} ({bounced / sessions * 100:.1f}%)")
        print(f"  Pages/session:       {float(r['screenPageViewsPerSession']):.2f}")
        print(f"  Avg session time:    {fmt_time(r['averageSessionDuration'])}")
        print(f"  Total events:        {int(r['eventCount']):,}")

    # Top countries
    print("\n  --- Top Countries ---")
    rows = run_report(
        client,
        dimensions=["country"],
        metrics=["activeUsers", "sessions"],
        date_ranges=date_ranges,
        order_by="activeUsers",
        limit=15,
    )
    for r in rows:
        print(f"  {r['country']:<25s} {int(r['activeUsers']):>6,} users  {int(r['sessions']):>6,} sessions")


def report_growth(client, date_ranges):
    """Growth opportunities — underperforming content, high-bounce pages, etc."""
    print("\n=== GROWTH OPPORTUNITIES ===")

    # High traffic + high bounce = biggest capture opportunities
    print("\n  --- High Traffic, High Bounce (capture opportunities) ---")
    rows = run_report(
        client,
        dimensions=["pageTitle"],
        metrics=["screenPageViews", "activeUsers", "bounceRate"],
        date_ranges=date_ranges,
        order_by="screenPageViews",
        limit=50,
    )
    # Filter for high-traffic blog posts with bounce > 45%
    opportunities = [
        r for r in rows
        if float(r["bounceRate"]) > 0.45
        and int(r["screenPageViews"]) > 20
        and "| The Intuitive Writing School" not in r["pageTitle"]
    ]
    print(f"  {'Page Title':<65s} {'Views':>6s} {'Bounce':>7s} {'Lost Users':>10s}")
    print(f"  {'─' * 65} {'─' * 6} {'─' * 7} {'─' * 10}")
    for r in opportunities[:15]:
        views = int(r["screenPageViews"])
        bounce = float(r["bounceRate"])
        lost = int(views * bounce)
        title = r["pageTitle"][:63]
        print(f"  {title:<65s} {views:>6,} {fmt_pct(str(bounce)):>7s} {lost:>10,}")

    # Low bounce pages = what's working (model for others)
    print("\n  --- Low Bounce Pages (what's working) ---")
    rows_low = [
        r for r in rows
        if float(r["bounceRate"]) < 0.35
        and int(r["screenPageViews"]) > 10
    ]
    for r in sorted(rows_low, key=lambda x: float(x["bounceRate"]))[:10]:
        title = r["pageTitle"][:63]
        print(f"  {title:<65s} {int(r['screenPageViews']):>6,} views  bounce {fmt_pct(r['bounceRate'])}")

    # Search terms driving traffic (if available)
    print("\n  --- Top Search Queries (from Google) ---")
    try:
        rows = run_report(
            client,
            dimensions=["sessionGoogleAdsQuery"],
            metrics=["sessions"],
            date_ranges=date_ranges,
            order_by="sessions",
            limit=20,
        )
        if rows:
            for r in rows:
                print(f"  {r['sessionGoogleAdsQuery']:<50s} {int(r['sessions']):>6,} sessions")
        else:
            print("  (No search query data — needs Search Console integration)")
    except Exception:
        print("  (Search query data not available)")


# --- Main ---


def main():
    parser = argparse.ArgumentParser(description="GA4 Analytics Dashboard")
    parser.add_argument(
        "--report",
        choices=["traffic", "content", "funnel", "growth"],
        help="Run a specific report (default: all)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to analyze (default: 30)",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare to previous period",
    )
    args = parser.parse_args()

    client = get_client()
    ranges = date_ranges_for(args.days, args.compare)

    period_end = (datetime.now().date() - timedelta(days=1)).isoformat()
    period_start = (datetime.now().date() - timedelta(days=args.days)).isoformat()
    print(f"Period: {period_start} to {period_end} ({args.days} days)")

    if args.report is None or args.report == "traffic":
        if args.report is None:
            report_overview(client, ranges, args.compare)
        report_traffic(client, ranges)

    if args.report is None or args.report == "content":
        report_content(client, ranges)

    if args.report is None or args.report == "funnel":
        report_funnel(client, ranges)

    if args.report is None or args.report == "growth":
        report_growth(client, ranges)


if __name__ == "__main__":
    main()
