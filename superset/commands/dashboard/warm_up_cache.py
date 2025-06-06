from __future__ import annotations

from typing import Any, List, Union

from superset.commands.base import BaseCommand
from superset.commands.chart.warm_up_cache import ChartWarmUpCacheCommand
from superset.commands.dashboard.exceptions import WarmUpCacheDashboardNotFoundError
from superset.extensions import db
from superset.models.dashboard import Dashboard
from superset.models.slice import Slice


class DashboardWarmUpCacheCommand(BaseCommand):
    def __init__(self, dashboard_or_id: Union[int, Dashboard]):
        self._dashboard_or_id = dashboard_or_id
        self._dashboard: Dashboard | None = None
        self._charts: List[Slice] = []

    def run(self) -> List[dict[str, Any]]:
        self.validate()
        assert self._dashboard
        return [
            ChartWarmUpCacheCommand(chart, self._dashboard.id, None).run()
            for chart in self._charts
        ]

    def validate(self) -> None:
        if isinstance(self._dashboard_or_id, Dashboard):
            dashboard = self._dashboard_or_id
        else:
            dashboard = db.session.query(Dashboard).filter_by(id=self._dashboard_or_id).one_or_none()
        if not dashboard:
            raise WarmUpCacheDashboardNotFoundError()
        self._dashboard = dashboard
        self._charts = dashboard.slices