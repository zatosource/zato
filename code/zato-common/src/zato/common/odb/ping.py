# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################
# ################################################################################################################################

def get_ping_query(fs_sql_config, engine_params, default_query='select 1+1'):
    """ Returns a ping query for input engine and component-wide SQL configuration.
    """
    ping_query = None
    for key, value in fs_sql_config.items():
        if key == engine_params['engine']:
            ping_query = value.get('ping_query')
            break

    if not ping_query:

        # We special case SQLite because it is never served from sql.ini
        if engine_params['engine'] == 'sqlite':
            ping_query = 'SELECT 1'

        if not ping_query:

            # Use the default one, if we have any ..
            if default_query:
                ping_query = default_query

            # .. otherwise, report an error.
            else:
                raise ValueError('Could not find ping_query for {}'.format(engine_params))

    # If we are here it means that a query was found
    return ping_query

# ################################################################################################################################
# ################################################################################################################################
