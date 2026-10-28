# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.test.b2b_perf import new_perf_settings, PerfRun
from zato.common.test.b2b_perf_common import Steady_Rate
from zato.common.test.b2b_perf_results import check_criteria, result_properties

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from perf_db import PerfDatabase
    from zato.common.typing_ import callable_
    callable_ = callable_
    Path = Path
    PerfDatabase = PerfDatabase

# ################################################################################################################################
# ################################################################################################################################

Shape_Request_Response = 'request-response'
Shape_Notification     = 'notification-signal'

# How many requests of the partner and how many notifications of the host start per second in each shape.
_shape_rates = {
    Shape_Request_Response: (Steady_Rate, 0),
    Shape_Notification: (0, Steady_Rate),
}

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('shape', (Shape_Request_Response, Shape_Notification))
def test_steady_load(database:'PerfDatabase', shape:'str', tmp_path:'Path', record_property:'callable_') -> 'None':
    """ Transactions of one shape at the steady rate for the measurement duration meet the criteria of a steady run.
    """
    request_rate, notification_rate = _shape_rates[shape]
    work_dir = str(tmp_path)

    settings = new_perf_settings(work_dir, database.env, request_rate, notification_rate)

    run = PerfRun(settings)
    result = run.run()

    properties = result_properties(result)

    for name, value in properties.items():
        record_property(name, value)

    failures = check_criteria(result)
    assert not failures, failures

# ################################################################################################################################
# ################################################################################################################################
