# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist, strlistnone

# ################################################################################################################################
# ################################################################################################################################

def populate_environment_from_file(env_path:'str', *, to_delete:'strlistnone'=None, use_print:'bool'=True) -> 'strlist':

    # stdlib
    import os
    from logging import getLogger

    # Reusable
    logger = getLogger('zato')

    # Our response to produce
    out:'strlist' = []

    if env_path:
        if not os.path.exists(env_path):

            # Reusable
            msg = 'No such path (env. variables) -> %s'

            # Optionally, we need to use print too because logging may not be configured yet ..
            if use_print:
                # Ignore the default path
                if env_path != '/opt/hot-deploy/enmasse/env.ini':
                    print(msg % env_path)

            # .. but use logging nevertheless.
            logger.info(msg, env_path)

        else:

            # Zato
            from zato.common.ext.configobj_ import ConfigObj

            # Local variables
            to_delete = to_delete or []
            msg_deleted = 'Deleted env. variable `%s`'
            msg_imported = 'Imported env. variable `%s` from `%s`'

            # Build a configuration object with new variables to load ..
            env_config = ConfigObj(env_path)
            env = env_config.get('env') or {}

            # .. delete any previous ones ..
            for key in to_delete:
                _:'any_' = os.environ.pop(key, None)
                logger.info(msg_deleted, key)

            # .. go through everything that is new ..
            for key, value in env.items(): # type: ignore

                # .. make sure values are strings ..
                if isinstance(value, (int, float)):
                    value = str(value)

                # .. do update the environment ..
                os.environ[key] = value

                # .. append the key for our caller's benefit ..
                out.append(key)

                # .. optionally, use print for logging ..
                if use_print:
                    print(msg_imported % (key, env_path))

                # .. but use logging too.
                logger.info(msg_imported, key, env_path)

    # We are ready to return our response now
    return out

# ################################################################################################################################

def get_list_from_environment(key:'str', separator:'str') -> 'strlist':

    # stdlib
    import os

    # Zato
    from zato.common.util.api import make_list_from_string_list

    # Our value to produce
    out = []

    if value := os.environ.get(key):
        value = make_list_from_string_list(value, separator)
        out.extend(value)

    return out

# ################################################################################################################################
# ################################################################################################################################
