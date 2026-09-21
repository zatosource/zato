# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the alert rules config screen shows of each rule type - the title of each type's row, which cells the row
# carries and how one cell reads on screen, shared by the config view and by the tests reading the tables directly.

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.object_config import field_display
from zato.common.api import Alerting
from zato.common.util.api import pluralize

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# What the config screen calls each type
_type_titles = {
    'rest':          'REST outgoing',
    'soap':          'SOAP outgoing',
    'fhir':          'FHIR outgoing',
    'sql':           'SQL',
    'llm':           'LLM',
    'mcp':           'MCP',
    'microsoft':     'Microsoft cloud',
    'email':         'Email',
    'odoo':          'Odoo',
    'file_transfer': 'File transfer',
    'scheduler':     'Scheduler',
    'channels':      'Channels',
    'mllp_channel':  'MLLP channels',
    'mllp_outgoing': 'MLLP outgoing',
    'common':        'Common',
}

# What the alert rules screen calls the LLM cell - shorter than the tab's label, the column being narrow
_llm_field_name = 'use_llm'
_llm_cell_label = 'LLM'

# The one unit that sits right against its value rather than a space away from it
_percent_unit = '%'

# The five cell slots of each type's row - the columns line up across the rows,
# so a type without a value in some column carries a placeholder there.
_type_cells = {
    'rest':          ['consecutive_failures', 'error_rate', 'window', 'status_codes', 'max_latency', 'dlq_messages', 'queue_depth',
        'use_llm'],
    'soap':          ['consecutive_failures', 'error_rate', 'window', 'status_codes', 'fault_codes', 'max_latency', 'dlq_messages',
        'queue_depth', 'use_llm'],
    'fhir':          ['consecutive_failures', 'error_rate', 'window', 'status_codes', 'outcome_codes', 'max_latency', 'dlq_messages',
        'queue_depth', 'use_llm'],
    'sql':           ['consecutive_failures', 'error_rate', 'window', 'max_query_time', 'use_llm'],
    'llm':           ['consecutive_failures', 'error_rate', 'window', 'status_codes', 'truncations', 'refusals', 'token_budget',
        'warning_latency', 'error_latency', 'use_llm'],
    'mcp':           ['consecutive_failures', 'error_rate', 'window', 'invalid_calls', 'rejections', 'auth_failures',
        'throttled_calls', 'repeat_calls', 'warning_latency', 'error_latency', 'truncations', 'volume_budget', 'max_tools',
        'use_llm'],
    'microsoft':     ['consecutive_failures', 'error_rate', 'window', 'health_alerts', 'max_call_time', 'use_llm'],
    'email':         ['consecutive_failures', 'error_rate', 'window', 'auth_failures', 'use_llm'],
    'odoo':          ['consecutive_failures', 'error_rate', 'window', 'auth_failures', 'max_call_time', 'use_llm'],
    'file_transfer': ['consecutive_failures', 'warning_failures', 'error_failures', 'window', 'test_transfers', 'use_llm',
        'arrival_overdue'],
    'scheduler':     ['error_rate', 'window', 'overdue_multiplier', 'start_delay', 'use_llm'],
    'channels':      ['consecutive_failures', 'error_rate', 'window', 'max_latency', 'use_llm'],
    'mllp_channel':  ['consecutive_failures', 'error_rate', 'window', 'ack_codes', 'max_latency', 'use_llm'],
    'mllp_outgoing': ['consecutive_failures', 'error_rate', 'window', 'ack_codes', 'connection_failures', 'max_latency',
        'dlq_messages', 'queue_depth', 'use_llm'],
    'common':        ['certificate_warning', 'outstanding_backlog', 'feed_silence', None, None],
}

# What a toggle cell's value reads as
_toggle_on_label  = 'On'
_toggle_off_label = 'Off'


# What each cell of the notifications row calls its value
_notification_display = {
    Alerting.Extra_Slack_Webhook:    'Slack webhook',
    Alerting.Extra_Teams_Webhook:    'Teams webhook',
    Alerting.Extra_Webhook_URL:      'Webhook URL',
    Alerting.Extra_Email_Connection: 'Email connection',
    Alerting.Extra_Default_To:       'Email to',
    Alerting.Extra_From:             'Email from',
    Alerting.Extra_Dashboard_URL:    'Dashboard URL',
    Alerting.Extra_LLM_Connection:   'LLM connection',
}

# What a notification cell without a value reads as
_not_set_label = 'Not set'

# ################################################################################################################################

def _format_duration(seconds:'int') -> 'str':
    """ What a duration cell reads as - the count with the largest unit dividing the seconds evenly, e.g. 1 day.
    """
    count, unit_name = config_map.split_duration(seconds)
    out = pluralize(count, unit_name)
    return out

# ################################################################################################################################

def _format_amount(count:'int') -> 'str':
    """ What an amount cell reads as - the count with the largest unit it reaches, e.g. 10 millions or 1.5 millions.
    """
    unit_count, unit_name = config_map.split_amount(count)
    out = pluralize(unit_count, unit_name)
    return out

# ################################################################################################################################

def _format_size(size:'int') -> 'str':
    """ What a size cell reads as - the count with the largest unit it reaches, e.g. 100 megabytes or 1.5 gigabytes.
    """
    unit_count, unit_name = config_map.split_size(size)
    out = pluralize(unit_count, unit_name)
    return out

# ################################################################################################################################

def _build_config_cell(field_name:'str', kind:'str', values:'stranydict') -> 'stranydict | None':
    """ One cell of one type's row - the label, the value in screen units and what
    the cell displays. A field whose rule is gone renders as a placeholder.
    """
    if field_name not in values:
        return None

    label, unit = field_display[field_name]
    value = values[field_name]

    # The suffix sits right after the value, so a unit is set off by a space and a percent sign is not
    if unit == _percent_unit:
        suffix = unit
    elif unit:
        suffix = ' ' + unit
    else:
        suffix = ''

    if field_name == _llm_field_name:
        label = _llm_cell_label

    # Our response to produce
    out = {
        'name': field_name,
        'label': label,
        'suffix': suffix,
    }

    if kind in (config_map.Kind_Toggle, config_map.Kind_Ruleset_Toggle):
        out['kind'] = 'checkbox'
        out['value'] = 'true' if value else 'false'
        out['display'] = _toggle_on_label if value else _toggle_off_label
    elif kind == config_map.Kind_Duration:
        out['kind'] = 'duration'
        out['value'] = value
        out['display'] = _format_duration(value)
    elif kind == config_map.Kind_Amount:
        out['kind'] = 'amount'
        out['value'] = value
        out['display'] = _format_amount(value)
    elif kind == config_map.Kind_Size:
        out['kind'] = 'size'
        out['value'] = value
        out['display'] = _format_size(value)
    elif kind == config_map.Kind_Text:
        out['kind'] = 'text'
        out['value'] = value
        out['display'] = value
    else:
        out['kind'] = 'number'
        out['value'] = value
        out['display'] = f'{value}{suffix}'

    return out

# ################################################################################################################################
# ################################################################################################################################
