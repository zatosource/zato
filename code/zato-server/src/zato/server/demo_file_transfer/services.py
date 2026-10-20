# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The source of the services the file transfer demo deploys from one file in the hot-deployment directory -
# a target service per schedule shape and the feeder that keeps the directories supplied with new files.

# stdlib
from pprint import pformat

# Zato
from zato.server.demo_file_transfer.layout import Feeder_Name, Shape_Invoices, Shape_Orders, Shape_Reports, \
    Shape_Shipments, Target_Services

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dictlist

# ################################################################################################################################
# ################################################################################################################################

# One in this many feeds adds a malformed invoice to each invoices directory
_malformed_every = 5

# ################################################################################################################################
# ################################################################################################################################

_services_source = '''\
# -*- coding: utf-8 -*-

# stdlib
from random import randint
from traceback import format_exc

# Zato
from zato.server.demo_file_transfer.files import build_files, Invoice_Header
from zato.server.service import Service

# ##############################################################################

# Each demo connection the feeder uploads to, with the directory each of its schedules polls
Targets = {targets}

# One in this many feeds adds a malformed invoice to each invoices directory
Malformed_Every = {malformed_every}

# What each connection type is called in the log
Protocols = {{
    'outconn-sftp': 'SFTP',
    'outconn-ftp': 'FTP',
    'outconn-smb': 'SMB',
}}

# ##############################################################################

class DemoInvoices(Service):
    """ Receives each invoice a demo schedule picks up and rejects the malformed ones.
    """
    name = '{invoices_service}'

    def handle(self):

        item = self.request.input
        protocol = Protocols[item.conn_type]

        # A well-formed invoice starts with the expected header ..
        header, _, _ = item.text.partition('\\n')

        # .. anything else fails, which makes the schedule retry the file and then quarantine it.
        if header != Invoice_Header:
            raise Exception('Invoice `%s` from `%s` has an unexpected header `%s`' % (item.file_name, item.conn_name, header))

        self.logger.info('Invoice `%s` received over %s from `%s`', item.file_name, protocol, item.conn_name)

# ##############################################################################

class DemoOrders(Service):
    """ Receives each order a demo schedule picks up once its marker file appears.
    """
    name = '{orders_service}'

    def handle(self):

        item = self.request.input
        protocol = Protocols[item.conn_type]

        self.logger.info('Order `%s` received over %s from `%s`', item.file_name, protocol, item.conn_name)

# ##############################################################################

class DemoShipments(Service):
    """ Receives each shipment a demo schedule claims and picks up.
    """
    name = '{shipments_service}'

    def handle(self):

        item = self.request.input
        protocol = Protocols[item.conn_type]

        self.logger.info('Shipment `%s` received over %s from `%s`', item.file_name, protocol, item.conn_name)

# ##############################################################################

class DemoReports(Service):
    """ Receives each report a demo schedule picks up.
    """
    name = '{reports_service}'

    def handle(self):

        item = self.request.input
        protocol = Protocols[item.conn_type]

        self.logger.info('Report `%s` received over %s from `%s`', item.file_name, protocol, item.conn_name)

# ##############################################################################

class DemoFeed(Service):
    """ Uploads a few new files into each directory of every demo connection.
    """
    name = '{feeder_service}'

    def handle(self):

        with_malformed = randint(1, Malformed_Every) == 1

        for target in Targets:

            facade_name = target['facade']
            conn_name = target['conn_name']
            directories = target['directories']

            # Each target is reached through its own protocol, i.e. self.sftp, self.ftp or self.smb ..
            facade = getattr(self, facade_name)

            # .. one connection that cannot be reached right now does not keep the others from their files.
            try:
                conn = facade[conn_name]

                for shape, directory in directories.items():
                    demo_files = build_files(shape, with_malformed)

                    for demo_file in demo_files:
                        remote_path = directory + '/' + demo_file.name
                        conn.write(data=demo_file.data, remote_path=remote_path)

            except Exception:
                self.logger.warning('Could not feed `%s` -> `%s`', conn_name, format_exc())

# ##############################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

def render_services_source(targets:'dictlist') -> 'str':
    """ The services file, with the targets the feeder uploads to - each one a dict with the facade attribute,
    the connection's name and the directory of each of its schedule shapes.
    """
    targets_source = pformat(targets, sort_dicts=False)

    out = _services_source.format(
        targets=targets_source,
        malformed_every=_malformed_every,
        invoices_service=Target_Services[Shape_Invoices],
        orders_service=Target_Services[Shape_Orders],
        shipments_service=Target_Services[Shape_Shipments],
        reports_service=Target_Services[Shape_Reports],
        feeder_service=Feeder_Name,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
