# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato raises alerts and sends them out - what happens next lives in Jira,
# ServiceNow or whatever receives the webhook. There is no incidents screen,
# so the URL config must not resolve any incidents path.

# Zato
from zato.admin import urls

# ################################################################################################################################
# ################################################################################################################################

class TestNoIncidentsURLs:

    def test_no_url_name_says_incidents(self) -> 'None':

        for pattern in urls.urlpatterns:

            name = getattr(pattern, 'name', None)

            if name:
                assert 'incident' not in name, name

# ################################################################################################################################

    def test_no_url_path_says_incidents(self) -> 'None':

        for pattern in urls.urlpatterns:
            assert 'incident' not in str(pattern.pattern), str(pattern.pattern)

# ################################################################################################################################

    def test_the_alert_rules_screens_still_resolve(self) -> 'None':

        # The positive control - the config screen the menu points to,
        # its save endpoints and the listing are all still there
        names = []

        for pattern in urls.urlpatterns:

            name = getattr(pattern, 'name', None)

            if name:
                names.append(name)

        assert 'alert-rules' in names
        assert 'alert-rules-config' in names
        assert 'alert-rules-config-save' in names
        assert 'alert-rules-config-notifications-save' in names

# ################################################################################################################################
# ################################################################################################################################
