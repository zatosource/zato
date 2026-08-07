# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from time import sleep

# Zato
from zato.common.util.open_ import open_w
from zato.server.commands import CommandsFacade

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    from zato.server.base.parallel import ParallelServer

    ParallelServer = ParallelServer
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_service_name = 'api.my-service'
_service_file_name = 'api.py'
_config_file_name = 'tutorial-enmasse.yaml'

# Hot deploy picks the file up on its own, so the import waits for the service
# rather than assuming it is there - this is how long it waits.
_wait_steps = 200
_wait_step_seconds = 0.05

# ################################################################################################################################
# ################################################################################################################################

_service_source = '''# -*- coding: utf-8 -*-

# Zato
from zato.server.service import Service

# ##############################################################################

class MyService(Service):
    """ Returns user details by the person's name.
    """
    name = 'api.my-service'

    # I/O definition
    input = '-name'
    output = 'user_type', 'account_no', 'account_balance'

    def handle(self):

        name = self.request.input.name or 'partner'

        # Get data from CRM ..
        crm_conn = self.rest['CRM']
        crm_request = {'UserName':name}
        crm_data = crm_conn.get(self.cid, crm_request).data
        user_type = crm_data['UserType']
        account_no = crm_data['AccountNumber']

        # .. then query Billing ..
        billing_conn = self.out.sql['Billing']
        billing_query = 'SELECT account_balance FROM balance WHERE user_name = :name'
        billing_data = billing_conn.one(billing_query, {'name': name})
        account_balance = billing_data['account_balance']

        self.logger.info(f'cid:{self.cid} Returning user details for {name}')

        # .. and produce the response.
        self.response.payload.user_type = user_type
        self.response.payload.account_no = account_no
        self.response.payload.account_balance = account_balance

# ##############################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

def ensure_tutorial_service(server:'ParallelServer') -> 'bool':
    """ Deploys the tutorial service and waits for it to come up. The file is always written,
    so a rerun replaces an earlier version in place.
    """
    file_path = os.path.join(server.hot_deploy_config.pickup_dir, _service_file_name)

    with open_w(file_path) as f:
        _ = f.write(_service_source)

    steps_left = _wait_steps

    while steps_left:

        if server.service_store.is_deployed(_service_name):
            logger.info('Deployed the tutorial service from %s', file_path)
            return True

        sleep(_wait_step_seconds)
        steps_left -= 1

    logger.warning('The tutorial service did not deploy from %s', file_path)
    return False

# ################################################################################################################################

def import_demo_tutorial(server:'ParallelServer') -> 'stranydict':
    """ Sets up everything the main tutorial builds - the api.my-service service,
    the CRM and Billing connections, the API key, the REST channel and the scheduler job.
    """

    # The channel and the scheduler job name this service, so it goes in first.
    service_deployed = ensure_tutorial_service(server)

    config_path = os.path.join(os.path.dirname(__file__), _config_file_name)

    facade = CommandsFacade()
    facade.init(server)

    result = facade.run_enmasse_sync_import(config_path)

    out = {
        'service_deployed': service_deployed,
        'is_ok': result.is_ok,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
