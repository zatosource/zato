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
class GrafanaCustom(Model):
    drawStyle: 'str'
    lineInterpolation: 'str'
    spanNulls: 'bool'

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
class GrafanaOptions(Model):
    legend: 'strdict'
    tooltip: 'strdict'

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

    def create_panel(self, config:'PanelConfig') -> 'anydict':
        """ Create a panel configuration.
        """
        datasource = GrafanaDatasource()
        datasource.type = 'prometheus'
        datasource.uid = 'prometheus'

        panel = GrafanaPanel()
        panel.id = config.panel_id
        panel.title = config.title
        panel.type = config.panel_type

        panel.gridPos = GrafanaGridPos()
        panel.gridPos.x = config.x
        panel.gridPos.y = config.y
        panel.gridPos.w = config.w
        panel.gridPos.h = config.h

        target = GrafanaTarget()
        target.expr = config.query
        target.refId = 'A'
        target.datasource = datasource
        panel.targets = [target]

        panel.fieldConfig = GrafanaFieldConfig()
        panel.fieldConfig.defaults = GrafanaDefaults()
        panel.fieldConfig.defaults.color = GrafanaColor()
        panel.fieldConfig.defaults.color.mode = 'palette-classic'
        panel.fieldConfig.defaults.custom = GrafanaCustom()
        panel.fieldConfig.defaults.custom.drawStyle = 'line'
        panel.fieldConfig.defaults.custom.lineInterpolation = 'linear'
        panel.fieldConfig.defaults.custom.spanNulls = False
        panel.fieldConfig.defaults.mappings = []
        threshold = GrafanaThreshold()
        threshold.color = 'green'
        threshold.value = None

        thresholds = GrafanaThresholds()
        thresholds.steps = [threshold]
        panel.fieldConfig.defaults.thresholds = thresholds

        panel.options = GrafanaOptions()
        panel.options.legend = {'displayMode': 'visible'}
        panel.options.tooltip = {'mode': 'single', 'sort': 'none'}

        return panel.to_dict()

    def create_process_monitoring_dashboard(self) -> 'anydict':
        """ Create main process monitoring dashboard.
        """
        config1 = PanelConfig()
        config1.panel_id = 1
        config1.title = 'Process metrics by instance'
        config1.query = 'process_value{ctx_id!=""}'
        config1.x = 0
        config1.y = 0
        config1.w = 12
        config1.h = 8

        config2 = PanelConfig()
        config2.panel_id = 2
        config2.title = 'Global metrics'
        config2.query = 'process_value{process_name="global"}'
        config2.x = 0
        config2.y = 8
        config2.w = 12
        config2.h = 8

        config3 = PanelConfig()
        config3.panel_id = 3
        config3.title = 'Aircraft handling metrics'
        config3.query = 'process_value{process_name="AircraftHandling"}'
        config3.x = 0
        config3.y = 16
        config3.w = 12
        config3.h = 8

        config4 = PanelConfig()
        config4.panel_id = 4
        config4.title = 'Applicant processing metrics'
        config4.query = 'process_value{process_name="ApplicantProcessing"}'
        config4.x = 0
        config4.y = 24
        config4.w = 12
        config4.h = 8

        panel1 = self.create_panel(config1)
        panel2 = self.create_panel(config2)
        panel3 = self.create_panel(config3)
        panel4 = self.create_panel(config4)
        panels = [panel1, panel2, panel3, panel4]

        dashboard = {
            'dashboard': {
                'id': None,
                'uid': None,
                'title': 'Zato process monitoring',
                'tags': ['zato', 'monitoring'],
                'timezone': 'browser',
                'panels': panels,
                'time': {'from': 'now-5m', 'to': 'now'},
                'timepicker': {},
                'templating': {
                    'list': [
                        {
                            'name': 'process_name',
                            'type': 'query',
                            'datasource': {'type': 'prometheus', 'uid': 'prometheus'},
                            'query': 'label_values(process_value, process_name)',
                            'multi': True,
                            'includeAll': True,
                            'allValue': '.*',
                            'current': {'text': 'All', 'value': ['$__all']},
                            'options': [{'text': 'All', 'value': '$__all', 'selected': True}],
                            'refresh': 1
                        },
                        {
                            'name': 'ctx_id',
                            'type': 'query',
                            'datasource': {'type': 'prometheus', 'uid': 'prometheus'},
                            'query': 'label_values(process_value{process_name=~"$process_name"}, ctx_id)',
                            'multi': True,
                            'includeAll': True,
                            'allValue': '.*',
                            'current': {'text': 'All', 'value': ['$__all']},
                            'options': [{'text': 'All', 'value': '$__all', 'selected': True}],
                            'refresh': 2
                        }
                    ]
                },
                'refresh': '5s'
            },
            'overwrite': True
        }

        return dashboard

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
    builder = GrafanaDashboardBuilder()
    success = builder.setup_dashboards()
    sys.exit(0 if success else 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
