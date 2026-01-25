# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from zato.admin.web.views.models import ContentRow

updates_page_config = {}
updates_page_config['title'] = 'Install updates'
updates_page_config['api_prefix'] = '/zato/updates/'
updates_page_config['step1_label'] = 'Download'
updates_page_config['step2_label'] = 'Install'
updates_page_config['check_button_label'] = 'Check for updates'
updates_page_config['action_button_label'] = 'Install updates'
updates_page_config['version_section_title'] = 'Version info'
updates_page_config['config_section_title'] = 'Config'
updates_page_config['logs_section_title'] = 'Update log'
updates_page_config['up_to_date_label'] = 'Up to date?'
updates_page_config['your_version_label'] = 'Your version'
updates_page_config['latest_version_label'] = 'Latest version'
updates_page_config['auto_update_label'] = 'Auto-update'
updates_page_config['frequency_label'] = 'How often?'
updates_page_config['week_label'] = 'Week'
updates_page_config['day_label'] = 'Day'
updates_page_config['time_label'] = 'Time'
updates_page_config['save_button_label'] = 'Save'
updates_page_config['download_logs_label'] = 'Download full logs'
updates_page_config['show_sidebar'] = True
updates_page_config['show_restart_steps'] = True
updates_page_config['restart_step_id'] = 'install'
updates_page_config['restart_step_label'] = updates_page_config['step2_label']
updates_page_config['content_rows'] = []

content_rows = updates_page_config['content_rows']

row = ContentRow(
    label=updates_page_config['up_to_date_label'],
    widget='badge',
    value_key='up_to_date',
    element_id='up-to-date-badge',
    default_text='Checking...'
)
content_rows.append(row)

row = ContentRow(
    label=updates_page_config['your_version_label'],
    widget='text',
    value_key='current_version',
    is_copyable=True,
    copy_id='current-version'
)
content_rows.append(row)

row = ContentRow(
    label=updates_page_config['latest_version_label'],
    widget='text',
    value_key='latest_version',
    is_copyable=True,
    copy_id='latest-version',
    spinner=True
)
content_rows.append(row)

grafana_cloud_page_config = {}
grafana_cloud_page_config['title'] = 'Grafana Cloud'
grafana_cloud_page_config['api_prefix'] = '/zato/monitoring/grafana-cloud/'
grafana_cloud_page_config['step1_label'] = 'Configuring Grafana Cloud'
grafana_cloud_page_config['step2_label'] = 'Connect'
grafana_cloud_page_config['check_button_label'] = 'Test connection'
grafana_cloud_page_config['action_button_label'] = 'Save'
grafana_cloud_page_config['version_section_title'] = 'Grafana Cloud'
grafana_cloud_page_config['config_section_title'] = 'Config'
grafana_cloud_page_config['logs_section_title'] = 'Connection log'
grafana_cloud_page_config['up_to_date_label'] = 'Connected?'
grafana_cloud_page_config['your_version_label'] = 'Instance ID'
grafana_cloud_page_config['api_key_label'] = 'API key'
grafana_cloud_page_config['endpoint_label'] = 'Endpoint'
grafana_cloud_page_config['auto_update_label'] = 'Auto-connect'
grafana_cloud_page_config['frequency_label'] = 'How often?'
grafana_cloud_page_config['week_label'] = 'Week'
grafana_cloud_page_config['day_label'] = 'Day'
grafana_cloud_page_config['time_label'] = 'Time'
grafana_cloud_page_config['save_button_label'] = 'Save'
grafana_cloud_page_config['download_logs_label'] = 'Download full logs'
grafana_cloud_page_config['show_sidebar'] = False
grafana_cloud_page_config['show_restart_steps'] = True
grafana_cloud_page_config['panel_width'] = '45%'
grafana_cloud_page_config['restart_step_id'] = 'connect'
grafana_cloud_page_config['restart_step_label'] = grafana_cloud_page_config['step2_label']
grafana_cloud_page_config['content_rows'] = []

content_rows = grafana_cloud_page_config['content_rows']

row = ContentRow(
    label='Is enabled',
    widget='toggle',
    value_key='is_enabled',
    element_id='is-enabled'
)
content_rows.append(row)

row = ContentRow(
    label=grafana_cloud_page_config['your_version_label'],
    widget='input',
    value_key='instance_id',
    is_copyable=True,
    copy_id='instance-id'
)
content_rows.append(row)

row = ContentRow(
    label=grafana_cloud_page_config['api_key_label'],
    widget='input',
    value_key='api_key',
    is_copyable=True,
    copy_id='api-key',
    spinner=False
)
content_rows.append(row)

datadog_page_config = {}
datadog_page_config['title'] = 'Datadog'
datadog_page_config['api_prefix'] = '/zato/monitoring/datadog/'
datadog_page_config['step1_label'] = 'Configuring Datadog'
datadog_page_config['step2_label'] = 'Connect'
datadog_page_config['check_button_label'] = 'Test connection'
datadog_page_config['action_button_label'] = 'Save'
datadog_page_config['version_section_title'] = 'Datadog'
datadog_page_config['config_section_title'] = 'Config'
datadog_page_config['logs_section_title'] = 'Connection log'
datadog_page_config['save_button_label'] = 'Save'
datadog_page_config['download_logs_label'] = 'Download full logs'
datadog_page_config['show_sidebar'] = False
datadog_page_config['show_restart_steps'] = True
datadog_page_config['panel_width'] = '45%'
datadog_page_config['restart_step_id'] = 'connect'
datadog_page_config['restart_step_label'] = datadog_page_config['step2_label']
datadog_page_config['content_rows'] = []

content_rows = datadog_page_config['content_rows']

row = ContentRow(
    label='Is enabled',
    widget='toggle',
    value_key='is_enabled',
    element_id='is-enabled'
)
content_rows.append(row)

row = ContentRow(
    label='Main agent',
    widget='input',
    value_key='main_agent',
    is_copyable=True,
    copy_id='main-agent'
)
content_rows.append(row)

row = ContentRow(
    label='Metrics agent',
    widget='input',
    value_key='metrics_agent',
    is_copyable=True,
    copy_id='metrics-agent',
    spinner=False
)
content_rows.append(row)

python_packages_page_config = {}
python_packages_page_config['title'] = 'Install Python packages'
python_packages_page_config['api_prefix'] = '/zato/python-packages/'
python_packages_page_config['step1_label'] = 'Installing packages'
python_packages_page_config['step2_label'] = 'Restart'
python_packages_page_config['check_button_label'] = 'Test'
python_packages_page_config['action_button_label'] = 'Save'
python_packages_page_config['version_section_title'] = 'Install Python packages'
python_packages_page_config['config_section_title'] = 'Config'
python_packages_page_config['logs_section_title'] = 'Installation log'
python_packages_page_config['save_button_label'] = 'Save'
python_packages_page_config['download_logs_label'] = 'Download full logs'
python_packages_page_config['show_sidebar'] = False
python_packages_page_config['show_restart_steps'] = True
python_packages_page_config['panel_width'] = '55%'
python_packages_page_config['restart_step_id'] = 'install'
python_packages_page_config['restart_step_label'] = python_packages_page_config['step2_label']
python_packages_page_config['content_rows'] = []

content_rows = python_packages_page_config['content_rows']

row = ContentRow(
    label='Requirements',
    widget='textarea',
    value_key='requirements',
    element_id='requirements'
)
content_rows.append(row)
