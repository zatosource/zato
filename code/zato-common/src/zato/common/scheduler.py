# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

startup_jobs="""[zato.stats.process-raw-times]
seconds=90
service=zato.stats.process-raw-times
extra=max_batch_size=99999

[zato.stats.aggregate-by-minute]
seconds=60
service=zato.stats.aggregate-by-minute

[zato.stats.aggregate-by-hour]
minutes=10
service=zato.stats.aggregate-by-hour

[zato.stats.aggregate-by-day]
minutes=60
service=zato.stats.aggregate-by-day

[zato.stats.aggregate-by-month]
minutes=60
service=zato.stats.aggregate-by-month

[zato.stats.summary.create-summary-by-day]
minutes=10
service=zato.stats.summary.create-summary-by-day

[zato.stats.summary.create-summary-by-week]
minutes=10
service=zato.stats.summary.create-summary-by-week

[zato.stats.summary.create-summary-by-month]
minutes=60
service=zato.stats.summary.create-summary-by-month

[zato.stats.summary.create-summary-by-year]
minutes=60
service=zato.stats.summary.create-summary-by-year

[zato.outgoing.sql.auto-ping]
minutes=3
service=zato.outgoing.sql.auto-ping

[zato.wsx.cleanup.pub-sub]
minutes=30
service=pub.zato.channel.web-socket.cleanup-wsx-pub-sub
extra=
is_extra_list=True

[zato.wsx.cleanup]
minutes=30
service=pub.zato.channel.web-socket.cleanup-wsx

[zato.pubsub.cleanup]
minutes=5
service=zato.pubsub.cleanup-service
extra=
"""

def absolutize(path, base=''):
    """ Turns a relative path into an absolute one or returns it as is if it's already absolute.
    """
    import os
    from os.path import isabs

    if not isabs(path):
        path = os.path.expanduser(path)

    if not isabs(path):
        path = os.path.normpath(os.path.join(base, path))

    return path

def _get_config(conf, bunchified, needs_user_config, repo_location=None):
    # type: (bool, bool, str) -> Bunch

    import os
    from bunch import bunchify
    from configobj import ConfigObj

    conf = bunchify(conf) if bunchified else conf

    if needs_user_config:
        conf.user_config_items = {}

        user_config = conf.get('user_config')
        if user_config:
            for name, path in user_config.items():
                path = absolutize(path, repo_location)
                if not os.path.exists(path):
                    logger.warn('User config not found `%s`, name:`%s`', path, name)
                else:
                    user_conf = ConfigObj(path)
                    user_conf = bunchify(user_conf) if bunchified else user_conf
                    conf.user_config_items[name] = user_conf

    return conf

def get_config_from_string(data):
    """ A simplified version of get_config which creates a config object from string, skipping any user-defined config files.
    """
    # type: (str) -> Bunch
    from io import StringIO
    from configobj import ConfigObj

    buff = StringIO()
    buff.write(data)
    buff.seek(0)

    conf = ConfigObj(buff)
    out = _get_config(conf, True, False)

    buff.close()
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_startup_job_services():
    # type: () -> list
    config = get_config_from_string(startup_jobs)
    return sorted(value.service for value in config.values())

# ################################################################################################################################
# ################################################################################################################################
