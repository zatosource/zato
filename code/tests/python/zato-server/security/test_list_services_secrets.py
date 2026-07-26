# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.util.auth import Sec_Def_Secret_Fields
from zato.server.service.internal.security import GetByID, GetList as SecurityGetList
from zato.server.service.internal.security.basic_auth import GetList as BasicAuthGetList
from zato.server.service.internal.security.wss import GetList as WSSGetList

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _get_field_names(service:'any_') -> 'set':
    """ The names the service declares in its output, with the optional marker taken off.
    """
    out = set()

    for item in service.output:
        name = item if isinstance(item, str) else item.name
        out.add(name.lstrip('-'))

    return out

# ################################################################################################################################
# ################################################################################################################################

class ListServicesSecretsTestCase(TestCase):

    def test_no_list_service_returns_a_secret(self):

        for service in (BasicAuthGetList, WSSGetList, SecurityGetList, GetByID):
            field_names = _get_field_names(service)

            for secret_field in Sec_Def_Secret_Fields:
                self.assertNotIn(secret_field, field_names, f'{service.__name__} returns `{secret_field}`')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
