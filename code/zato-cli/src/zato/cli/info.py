# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from anyjson import dumps as json_dumps, loads as json_loads
from cStringIO import StringIO
from datetime import datetime
from itertools import chain, groupby
from operator import attrgetter, itemgetter

# pyaml
import pyaml

# psutil
from psutil import CONN_LISTEN, Process

# PyYAML
import yaml

# pytz
from pytz import UTC

# Texttable
from texttable import Texttable

# Zato
from zato.cli import ManageCommand, ZATO_INFO_FILE
from zato.common import INFO_FORMAT, MISC
from zato.common.util import current_host

DEFAULT_COLS_WIDTH = '30,90'

class _Dumper(yaml.SafeDumper):
    def represent_none(self, data):
        return self.represent_scalar('tag:yaml.org,2002:null', '')

class Info(ManageCommand):
    """ Shows detailed information regarding a chosen Zato component
    """
    # Changed in 2.0 - --json replaced with --format
    opts = [
        {'name':'--format', 'help':'Output format, must be one of text, json or yaml, default: {}'.format(INFO_FORMAT.TEXT),
           'default':INFO_FORMAT.TEXT},
        {'name':'--cols_width', 'help':'A list of columns width to use for the table output, default: {}'.format(DEFAULT_COLS_WIDTH)}
    ]

    def format_connections(self, conns, format):
        """ Formats a list of connections according to the output format.
        """
        groups = (groupby(conns, key=attrgetter('status')))
        out = {}

        for status, items in groups:
            items = list(items)
            items.sort(key=attrgetter('raddr'))
            out_items = out.setdefault(status, [])
            for item in items:
                laddr_str = ':'.join(str(elem) for elem in item.laddr).ljust(21).decode('utf-8')
                raddr_str = ':'.join(str(elem) for elem in item.raddr).rjust(21).decode('utf-8')
                if item.raddr:
                    out_item = '{} -> {}'.format(laddr_str, raddr_str)
                    out_items.append(out_item)
                else:
                    out_items.append('{}:{}'.format(*item.laddr))

        #print()
        from pprint import pprint
        #pprint(out_items)

        return out

    def _on_server(self, args):

        os.chdir(self.original_dir)
        abs_args_path = os.path.abspath(args.path)
        component_details = open(os.path.join(abs_args_path, ZATO_INFO_FILE)).read()

        out = {
            'component_details': component_details,
            'component_full_path': abs_args_path,
            'component_host': current_host(),
            'component_running': False,
            'current_time': datetime.now().isoformat(),
            'current_time_utc': datetime.utcnow().isoformat(),
            'master_proc_connections': None,
            'master_proc_pid': None,
            'master_proc_name': None,
            'master_proc_create_time': None,
            'master_proc_create_time_utc': None,
            'master_proc_username': None,
            'master_proc_workers_no': None,
            'master_proc_workers_pids': None,
        }

        master_proc_pid = None
        try:
            master_proc_pid = int(open(os.path.join(abs_args_path, MISC.PIDFILE)).read())
        except(IOError, ValueError):
            # Ok, no such file or it's empty
            pass

        if master_proc_pid:
            out['component_running'] = True
            master_proc = Process(master_proc_pid)
            workers_pids = sorted(elem.pid for elem in master_proc.children())

            out['master_proc_connections'] = self.format_connections(master_proc.connections(), self.args.format)
            out['master_proc_pid'] = master_proc.pid
            out['master_proc_create_time'] = datetime.fromtimestamp(master_proc.create_time()).isoformat()
            out['master_proc_create_time_utc'] = datetime.fromtimestamp(master_proc.create_time(), UTC).isoformat()
            out['master_proc_username'] = master_proc.username()
            out['master_proc_name'] = master_proc.name()
            out['master_proc_workers_no'] = len(workers_pids)
            out['master_proc_workers_pids'] = workers_pids

            for pid in workers_pids:
                worker = Process(pid)
                out['worker_{}_create_time'.format(pid)] = datetime.fromtimestamp(worker.create_time()).isoformat()
                out['worker_{}_create_time_utc'.format(pid)] = datetime.fromtimestamp(worker.create_time(), UTC).isoformat()
                out['worker_{}_connections'.format(pid)] = self.format_connections(worker.connections(), self.args.format)

        if(args.format in INFO_FORMAT.JSON, INFO_FORMAT.YAML):
            out['component_details'] = json_loads(out['component_details'])

        if args.format == INFO_FORMAT.JSON:
            self.logger.info(json_dumps(out))

        elif args.format == INFO_FORMAT.YAML:
            buff = StringIO()
            yaml.dump_all([out], default_flow_style=False, indent=4, Dumper=_Dumper, stream=buff)
            value = buff.getvalue()
            buff.close()

            self.logger.info(value)

        else:
            cols_width = args.cols_width if args.cols_width else DEFAULT_COLS_WIDTH
            cols_width = (elem.strip() for elem in cols_width.split(','))
            cols_width = [int(elem) for elem in cols_width]

            table = Texttable()
            table.set_cols_width(cols_width)

            # Use text ('t') instead of auto so that boolean values don't get converted into ints
            table.set_cols_dtype(['t', 't'])

            rows = [['Key', 'Value']]
            rows.extend(sorted(out.items()))

            table.add_rows(rows)

            self.logger.info(table.draw())

    _on_lb = _on_web_admin = _on_server
