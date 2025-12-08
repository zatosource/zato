# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import str_

from zato.common.monitoring.context import ProcessContext, get_global_metrics
from zato.common.monitoring.metrics import get_global_metrics_store

# ################################################################################################################################
# ################################################################################################################################

def create_context(process_name:'str_', ctx_id:'str_') -> 'ProcessContext':
    """ Create a new process context for metrics operations.
    """
    return ProcessContext(process_name, ctx_id)

def get_metrics_data() -> 'str_':
    """ Get all metrics in Prometheus text format.
    """
    return get_global_metrics_store().get_prometheus_format()

def push_start(process_name:'str_', ctx_id:'str_') -> 'None':
    """ Mark process instance as started (convenience function).
    """
    context = create_context(process_name, ctx_id)
    context.push_timestamp('started')

def push_end(process_name:'str_', ctx_id:'str_', status:'str_' = 'completed') -> 'None':
    """ Mark process instance as ended (convenience function).
    """
    context = create_context(process_name, ctx_id)
    context.push_timestamp('ended')
    context.push('status', 1.0 if status == 'completed' else 0.0)

def incr_global(key:'str_') -> 'None':
    """ Increment global counter.
    """
    get_global_metrics().incr_global(key)

def decr_global(key:'str_') -> 'None':
    """ Decrement global counter.
    """
    get_global_metrics().decr_global(key)

def push_global(key:'str_', value:'float') -> 'None':
    """ Set global metric value.
    """
    get_global_metrics().push_global(key, value)

# ################################################################################################################################
# ################################################################################################################################
