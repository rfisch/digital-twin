"""GA4 client for fetching top blog posts.

Wraps the Google Analytics Data API to provide a ranked dropdown
of blog posts for the LinkedIn multi-post generator. Reuses patterns
from scripts/analytics.py.

Scoring: composite of views, session duration, and sessions, with
revisit ratio (sessions / unique users) as a multiplier. Posts where
people come back, read longer, and view more rank highest.
"""

import os
import time
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
CREDENTIALS_PATH = Path(__file__).parent.parent / "credentials" / "ga_service_account.json"
SITE_BASE = "https://theintuitivewritingschool.com"

# Cache duration in seconds
CACHE_TTL = 3600  # 1 hour


class AnalyticsClient:
    """Fetch top blog posts from GA4 for the LinkedIn dropdown."""

    def __init__(self):
        self._client: BetaAnalyticsDataClient | None = None
        self._cache: dict[int, dict] = {}  # {days: {"data": [...], "ts": float}}

    def is_configured(self) -> bool:
        return CREDENTIALS_PATH.exists()

    def _get_client(self) -> BetaAnalyticsDataClient:
        if self._client is None:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CREDENTIALS_PATH)
            self._client = BetaAnalyticsDataClient()
        return self._client

    def _date_range(self, days: int) -> list[DateRange]:
        end = datetime.now().date() - timedelta(days=1)
        start = end - timedelta(days=days - 1)
        return [DateRange(start_date=start.isoformat(), end_date=end.isoformat())]

    def _run_report(
        self,
        dimensions: list[str],
        metrics: list[str],
        date_ranges: list[DateRange],
        order_by: str | None = None,
        limit: int = 50,
        dimension_filter: FilterExpression | None = None,
    ) -> list[dict]:
        client = self._get_client()
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
                    desc=True,
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

    def get_top_blog_posts(self, days: int = 30, limit: int = 20) -> list[dict]:
        """Return top blog posts ranked by composite score.

        Score = views * avg_session_duration * sessions * revisit_multiplier
        where revisit_multiplier = max(1.0, sessions / active_users)

        Returns: [{"title": str, "path": str, "url": str, "sessions": int,
                    "views": int, "avg_duration": float, "revisit_ratio": float,
                    "score": float}, ...]
        """
        # Check cache
        cached = self._cache.get(days)
        if cached and (time.time() - cached["ts"]) < CACHE_TTL:
            return cached["data"][:limit]

        date_ranges = self._date_range(days)

        # Single query with path + title + all scoring metrics
        blog_filter = FilterExpression(
            filter=Filter(
                field_name="landingPagePlusQueryString",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.BEGINS_WITH,
                    value="/blog/",
                ),
            )
        )

        rows = self._run_report(
            dimensions=["landingPagePlusQueryString", "pageTitle"],
            metrics=[
                "screenPageViews",
                "sessions",
                "activeUsers",
                "averageSessionDuration",
            ],
            date_ranges=date_ranges,
            order_by="screenPageViews",
            limit=100,
            dimension_filter=blog_filter,
        )

        posts = []
        for r in rows:
            path = r["landingPagePlusQueryString"]

            # Skip non-post paths
            if path.rstrip("/") == "/blog":
                continue
            if "?" in path:  # tag/category pages like /blog?tag=...
                continue

            views = int(r["screenPageViews"])
            sessions = int(r["sessions"])
            active_users = int(r["activeUsers"]) or 1
            avg_duration = float(r["averageSessionDuration"])

            # Revisit ratio: how many times each unique user comes back
            revisit_ratio = sessions / active_users
            revisit_multiplier = max(1.0, revisit_ratio)

            # Composite score — floor duration at 1.0 so zero duration
            # doesn't zero out the entire score
            duration_factor = max(1.0, avg_duration)
            score = views * duration_factor * sessions * revisit_multiplier

            title = r["pageTitle"]
            # Strip site suffix if present
            for suffix in [" | The Intuitive Writing School", " — The Intuitive Writing School"]:
                if title.endswith(suffix):
                    title = title[: -len(suffix)].strip()

            posts.append({
                "title": title,
                "path": path,
                "url": SITE_BASE + path,
                "views": views,
                "sessions": sessions,
                "avg_duration": round(avg_duration, 1),
                "revisit_ratio": round(revisit_ratio, 2),
                "score": round(score, 1),
            })

        # Sort by composite score descending
        posts.sort(key=lambda p: p["score"], reverse=True)

        # Cache results
        self._cache[days] = {"data": posts, "ts": time.time()}

        return posts[:limit]

    def invalidate_cache(self):
        """Clear the cache (e.g., when time range changes)."""
        self._cache.clear()
