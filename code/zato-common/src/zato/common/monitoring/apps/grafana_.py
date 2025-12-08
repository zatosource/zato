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
class GrafanaTarget(Model):
    expr: 'str'
    refId: 'str'
    datasource: 'strdict'

@dataclass(init=False)
class GrafanaFieldConfig(Model):
    defaults: 'strdict'

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
    datasource: 'strdict'
    query: 'str'
    multi: 'bool'
    includeAll: 'bool'
    allValue: 'str'

@dataclass(init=False)
class GrafanaTemplating(Model):
    list_: 'list_[GrafanaVariable]'

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

# ################################################################################################################################
# ################################################################################################################################

class GrafanaDashboardBuilder:
    """ Creates Grafana dashboards and panels programmatically via REST API.
    """

    def __init__(self, grafana_url:'str'='http://localhost:3000', username:'str'='admin', password:'str'='admin') -> 'None':
        self.grafana_url = grafana_url
        self.auth = (username, password)
        self.headers = {'Content-Type': 'application/json'}

    def create_panel(self, panel_id:'int', title:'str', query:'str', panel_type:'str'='timeseries', x:'int'=0, y:'int'=0, w:'int'=12, h:'int'=8) -> 'anydict':
        """ Create a panel configuration.
        """
        return {
            'id': panel_id,
            'title': title,
            'type': panel_type,
            'gridPos': {'x': x, 'y': y, 'w': w, 'h': h},
            'targets': [{
                'expr': query,
                'refId': 'A',
                'datasource': {'type': 'prometheus', 'uid': 'prometheus'}
            }],
            'fieldConfig': {
                'defaults': {
                    'color': {'mode': 'palette-classic'},
                    'custom': {'drawStyle': 'line', 'lineInterpolation': 'linear', 'spanNulls': False},
                    'mappings': [],
                    'thresholds': {'steps': [{'color': 'green', 'value': None}]}
                }
            },
            'options': {
                'legend': {'displayMode': 'visible'},
                'tooltip': {'mode': 'single', 'sort': 'none'}
            }
        }

    def create_process_monitoring_dashboard(self) -> 'anydict':
        """ Create main process monitoring dashboard.
        """
        panels = [
            self.create_panel(1, 'Process metrics by instance',
                'process_value{ctx_id!=""}', x=0, y=0, w=12, h=8),

            self.create_panel(2, 'Global metrics',
                'process_value{process_name="global"}', x=0, y=8, w=12, h=8),

            self.create_panel(3, 'Aircraft handling metrics',
                'process_value{process_name="AircraftHandling"}', x=0, y=16, w=12, h=8),

            self.create_panel(4, 'Applicant processing metrics',
                'process_value{process_name="ApplicantProcessing"}', x=0, y=24, w=12, h=8)
        ]

        dashboard = {
            'dashboard': {
                'id': None,
                'uid': None,
                'title': 'Zato process monitoring',
                'tags': ['zato', 'monitoring'],
                'timezone': 'browser',
                'panels': panels,
                'time': {'from': 'now-1h', 'to': 'now'},
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
                            'allValue': '.*'
                        },
                        {
                            'name': 'ctx_id',
                            'type': 'query',
                            'datasource': {'type': 'prometheus', 'uid': 'prometheus'},
                            'query': 'label_values(process_value{process_name=~"$process_name"}, ctx_id)',
                            'multi': True,
                            'includeAll': True,
                            'allValue': '.*'
                        }
                    ]
                },
                'refresh': '10s'
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
