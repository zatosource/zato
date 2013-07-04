# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from anyjson import dumps, loads
from datetime import datetime

# psutil
from psutil import Process

# pytz
from pytz import UTC

# Texttable
from texttable import Texttable

# Zato
from zato.cli import ManageCommand, ZATO_INFO_FILE
from zato.common.util import current_host

DEFAULT_COLS_WIDTH = '30,90'

class Info(ManageCommand):
    """ Shows detailed information regarding a chosen Zato component
    """
    opts = [
        {'name':'--json', 'help':'Whether to return the output in JSON', 'action':'store_true'},
        {'name':'--cols_width', 'help':'A list of columns width to use for the table output, default: {}'.format(DEFAULT_COLS_WIDTH)}
    ]
    
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

        master_proc_pid = self._zdaemon_command('status')
        master_proc_pid = master_proc_pid.values()
        if master_proc_pid and master_proc_pid[0]:
            out['component_running'] = True
            master_proc_pid = int(master_proc_pid[0])
            master_proc = Process(master_proc_pid)
            workers_pids = sorted(elem.pid for elem in master_proc.get_children())
            
            out['master_proc_connections'] = master_proc.get_connections()
            out['master_proc_pid'] = master_proc.pid
            out['master_proc_create_time'] = datetime.fromtimestamp(master_proc.create_time).isoformat()
            out['master_proc_create_time_utc'] = datetime.fromtimestamp(master_proc.create_time, UTC).isoformat()
            out['master_proc_username'] = master_proc.username
            out['master_proc_name'] = master_proc.name
            out['master_proc_workers_no'] = len(workers_pids)
            out['master_proc_workers_pids'] = workers_pids
            
            for pid in workers_pids:
                worker = Process(pid)
                out['worker_{}_create_time'.format(pid)] = datetime.fromtimestamp(worker.create_time).isoformat()
                out['worker_{}_create_time_utc'.format(pid)] = datetime.fromtimestamp(worker.create_time, UTC).isoformat()
                out['worker_{}_connections'.format(pid)] = worker.get_connections()
            
        if getattr(args, 'json', False):
            out['component_details'] = loads(out['component_details'])
            self.logger.info(dumps(out))
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
