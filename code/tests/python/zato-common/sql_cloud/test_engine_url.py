# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli.enmasse.util import get_engine_from_type, get_type_from_engine, SQL_TYPE_MAP
from zato.common.util.api import get_engine_url

# ################################################################################################################################
# ################################################################################################################################

class TestRedshiftEngineURL:

    def test_redshift_url_shape(self) -> 'None':
        """ Redshift URLs go through the standard host:port template.
        """
        config = {
            'engine': 'redshift+redshift_connector',
            'username': 'test_user',
            'password': 'test_password',
            'host': 'examplecluster.abc123xyz789.us-west-2.redshift.amazonaws.com',
            'port': 5439,
            'db_name': 'testdb',
        }

        url = get_engine_url(config)

        expected = 'redshift+redshift_connector://test_user:test_password' + \
            '@examplecluster.abc123xyz789.us-west-2.redshift.amazonaws.com:5439/testdb'

        assert url == expected

# ################################################################################################################################
# ################################################################################################################################

class TestSQLTypeMap:

    def test_redshift_round_trip(self) -> 'None':
        """ The friendly redshift type maps to the engine name and back.
        """
        engine = get_engine_from_type('redshift')
        assert engine == 'redshift+redshift_connector'

        friendly = get_type_from_engine(engine)
        assert friendly == 'redshift'

# ################################################################################################################################

    def test_engine_names_accepted_directly(self) -> 'None':
        """ Internal engine names pass through unchanged when given directly.
        """
        assert get_engine_from_type('redshift+redshift_connector') == 'redshift+redshift_connector'

# ################################################################################################################################

    def test_type_map_contents(self) -> 'None':
        """ The Redshift engine is present in the type map.
        """
        assert SQL_TYPE_MAP['redshift'] == 'redshift+redshift_connector'

# ################################################################################################################################
# ################################################################################################################################
