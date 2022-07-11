# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

def populate_environment_from_file(env_path:'str') -> 'None':

    # stdlib
    import os
    from logging import getLogger

    # Reusable
    logger = getLogger('zato')

    if env_path:
        if not os.path.exists(env_path):

            # Reusable
            msg = 'No such path (env. variables) -> %s'

            # We need to use print too because logging may not be configured yet ..
            print(msg % env_path)

            # .. but use logging nevertheless.
            logger.info(msg, env_path)

        else:

            # Zato
            from zato.common.ext.configobj_ import ConfigObj

            env_config = ConfigObj(env_path)
            env = env_config.get('env') or {}

            msg = 'Imported env. variable `%s` from `%s`'

            for key, value in env.items(): # type: ignore
                os.environ[key] = value
                print(msg % (key, env_path))
                logger.info(msg, key, env_path)

# ################################################################################################################################
# ################################################################################################################################
