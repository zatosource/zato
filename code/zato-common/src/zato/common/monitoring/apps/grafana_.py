# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import requests
import sys
from dataclasses import dataclass

# Zato
from zato.common.marshal_.api import Model
from zato.common.typing_ import anydict, list_, optional, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Grafana Dashboard Models

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class GrafanaGridPos(Model):
    x: 'int'
    y: 'int'
    w: 'int'
    h: 'int'

@dataclass(init=False)
class GrafanaDatasource(Model):
    type: 'str'
    uid: 'str'

@dataclass(init=False)
class GrafanaTarget(Model):
    expr: 'str'
    refId: 'str'
    datasource: 'GrafanaDatasource'

@dataclass(init=False)
class GrafanaThreshold(Model):
    color: 'str'
    value: 'optional[int]'

@dataclass(init=False)
class GrafanaThresholds(Model):
    steps: 'list_[GrafanaThreshold]'

@dataclass(init=False)
class GrafanaColor(Model):
    mode: 'str'

@dataclass(init=False)
class GrafanaStacking(Model):
    mode: 'str'
    group: 'str'

@dataclass(init=False)
class GrafanaScaleDistribution(Model):
    type: 'str'

@dataclass(init=False)
class GrafanaCustom(Model):
    drawStyle: 'str'
    lineInterpolation: 'str'
    barAlignment: 'int'
    lineWidth: 'int'
    fillOpacity: 'int'
    gradientMode: 'str'
    spanNulls: 'bool'
    insertNulls: 'bool'
    showPoints: 'str'
    pointSize: 'int'
    stacking: 'GrafanaStacking'
    axisPlacement: 'str'
    axisLabel: 'str'
    axisColorMode: 'str'
    scaleDistribution: 'GrafanaScaleDistribution'
    axisCenteredZero: 'bool'
    hideFrom: 'strdict'
    thresholdsStyle: 'strdict'

@dataclass(init=False)
class GrafanaDefaults(Model):
    color: 'GrafanaColor'
    custom: 'GrafanaCustom'
    mappings: 'list_[strdict]'
    thresholds: 'GrafanaThresholds'

@dataclass(init=False)
class GrafanaFieldConfig(Model):
    defaults: 'GrafanaDefaults'

@dataclass(init=False)
class GrafanaTimepicker(Model):
    pass

@dataclass(init=False)
class GrafanaLegend(Model):
    pass

@dataclass(init=False)
class GrafanaTooltip(Model):
    mode: 'str'
    sort: 'str'

@dataclass(init=False)
class GrafanaOptions(Model):
    legend: 'GrafanaLegend'
    tooltip: 'GrafanaTooltip'

@dataclass(init=False)
class GrafanaPanel(Model):
    id: 'int'
    title: 'str'
    type: 'str'
    gridPos: 'GrafanaGridPos'
    targets: 'list_[GrafanaTarget]'
    fieldConfig: 'GrafanaFieldConfig'
    options: 'GrafanaOptions'

@dataclass(init=False)
class GrafanaTime(Model):
    from_: 'str'
    to: 'str'

    def to_dict(self):
        data = super().to_dict()
        # Rename from_ to from for Grafana API
        if 'from_' in data:
            data['from'] = data.pop('from_')
        return data

@dataclass(init=False)
class GrafanaVariable(Model):
    name: 'str'
    type: 'str'
    datasource: 'GrafanaDatasource'
    query: 'str'
    multi: 'bool'
    includeAll: 'bool'
    allValue: 'str'
    current: 'strdict'
    options: 'list_[strdict]'
    refresh: 'int'

@dataclass(init=False)
class GrafanaTemplating(Model):
    list_: 'list_[GrafanaVariable]'

    def to_dict(self):
        data = super().to_dict()
        # Rename list_ to list for Grafana API
        if 'list_' in data:
            data['list'] = data.pop('list_')
        return data

