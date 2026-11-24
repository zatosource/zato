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
import shutil
import time

# Zato
from checks import check_acknowledgements, check_audit_events, check_publications, check_push_attempts, check_receipts, \
    check_redelivery, check_traffic, DatabaseReader
from workload import ModuleCtx as WorkloadCtx, Workload
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import find_free_port, render_template
from zato.common.test.receiver import WebhookReceiver
from zato.common.test.reliability.power_loss import PowerLossServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.reliability.power_loss.scenario')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the server receives traffic before the loss of power, in seconds
    Traffic_Seconds = 10

    # The enmasse file and the services of the server
    Template_Path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')
    Services_Path = os.path.join(os.path.dirname(__file__), '_services.py')

    # The variable through which zato start receives the directory that the server deploys from each time it starts -
    # the services of its code directory first and then the enmasse files of its enmasse directory.
    Env_Deploy_From = 'Zato_Deploy_From'

    # The directory that the server deploys from, its directories and the enmasse file of the server
    Deploy_Dir_Name    = 'deploy'
    Deploy_Code_Dir    = 'code'
    Deploy_Enmasse_Dir = 'enmasse'
    Enmasse_File_Name  = 'power-loss.yaml'

    # The directory of what the endpoint of the test received
    Push_Dir_Name = 'push-receiver'

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
        WorkloadCtx.Receipt_Reader_Password_Key: 'test.receipt-reader.' + CryptoManager.generate_hex_string(),
        WorkloadCtx.Pusher_Password_Key: 'test.pusher.' + CryptoManager.generate_hex_string(),
        WorkloadCtx.Push_Port_Key: str(find_free_port()),
    }

    enmasse_yaml = render_template(ModuleCtx.Template_Path, placeholders)
    deploy_dir = create_deploy_dir(parent_dir, enmasse_yaml)

    server_env = dict(database_env)
    server_env[ModuleCtx.Env_Deploy_From] = deploy_dir

    # The server imports no definitions before it starts, it imports them from its deployment directory.
    out = PowerLossServer(
        name=name,
        parent_dir=parent_dir,
        template_path=os.devnull,
        placeholders=placeholders,
        hot_deploy_sources=[],
        database_env=server_env,
    )

    return out

# ################################################################################################################################

def create_deploy_dir(parent_dir:'str', enmasse_yaml:'str') -> 'str':
    """ Creates the directory that the server deploys from each time it starts - its services in the code directory
    and its enmasse file in the enmasse directory, which the server imports once the services are deployed.
    """
    out = os.path.join(parent_dir, ModuleCtx.Deploy_Dir_Name)

    code_dir = os.path.join(out, ModuleCtx.Deploy_Code_Dir)
    enmasse_dir = os.path.join(out, ModuleCtx.Deploy_Enmasse_Dir)

    os.makedirs(code_dir)
    os.makedirs(enmasse_dir)

    _ = shutil.copy2(ModuleCtx.Services_Path, code_dir)

    enmasse_path = os.path.join(enmasse_dir, ModuleCtx.Enmasse_File_Name)

    with open(enmasse_path, 'w') as enmasse_file:
        _ = enmasse_file.write(enmasse_yaml)

    return out

# ################################################################################################################################

def run_power_loss(server:'PowerLossServer', power_loss:'PowerLoss', reader:'DatabaseReader') -> 'None':
    """ Runs the traffic against a started server, cuts the power and restores it, and checks what the database holds.
    """
    # The endpoint that the server pushes to runs in the test, so it keeps what it received across the loss of power
    push_port = int(server.placeholders[WorkloadCtx.Push_Port_Key])
    push_dir = os.path.join(server.parent_dir, ModuleCtx.Push_Dir_Name)

    receiver = WebhookReceiver(push_port, push_dir, WorkloadCtx.Push_URL_Path)
    receiver.start()

    try:
        workload = Workload(server.base_url, server.placeholders)
        workload.start()

        time.sleep(ModuleCtx.Traffic_Seconds)

        # The power goes while the clients are still sending, so requests in flight are cut off too ..
        power_loss.cut()
        workload.stop()

        logger.info('Power cut after %d publications, %d acknowledgements, %d receipts, %d pushed publications, ' + \
            '%d push requests and %d audited invocations', len(workload.published), len(workload.acked),
            len(workload.receipts), len(workload.push_published), len(receiver.get_request_records()),
            len(workload.audited_cids))

        check_traffic(workload, receiver)

        # .. it comes back ..
        power_loss.restore()

        # .. everything that was acknowledged is stored, the receipts and the push attempts included ..
        check_publications(workload, reader)
        check_acknowledgements(workload, reader)
        check_receipts(workload, reader)
        check_audit_events(workload, reader)
        check_push_attempts(receiver, reader)

        # .. the queue hands out every publication that was not acknowledged and none that was ..
        workload.drain()
        check_redelivery(workload)

        # .. and every acknowledged publication to the pushed topic reaches the endpoint.
        workload.wait_for_pushes(receiver)

    finally:
        receiver.stop()

# ################################################################################################################################
# ################################################################################################################################
