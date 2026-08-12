# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.alerting.names import get_llm_conn_name, get_notification_conn_name
from zato.common.api import Incidents

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _pytest.monkeypatch import MonkeyPatch
    MonkeyPatch = MonkeyPatch

# ################################################################################################################################
# ################################################################################################################################

class TestConnectionNames:

    def test_the_notification_name_defaults_to_the_constant(self, monkeypatch:'MonkeyPatch') -> 'None':
        monkeypatch.delenv(Incidents.Env_Notification_Conn_Name, raising=False)

        assert get_notification_conn_name() == Incidents.Notification_Conn_Name

# ################################################################################################################################

    def test_the_notification_name_comes_from_the_environment(self, monkeypatch:'MonkeyPatch') -> 'None':
        monkeypatch.setenv(Incidents.Env_Notification_Conn_Name, 'ops.alerts.notifications')

        assert get_notification_conn_name() == 'ops.alerts.notifications'

# ################################################################################################################################

    def test_the_llm_name_defaults_to_the_constant(self, monkeypatch:'MonkeyPatch') -> 'None':
        monkeypatch.delenv(Incidents.Env_LLM_Connection_Name, raising=False)

        assert get_llm_conn_name() == Incidents.LLM_Connection_Name

# ################################################################################################################################

    def test_the_llm_name_comes_from_the_environment(self, monkeypatch:'MonkeyPatch') -> 'None':
        monkeypatch.setenv(Incidents.Env_LLM_Connection_Name, 'ops.alerts.llm')

        assert get_llm_conn_name() == 'ops.alerts.llm'

# ################################################################################################################################
# ################################################################################################################################
