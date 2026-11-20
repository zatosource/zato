# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import engine_def, engine_def_sqlite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def get_engine_url(args:'any_') -> 'str':
    attrs = {}
    has_get = getattr(args, 'get', False)

    names = ('engine', 'username', 'password', 'host', 'port', 'db_name', 'sqlite_path')

    for name in names:
        if has_get:
            attrs[name] = args.get(name, '')
        else:
            attrs[name] = getattr(args, name, '')

    is_sqlite = attrs['engine'] == 'sqlite'

    # An SQLite path may arrive under either of the two names.
    if is_sqlite:
        db_name = attrs.get('db_name')
        sqlite_path = attrs.get('sqlite_path')

        if db_name:
            attrs['sqlite_path'] = db_name

        if sqlite_path:
            attrs['db_name'] = sqlite_path

    # Pick the URL template for the engine ..
    if is_sqlite:
        template = engine_def_sqlite

    # .. anything else uses the standard host:port template.
    else:
        template = engine_def

    out = template.format(**attrs)
    return out

# ################################################################################################################################
# ################################################################################################################################
