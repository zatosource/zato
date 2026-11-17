# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The scenario of the power loss tests. A server receives traffic for a while after it started, the storage
# of its database loses its power, and once the storage is back, everything the server acknowledged is checked.

# stdlib
import logging
import os
import time

# Zato
from checks import check_acknowledgements, check_audit_events, check_publications, check_redelivery, check_traffic, \
    DatabaseReader
from workload import ModuleCtx as WorkloadCtx, Workload
from zato.common.crypto.api import CryptoManager
from zato.common.test.durability.power_loss import PowerLossServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.durability.power_loss.scenario')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the server receives traffic before the loss of power, in seconds
    Traffic_Seconds = 10

    # The enmasse file and the services of the server
    Template_Path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')
    Services_Path = os.path.join(os.path.dirname(__file__), '_services.py')

# ################################################################################################################################
# ################################################################################################################################

class PowerLoss:
    """ How the storage of the database of a server loses its power and comes back.
    """

    def cut(self) -> 'None':
        raise NotImplementedError()

    def restore(self) -> 'None':
        raise NotImplementedError()

# ################################################################################################################################
# ################################################################################################################################

def new_server(name:'str', parent_dir:'str', database_env:'strstrdict') -> 'PowerLossServer':
    """ Returns a server of the power loss tests, with new passwords of its users, not yet created.
    """
    placeholders = {
        WorkloadCtx.Publisher_Password_Key: 'test.publisher.' + CryptoManager.generate_hex_string(),
        WorkloadCtx.Puller_Password_Key: 'test.puller.' + CryptoManager.generate_hex_string(),
        WorkloadCtx.Caller_Password_Key: 'test.caller.' + CryptoManager.generate_hex_string(),
    }

    out = PowerLossServer(
        name=name,
        parent_dir=parent_dir,
        template_path=ModuleCtx.Template_Path,
        placeholders=placeholders,
        hot_deploy_sources=[ModuleCtx.Services_Path],
        database_env=database_env,
    )

    return out

# ################################################################################################################################

def run_power_loss(server:'PowerLossServer', power_loss:'PowerLoss', reader:'DatabaseReader') -> 'None':
    """ Runs the traffic against a started server, cuts the power and restores it, and checks what the database holds.
    """
    workload = Workload(server.base_url, server.placeholders)
    workload.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The power goes while the clients are still sending, so requests in flight are cut off too ..
    power_loss.cut()
    workload.stop()

    logger.info('Power cut after %d publications, %d acknowledgements and %d audited invocations',
        len(workload.published), len(workload.acked), len(workload.audited_cids))

    check_traffic(workload)

    # .. it comes back ..
    power_loss.restore()

    # .. everything that was acknowledged is stored ..
    check_publications(workload, reader)
    check_acknowledgements(workload, reader)
    check_audit_events(workload, reader)

    # .. and the queue hands out every publication that was not acknowledged and none that was.
    workload.drain()
    check_redelivery(workload)

# ################################################################################################################################
# ################################################################################################################################
