# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.model.file_transfer_ import FileTransferItem
    from zato.server.connection.smb import SMBConnection

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment the hub folders belong to
    Hub_Environment = 'test'

    # The applications each application's files are routed to
    Routes = {
        'plant': ['logistics'],
        'logistics': ['plant'],
        'catalog': ['branch01', 'branch02', 'branch03', 'branch04', 'branch05', 'branch06', 'branch07', 'branch08'],
        'branch01': ['logistics'],
        'branch02': ['logistics'],
        'branch03': ['logistics'],
        'branch04': ['logistics'],
        'branch05': ['logistics'],
        'branch06': ['logistics'],
        'branch07': ['logistics'],
        'branch08': ['logistics'],
    }

    # The suffix of a file the hub writes before it renames it to its final name
    Lock_Suffix = '.lck'

    # The suffix of each file the hub writes
    Out_Suffix = '.hub'

    # The suffix of a file written before it is renamed to its final name, outside the hub
    Temp_Suffix = '.tmp'

    # The prefixes of the connections to the exchange shares and to the partner drop
    Exchange_Prefix = 'exchange.'
    Partner_Prefix  = 'partner.'

    # The label sites, the queue of each and the prefix of each trigger file
    Label_Sites   = 'site-a', 'site-b'
    Label_Queues  = {'site-a': 'DOCKA', 'site-b': 'DOCKB'}
    Label_Prefix  = 'LB'

    # The folders the HR and ERP applications exchange files through, outbound to inbound
    Relay_Targets = {
        'hr-outbound': 'erp-inbound',
        'erp-outbound': 'hr-inbound',
    }

    # The format of the date in the name of each extract, and of the time that makes the name unique
    Extract_Date_Format = '%Y%m%d'
    Extract_Time_Format = '%H%M%S'

# ################################################################################################################################
# ################################################################################################################################

def _write_then_rename(conn:'SMBConnection', directory:'str', name:'str', data:'bytes', temp_suffix:'str') -> 'None':
    """ Writes a file under a temporary name and renames it, so that its reader never sees it partially written.
    """
    temp_path = f'{directory}/{name}{temp_suffix}'
    final_path = f'{directory}/{name}'

    conn.write(data, temp_path)
    conn.move(temp_path, final_path)

# ################################################################################################################################
# ################################################################################################################################

class Route(Service):
    """ Routes each file an application leaves in its outbox to the inboxes of the applications it is meant for.
    """
    name = 'file-exchange.route'

    def handle(self) -> 'None':

        item:'FileTransferItem' = self.request.input
        data = item.data

        # A file without content is rejected, which makes the schedule move it into its quarantine directory ..
        if not data:
            raise Exception(f'File `{item.full_path}` from `{item.conn_name}` has no content')

        # .. otherwise its name says which application wrote it and in which sequence, e.g. 000012.plant ..
        sequence, source_app = item.file_name.split('.')
        conn = self.smb[item.conn_name]

        # .. and it is written to each inbox under a name that keeps those two apart.
        name = f'{source_app}.{sequence}{ModuleCtx.Out_Suffix}'

        for destination in ModuleCtx.Routes[source_app]:
            directory = f'exchange/{ModuleCtx.Hub_Environment}/apps/{destination}/inbox'
            _write_then_rename(conn, directory, name, data, ModuleCtx.Lock_Suffix)

# ################################################################################################################################
# ################################################################################################################################

class Documents(Service):
    """ Stores each document in the archive, in a directory of the date in its name, and hands a copy to the partner.
    """
    name = 'file-exchange.documents'

    def handle(self) -> 'None':

        item:'FileTransferItem' = self.request.input
        data = item.data

        # The name ends with the date and time of the document, e.g. DOC1001-2026-11-17-181500.xml ..
        stem = item.file_name.rsplit('.', 1)[0]
        parts = stem.split('-')
        year, month, day = parts[-4], parts[-3], parts[-2]

        # .. the archive has a directory per day, created when the first document of that day arrives ..
        conn = self.smb[item.conn_name]
        archive_directory = f'archive/{year}/{month}/{day}'

        archive_path = f'{archive_directory}/{item.file_name}'

        conn.create_directory(archive_directory, exist_ok=True)
        conn.write(data, archive_path)

        # .. and the partner receives its copy in its own drop.
        partner_name = item.conn_name.replace(ModuleCtx.Exchange_Prefix, ModuleCtx.Partner_Prefix)
        partner = self.smb[partner_name]

        _write_then_rename(partner, 'partner-drop', item.file_name, data, ModuleCtx.Temp_Suffix)

# ################################################################################################################################
# ################################################################################################################################

class Labels(Service):
    """ Writes a label trigger file for each shipment notice, to the site that ships it.
    """
    name = 'file-exchange.labels'

    def handle(self) -> 'None':

        item:'FileTransferItem' = self.request.input

        # The notice is named after its job number, e.g. SHP1001.txt, and even jobs ship from the first site ..
        stem = item.file_name.rsplit('.', 1)[0]
        job_number = stem[3:]

        site_index = int(job_number) % 2
        site = ModuleCtx.Label_Sites[site_index]
        queue = ModuleCtx.Label_Queues[site]

        # .. and the trigger file names the queue and the job, e.g. LBDOCKA_1001.csv.
        name = f'{ModuleCtx.Label_Prefix}{queue}_{job_number}.csv'
        directory = f'labels/{site}'
        data = item.data
        conn = self.smb[item.conn_name]

        _write_then_rename(conn, directory, name, data, ModuleCtx.Temp_Suffix)

# ################################################################################################################################
# ################################################################################################################################

class LabelFailures(Service):
    """ Receives each trigger file the label printing could not process. The schedule moves it out of the way.
    """
    name = 'file-exchange.label-failures'

    def handle(self) -> 'None':

        item:'FileTransferItem' = self.request.input
        self.logger.info('Label trigger `%s` failed on `%s`', item.full_path, item.conn_name)

# ################################################################################################################################
# ################################################################################################################################

class LandingExtract(Service):
    """ Writes the extract of the previous day to the landing zone. The job that runs it names the connection to use.
    """
    name = 'file-exchange.landing-extract'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request
        conn = self.smb[conn_name]

        now = datetime.now(timezone.utc)
        previous_day = now - timedelta(days=1)

        extract_date = previous_day.strftime(ModuleCtx.Extract_Date_Format)
        extract_time = now.strftime(ModuleCtx.Extract_Time_Format)

        name = f'extract-{extract_date}-{extract_time}.csv'
        text = f'date,source\n{extract_date},{conn_name}\n'
        data = text.encode('utf8')

        _write_then_rename(conn, 'landing/daily', name, data, ModuleCtx.Temp_Suffix)

# ################################################################################################################################
# ################################################################################################################################

class Relay(Service):
    """ Relays each file between the HR and ERP applications, from the outbound folder of one to the inbound folder of the other.
    """
    name = 'file-exchange.relay'

    def handle(self) -> 'None':

        item:'FileTransferItem' = self.request.input

        source_folder = item.directory.rsplit('/', 1)[1]
        target_folder = ModuleCtx.Relay_Targets[source_folder]

        directory = f'people/{target_folder}'
        data = item.data
        conn = self.smb[item.conn_name]

        _write_then_rename(conn, directory, item.file_name, data, ModuleCtx.Temp_Suffix)

# ################################################################################################################################
# ################################################################################################################################
