# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import OK
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# PyYAML
import yaml

# Zato
from zato.cli.enmasse.importer.delete_targets import generic_sections, http_soap_sections
from zato.common.api import Groups
from zato.common.defaults import default_cluster_id

# Live environment
from live_containers.ready import wait_until
from live_environment.quickstart import Host

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.quickstart import ZatoEnvironment
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The service the suite deploys into the server to read runtime state through
    Runtime_Service      = 'enmasse.delete.live.runtime'
    Runtime_Service_File = 'enmasse_delete_live_runtime.py'

    # The markers the server writes to its log for each pickup import it runs
    Marker_Started   = 'Invoking command'
    Marker_Import    = '--import'
    Marker_Completed = 'Enmasse stderr'

    # What the enmasse output contains when an import ended well and when it did not
    Import_OK    = 'Enmasse OK'
    Import_Error = 'Error during import'

    # The relative location of the server's log
    Log_Path = os.path.join('logs', 'server.log')

# ################################################################################################################################
# ################################################################################################################################

# The list services of the sections that are neither HTTP nor generic, with the request each one takes
_list_services = {
    'security':        ('zato.security.get-list',            {}),
    'groups':          ('zato.groups.get-list',              {'group_type': Groups.Type.API_Clients}),
    'quota_tier':      ('zato.security.tier.get-list',       {}),
    'on_prem_gateway': ('zato.on-prem-gateway.get-list',     {}),
    'scheduler':       ('zato.scheduler.job.get-list',       {}),
    'sql':             ('zato.outgoing.sql.get-list',        {}),
    'email_smtp':      ('zato.email.smtp.get-list',          {}),
    'email_imap':      ('zato.email.imap.get-list',          {}),
    'odoo':            ('zato.outgoing.odoo.get-list',       {}),
    'pubsub_topic':    ('zato.pubsub.topic.get-list',        {}),
    'channel_amqp':    ('zato.channel.amqp.get-list',        {}),
    'outgoing_amqp':   ('zato.outgoing.amqp.get-list',       {}),
    'channel_azure_service_bus':  ('zato.channel.amqp.get-list',  {}),
    'outgoing_azure_service_bus': ('zato.outgoing.amqp.get-list', {}),
}

# The sections listed by the security definition's name rather than by their own
_security_listed = {
    'pubsub_permission':   ('zato.pubsub.permission.get-list',   'name'),
    'pubsub_subscription': ('zato.pubsub.subscription.get-list', 'sec_name'),
}

# The sections no service lists, which the runtime service reads from the ODB for
_runtime_only_sections = ('audit_retention', 'audit_extraction')

# ################################################################################################################################
# ################################################################################################################################

class Pickup:
    """ Places enmasse files in the pickup directory of an environment and waits for the server to import each one.
    """

    def __init__(self, environment:'ZatoEnvironment') -> 'None':
        self.environment = environment
        self.counter = 0
        self.log_path = os.path.join(environment.server_directory, ModuleCtx.Log_Path)

# ################################################################################################################################

    def _read_log(self) -> 'str':
        """ The server's log as it stands, empty before the server has written anything.
        """
        if not os.path.isfile(self.log_path):
            return ''

        with open(self.log_path) as log_file:
            out = log_file.read()

        return out

# ################################################################################################################################

    def _count_markers(self, text:'str') -> 'tuple[int, int]':
        """ How many pickup imports the log says started and how many completed.
        """
        started = 0
        completed = 0

        for line in text.splitlines():
            if ModuleCtx.Marker_Started in line and ModuleCtx.Marker_Import in line:
                started += 1
            elif ModuleCtx.Marker_Completed in line:
                completed += 1

        out = started, completed
        return out

# ################################################################################################################################

    def place(self, label:'str', config:'anydict') -> 'str':
        """ Writes a config under a unique name into the pickup directory, waits for the import the server runs for it
        to complete and returns what the server logged in the meantime.
        """
        self.counter += 1
        file_name = f'enmasse-{self.counter:03}-{label}.yaml'
        path = os.path.join(self.environment.pickup_directory, file_name)

        # What the log held before the file was placed is where the new segment starts ..
        log_before = self._read_log()
        offset = len(log_before)
        _, completed_before = self._count_markers(log_before)

        # .. the file is written in one go ..
        with open(path, 'w') as enmasse_file:
            _ = enmasse_file.write(yaml.safe_dump(config, sort_keys=False))

        # .. and the import has completed once the server reports one more completion and nothing still running.
        def _is_imported() -> 'bool':
            started, completed = self._count_markers(self._read_log())
            out = completed >= completed_before + 1 and started == completed
            return out

        wait_until(_is_imported, f'the import of {file_name}')

        out = self._read_log()[offset:]
        return out

# ################################################################################################################################
# ################################################################################################################################

class Runtime:
    """ Reads runtime state back through the service the suite deployed into the server.
    """

    def __init__(self, client:'AdminClient') -> 'None':
        self.client = client

# ################################################################################################################################

    def is_present(self, section:'str', name:'str', topic:'str'='') -> 'bool':
        """ Whether the server has the object at runtime.
        """
        request = {'section': section, 'name': name, 'topic': topic}
        response = self.client.invoke(ModuleCtx.Runtime_Service, request)

        out = response['is_present']
        return out

# ################################################################################################################################
# ################################################################################################################################

def listed_names(client:'AdminClient', section:'str') -> 'strlist':
    """ The names the server's list service of a section returns - for the pub/sub sections keyed by security,
    the names of the security definitions.
    """
    request:'anydict' = {'cluster_id': default_cluster_id}
    name_field = 'name'

    if section in http_soap_sections:
        service = 'zato.http-soap.get-list'
        connection, transport = http_soap_sections[section]
        request['connection'] = connection
        request['transport'] = transport

    elif section in generic_sections:
        service = 'zato.generic.connection.get-list'
        request['type_'] = generic_sections[section]

    elif section in _security_listed:
        service, name_field = _security_listed[section]

    else:
        service, extra = _list_services[section]
        request.update(extra)

    items, _ = client.get_list(service, **request)

    out = [item[name_field] for item in items]
    return out

# ################################################################################################################################

def is_listed(client:'AdminClient', runtime:'Runtime', section:'str', name:'str') -> 'bool':
    """ Whether the server lists the object of a section - through its list service, or through the runtime service
    for the sections no service lists.
    """
    if section in _runtime_only_sections:
        out = runtime.is_present(section, name)
    else:
        out = name in listed_names(client, section)

    return out

# ################################################################################################################################

def job_names(client:'AdminClient') -> 'strlist':
    """ The names of every scheduler job the server has.
    """
    out = listed_names(client, 'scheduler')
    return out
# ################################################################################################################################

def url_status(environment:'ZatoEnvironment', url_path:'str') -> 'int':
    """ The HTTP status the server returns for a GET request to a URL path.
    """
    url = f'http://{Host}:{environment.server_port}{url_path}'
    request = Request(url, method='GET')

    try:
        with urlopen(request, timeout=10) as response:
            out = response.status
    except HTTPError as error:
        out = error.code

    return out

# ################################################################################################################################

def is_served(environment:'ZatoEnvironment', url_path:'str') -> 'bool':
    """ Whether a GET request to a URL path is answered with HTTP 200.
    """
    out = url_status(environment, url_path) == OK
    return out

# ################################################################################################################################
# ################################################################################################################################
