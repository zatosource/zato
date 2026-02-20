from typing import Any, TYPE_CHECKING

import logging
import requests
import sys
from dataclasses import dataclass
from zato.common.marshal_.api import Model
from zato.common.typing_ import anydict, list_, optional, strdict


class GrafanaGridPos(Model):
    x: int
    y: int
    w: int
    h: int

class GrafanaDatasource(Model):
    type: str
    uid: str

class GrafanaTarget(Model):
    expr: str
    refId: str
    datasource: GrafanaDatasource

class GrafanaThreshold(Model):
    color: str
    value: optional[int]

class GrafanaThresholds(Model):
    steps: list_[GrafanaThreshold]

class GrafanaColor(Model):
    mode: str

class GrafanaStacking(Model):
    mode: str
    group: str

class GrafanaScaleDistribution(Model):
    type: str

class GrafanaThresholdsStyle(Model):
    mode: str

class GrafanaHideFrom(Model):
    legend: bool
    tooltip: bool
    vis: bool

class GrafanaCustom(Model):
    drawStyle: str
    lineInterpolation: str
    barAlignment: int
    lineWidth: int
    fillOpacity: int
    gradientMode: str
    spanNulls: bool
    insertNulls: bool
    showPoints: str
    pointSize: int
    stacking: GrafanaStacking
    axisPlacement: str
    axisLabel: str
    axisColorMode: str
    scaleDistribution: GrafanaScaleDistribution
    axisCenteredZero: bool
    hideFrom: GrafanaHideFrom
    thresholdsStyle: GrafanaThresholdsStyle

class GrafanaDefaults(Model):
    color: GrafanaColor
    custom: GrafanaCustom
    mappings: list_[strdict]
    thresholds: GrafanaThresholds

class GrafanaFieldConfig(Model):
    defaults: GrafanaDefaults

class GrafanaTimepicker(Model):
    ...

class GrafanaLegend(Model):
    ...

class GrafanaTooltip(Model):
    mode: str
    sort: str

class GrafanaOptions(Model):
    legend: GrafanaLegend
    tooltip: GrafanaTooltip

class GrafanaPanel(Model):
    id: int
    title: str
    type: str
    gridPos: GrafanaGridPos
    targets: list_[GrafanaTarget]
    fieldConfig: GrafanaFieldConfig
    options: GrafanaOptions

class GrafanaTime(Model):
    from_: str
    to: str
    def to_dict(self: Any) -> None: ...

class GrafanaVariableCurrent(Model):
    text: str
    value: list_[str]

class GrafanaVariableOption(Model):
    text: str
    value: str
    selected: bool

class GrafanaVariable(Model):
    name: str
    type: str
    datasource: GrafanaDatasource
    query: str
    multi: bool
    includeAll: bool
    allValue: str
    current: GrafanaVariableCurrent
    options: list_[GrafanaVariableOption]
    refresh: int

class GrafanaTemplating(Model):
    list_: list_[GrafanaVariable]
    def to_dict(self: Any) -> None: ...

class GrafanaDashboard(Model):
    id: optional[int]
    uid: optional[str]
    title: str
    tags: list_[str]
    timezone: str
    panels: list_[GrafanaPanel]
    time: GrafanaTime
    timepicker: strdict
    templating: GrafanaTemplating
    refresh: str

class GrafanaDashboardRequest(Model):
    dashboard: GrafanaDashboard
    overwrite: bool

class PanelConfig(Model):
    panel_id: int
    title: str
    query: str
    panel_type: str
    x: int
    y: int
    w: int
    h: int

class GrafanaDashboardBuilder:
    grafana_url: Any
    auth: Any
    headers: Any
    def __init__(self: Any, grafana_url: str = ..., username: str = ..., password: str = ...) -> None: ...
    def create_panel(self: Any, panel_id: int, title: str, query: str, x: int = ..., y: int = ..., w: int = ..., h: int = ...) -> anydict: ...
    def create_process_monitoring_dashboard(self: Any) -> anydict: ...
    def create_dashboard(self: Any, dashboard_config: anydict) -> bool: ...
    def setup_dashboards(self: Any) -> bool: ...

def main() -> None: ...
