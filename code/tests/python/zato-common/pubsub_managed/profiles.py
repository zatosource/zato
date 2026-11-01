# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The limits of the network, the storage and the compute of each managed database service, as the conditions
# of its small instance classes and of the network between the servers and the database.

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.test.pubsub_database import get_db_mode, is_managed_mode, PubSubDBMode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist

    floatlist = list[float]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class StorageTier:

    # The name of the tier in the reports
    name: 'str'

    # The operations per second and the bandwidth that the tier provisions, in megabytes per second
    iops: 'int'
    megabytes_per_second: 'int'

    # The operations per second of a burst at the start of the fault and how long the burst lasts, in seconds,
    # after which the tier drops to its provisioned operations per second
    burst_iops: 'int'
    burst_seconds: 'int'

# ################################################################################################################################

@dataclass(init=False)
class ProfileLimits:

    # How long a connection may stay idle before the network of the service drops it, in seconds
    idle_limit_seconds: 'int'

    # The storage tiers of the small and medium sizes
    storage_tiers: 'list[StorageTier]'

    # The CPUs that a burstable instance class is left with once its CPU credits run out
    baseline_cpus: 'float'

    # How long a failover leaves the endpoint without a database, in seconds
    failover_delays: 'intlist'

    # The round-trip times within one availability zone and across zones, in milliseconds
    round_trip_ms: 'floatlist'

    # How often the credentials of the pub/sub role change, in seconds
    rotation_seconds: 'int'

# ################################################################################################################################
# ################################################################################################################################

def _new_tier(name:'str', iops:'int', megabytes_per_second:'int', burst_iops:'int'=0, burst_seconds:'int'=0) -> 'StorageTier':
    out = StorageTier()
    out.name = name
    out.iops = iops
    out.megabytes_per_second = megabytes_per_second
    out.burst_iops = burst_iops
    out.burst_seconds = burst_seconds
    return out

# ################################################################################################################################

def _get_rds_limits() -> 'ProfileLimits':
    """ Amazon RDS on db.t3.small - a NAT gateway or a load balancer drops idle connections after 350 seconds,
    gp3 provisions 3,000 IOPS and 125 MB/s, a gp2 volume of 100 GiB bursts to 3,000 IOPS and falls back to 300,
    two vCPUs earn credits for 20 percent each, and IAM authentication tokens expire after 15 minutes.
    """
    out = ProfileLimits()
    out.idle_limit_seconds = 350
    out.storage_tiers = [
        _new_tier('gp3', 3000, 125),
        _new_tier('gp2-burst-exhausted', 300, 128, burst_iops=3000, burst_seconds=60),
    ]
    out.baseline_cpus = 0.4
    out.failover_delays = [35, 60, 120]
    out.round_trip_ms = [0.5, 2.0]
    out.rotation_seconds = 60
    return out

# ################################################################################################################################

def _get_azure_limits() -> 'ProfileLimits':
    """ Azure Database for PostgreSQL on Burstable B2s - the load balancer drops idle connections after 4 minutes,
    Premium SSD P10 provisions 500 IOPS and 100 MB/s, P20 2,300 IOPS and 150 MB/s, Premium SSD v2 its baseline
    of 3,000 IOPS and 125 MB/s, two vCores earn credits for 40 percent each, and Entra ID tokens expire after an hour.
    """
    out = ProfileLimits()
    out.idle_limit_seconds = 240
    out.storage_tiers = [
        _new_tier('premium-ssd-p10', 500, 100),
        _new_tier('premium-ssd-p20', 2300, 150),
        _new_tier('premium-ssd-v2', 3000, 125),
    ]
    out.baseline_cpus = 0.8
    out.failover_delays = [60, 120]
    out.round_trip_ms = [1.0, 2.0]
    out.rotation_seconds = 60
    return out

# ################################################################################################################################

_limits = {
    PubSubDBMode.PostgreSQL_RDS: _get_rds_limits(),
    PubSubDBMode.PostgreSQL_Azure: _get_azure_limits(),
}

# ################################################################################################################################

def get_profile_limits() -> 'ProfileLimits':
    """ Returns the limits of the managed mode that Zato_Test_PubSub_DB_Mode selects.
    """
    mode = get_db_mode()
    assert is_managed_mode(mode), f'The managed suites run in a managed mode and the mode is `{mode}`'

    out = _limits[mode]
    return out

# ################################################################################################################################
# ################################################################################################################################
