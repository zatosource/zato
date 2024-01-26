# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.api import SCHEDULER

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import list_, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

pubsub_cleanup_job = SCHEDULER.PubSubCleanupJob

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SchedulerCredentials:
    username:'str'
    password:'str'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PathAction:
    path:'str'
    action:'str'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _BaseConfig:
    host:'str'
    port:'int'
    use_tls:'bool'
    verify_tls:'bool'

@dataclass(init=False)
class ServerSchedulerConfig(_BaseConfig):
    username:'str'
    password:'str'

@dataclass(init=False)
class SchedulerConfig(_BaseConfig):
    bind_host:'str'
    bind_port:'int'
    tls_version:'str'
    tls_version:'str'
    tls_ciphers:'str'
    priv_key_location:'str'
    pub_key_location:'str'
    cert_location:'str'
    ca_certs_location:'str'
    api_user_list:'list_[SchedulerCredentials]'
    config_action_user_list:'list_[SchedulerCredentials]'

# ################################################################################################################################
# ################################################################################################################################

startup_jobs=f"""
[zato.outgoing.sql.auto-ping]
minutes=3
service=zato.outgoing.sql.auto-ping

[zato.wsx.cleanup]
minutes=30
service=pub.zato.channel.web-socket.cleanup-wsx

[{pubsub_cleanup_job}]
minutes=60
service=zato.pubsub.cleanup-service
extra=
""".lstrip()

# ################################################################################################################################
# ################################################################################################################################

def get_startup_job_services() -> 'strlist':

    # Zato
    from zato.common.util.api import get_config_from_string

    config = get_config_from_string(startup_jobs)
    return sorted(value.service for value in config.values())

# ################################################################################################################################
# ################################################################################################################################

def get_server_scheduler_config(fs_config:'strdict') -> 'ServerSchedulerConfig':

    # Our response to produce
    out = ServerSchedulerConfig()
    return out

# ################################################################################################################################
# ################################################################################################################################
