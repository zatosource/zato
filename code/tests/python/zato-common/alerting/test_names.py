# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.alerting.names import get_notification_conn_name
from zato.common.api import Alerting

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _pytest.monkeypatch import MonkeyPatch
    MonkeyPatch = MonkeyPatch

# ################################################################################################################################
# ################################################################################################################################

class TestConnectionNames:

    def test_the_notification_name_defaults_to_the_constant(self, monkeypatch:'MonkeyPatch') -> 'None':
        monkeypatch.delenv(Alerting.Env_Notification_Conn_Name, raising=False)

        assert get_notification_conn_name() == Alerting.Notification_Conn_Name

# ################################################################################################################################

    def test_the_notification_name_comes_from_the_environment(self, monkeypatch:'MonkeyPatch') -> 'None':
        monkeypatch.setenv(Alerting.Env_Notification_Conn_Name, 'ops.alerts.notifications')

        assert get_notification_conn_name() == 'ops.alerts.notifications'

# ################################################################################################################################
# ################################################################################################################################