@dataclass(init=False)
class GrafanaDashboard(Model):
    id: 'optional[int]'
    uid: 'optional[str]'
    title: 'str'
    tags: 'list_[str]'
    timezone: 'str'
    panels: 'list_[GrafanaPanel]'
    time: 'GrafanaTime'
    timepicker: 'strdict'
    templating: 'GrafanaTemplating'
    refresh: 'str'

@dataclass(init=False)
class GrafanaDashboardRequest(Model):
    dashboard: 'GrafanaDashboard'
    overwrite: 'bool'

@dataclass(init=False)
class PanelConfig(Model):
    panel_id: 'int'
    title: 'str'
    query: 'str'
    panel_type: 'str' = 'timeseries'
    x: 'int' = 0
    y: 'int' = 0
    w: 'int' = 12
    h: 'int' = 8

# ################################################################################################################################
# ################################################################################################################################

class GrafanaDashboardBuilder:
    """ Creates Grafana dashboards and panels programmatically via REST API.
    """

    def __init__(self, grafana_url:'str'='http://localhost:3000', username:'str'='admin', password:'str'='admin') -> 'None':
        self.grafana_url = grafana_url
        self.auth = (username, password)
        self.headers = {'Content-Type': 'application/json'}

    def create_panel(self, panel_id:'int', title:'str', query:'str', x:'int'=0, y:'int'=0, w:'int'=12, h:'int'=8) -> 'anydict':
        """ Create a single panel configuration.
        """
        datasource = GrafanaDatasource()
        datasource.type = 'prometheus'
        datasource.uid = 'prometheus'

        grid_pos = GrafanaGridPos()
        grid_pos.x = x
        grid_pos.y = y
        grid_pos.w = w
        grid_pos.h = h

        target = GrafanaTarget()
        target.datasource = datasource
        target.expr = query
        target.refId = 'A'

        threshold = GrafanaThreshold()
        threshold.color = 'green'
        threshold.value = None

        thresholds = GrafanaThresholds()
        thresholds.steps = [threshold]

        # Field configuration setup
        field_config = GrafanaFieldConfig()
        field_config.defaults = GrafanaDefaults()

        # Color configuration
        color = GrafanaColor()
        color.mode = 'palette-classic'
        field_config.defaults.color = color

        # Custom display settings
        custom = GrafanaCustom()
        custom.drawStyle = 'line'
        custom.lineInterpolation = 'linear'
        custom.barAlignment = 0
        custom.lineWidth = 1
        custom.fillOpacity = 0
        custom.gradientMode = 'none'
        custom.spanNulls = False
        custom.insertNulls = False
        custom.showPoints = 'auto'
        custom.pointSize = 5
        
        # Stacking configuration
        stacking = GrafanaStacking()
        stacking.mode = 'none'
        stacking.group = 'A'
        custom.stacking = stacking
        
        # Axis configuration
        custom.axisPlacement = 'auto'
        custom.axisLabel = ''
        custom.axisColorMode = 'text'
        
        # Scale distribution
        scale_distribution = GrafanaScaleDistribution()
        scale_distribution.type = 'linear'
        custom.scaleDistribution = scale_distribution
        
        custom.axisCenteredZero = False
        custom.hideFrom = {'legend': False, 'tooltip': False, 'vis': False}
        custom.thresholdsStyle = {'mode': 'off'}
        field_config.defaults.custom = custom

        # Finalize field config
        field_config.defaults.mappings = []
        field_config.defaults.thresholds = thresholds

        # Panel creation
        panel = GrafanaPanel()
        panel.id = panel_id
        panel.title = title
        panel.type = 'timeseries'
        panel.targets = [target]
        panel.gridPos = grid_pos
        panel.fieldConfig = field_config

        # Panel options setup
        legend = GrafanaLegend()

        tooltip = GrafanaTooltip()
        tooltip.mode = 'single'
        tooltip.sort = 'none'

        options = GrafanaOptions()
        options.legend = legend
        options.tooltip = tooltip
        panel.options = options

        return panel.to_dict()

    def create_process_monitoring_dashboard(self) -> 'anydict':
        """ Create main process monitoring dashboard.
        """
        datasource = GrafanaDatasource()
        datasource.type = 'prometheus'
        datasource.uid = 'prometheus'

        var1 = GrafanaVariable()
        var1.name = 'process_name'
        var1.type = 'query'
        var1.datasource = datasource
        var1.query = 'label_values(process_value, process_name)'
        var1.multi = True
        var1.includeAll = True
        var1.allValue = '.*'
        var1.current = {'text': 'All', 'value': ['$__all']}
        var1.options = [{'text': 'All', 'value': '$__all', 'selected': True}]
        var1.refresh = 1

        var2 = GrafanaVariable()
        var2.name = 'ctx_id'
        var2.type = 'query'
        var2.datasource = datasource
        var2.query = 'label_values(process_value{process_name=~"$process_name"}, ctx_id)'
        var2.multi = True
        var2.includeAll = True
        var2.allValue = '.*'
        var2.current = {'text': 'All', 'value': ['$__all']}
        var2.options = [{'text': 'All', 'value': '$__all', 'selected': True}]
        var2.refresh = 2

        templating = GrafanaTemplating()
        templating.list_ = [var1, var2]

        panels = [
            self.create_panel(1, 'Process metrics by instance', 'process_value{ctx_id=~".+"}', x=0, y=0, w=12, h=8),
            self.create_panel(2, 'Global metrics', 'process_value{process_name="global"}', x=0, y=8, w=12, h=8),
            self.create_panel(3, 'Aircraft handling metrics', 'process_value{process_name="AircraftHandling"}', x=0, y=16, w=12, h=8),
            self.create_panel(4, 'Applicant processing metrics', 'process_value{process_name="ApplicantProcessing"}', x=0, y=24, w=12, h=8)
        ]

        time = GrafanaTime()
        time.from_ = 'now-5m'
        time.to = 'now'

        dashboard = GrafanaDashboard()
        dashboard.id = None
        dashboard.uid = None
        dashboard.title = 'Zato process monitoring'
        dashboard.tags = ['zato', 'monitoring']
        dashboard.timezone = 'browser'
        dashboard.panels = panels
        dashboard.time = time.to_dict()
        timepicker = GrafanaTimepicker()
        dashboard.timepicker = timepicker.to_dict()
        dashboard.templating = templating.to_dict()
        dashboard.refresh = '5s'

        dashboard_request = GrafanaDashboardRequest()
        dashboard_request.dashboard = dashboard
        dashboard_request.overwrite = True

        result = dashboard_request.to_dict()
        logger.info(f'Dashboard JSON being sent: {result}')

        return result

    def create_dashboard(self, dashboard_config:'anydict') -> 'bool':
        """ Create dashboard via REST API.
        """
        url = f'{self.grafana_url}/api/dashboards/db'

        try:
            response = requests.post(url,
                json=dashboard_config,
                auth=self.auth,
                headers=self.headers,
                timeout=10)

            if response.status_code == 200:
                result = response.json()
                logger.info(f'Dashboard created: {result.get("url", "unknown")}')
                return True
            else:
                logger.error(f'Failed to create dashboard: {response.status_code} - {response.text}')
                return False

        except Exception as e:
            logger.error(f'Error creating dashboard: {e}')
            return False

    def setup_dashboards(self) -> 'bool':
        """ Set up all monitoring dashboards.
        """
        logger.info('Creating Zato monitoring dashboards...')

        # Main process monitoring dashboard
        dashboard = self.create_process_monitoring_dashboard()
        success = self.create_dashboard(dashboard)

        if success:
            logger.info('Dashboard setup completed successfully')
            return True
        else:
            logger.error('Dashboard setup failed')
            return False

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Main entry point.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    builder = GrafanaDashboardBuilder()
    success = builder.setup_dashboards()
    sys.exit(0 if success else 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
