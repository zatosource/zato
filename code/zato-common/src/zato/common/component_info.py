# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime
from itertools import groupby
from io import StringIO
from operator import attrgetter
from time import time

# psutil
from psutil import Process

# PyYAML
import yaml

# pytz
from pytz import UTC

# Texttable
from texttable import Texttable

# Zato
from zato.common.api import INFO_FORMAT, MISC, ZATO_INFO_FILE
from zato.common.json_internal import dumps as json_dumps, loads as json_loads
from zato.common.util.api import current_host
from zato.common.util.open_ import open_r

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, intlist, stranydict

# ################################################################################################################################
# ################################################################################################################################

def format_connections(conns:'anylist', format:'str') -> 'stranydict':
    """ Formats a list of connections according to the output format.
    """
    groups = (groupby(conns, key=attrgetter('status')))
    out:'stranydict' = {}

    for status, items in groups:
        items = list(items)
        items.sort(key=attrgetter('raddr'))
        out_items = out.setdefault(status, [])

        for item in items:

            laddr_str = ':'.join(str(elem) for elem in item.laddr).ljust(21)
            raddr_str = ':'.join(str(elem) for elem in item.raddr).rjust(21)

            out_item = {
                'from': '{}:{}'.format(*item.laddr),
                'to': None,
                'formatted': None,
            }

            if item.raddr:
                out_item['to'] = '{}:{}'.format(*item.raddr)
                out_item['formatted'] = '{} -> {}'.format(laddr_str, raddr_str)
            else:
                out_item['formatted'] = '{}:{}'.format(*item.laddr)

            out_items.append(out_item)

    return out

def get_info(component_path:'str', format:'str') -> 'stranydict':

    master_proc_pid_file = None

    component_details_file = open_r(os.path.join(component_path, ZATO_INFO_FILE))
    component_details = component_details_file.read()

    out:'stranydict' = {
        'component_details': component_details,
        'component_full_path': component_path,
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
        'master_proc_servers_no': None,
        'master_proc_servers_pids': None,
    }

    master_proc_pid = None
    try:
        master_proc_pid_file = open_r(os.path.join(component_path, MISC.PIDFILE))
        master_proc_pid = int(master_proc_pid_file.read())
    except(IOError, ValueError):
        # Ok, no such file or it is empty
        pass
    finally:
        if master_proc_pid_file:
            master_proc_pid_file.close()

    if master_proc_pid:
        out['component_running'] = True
        master_proc = Process(master_proc_pid)
        server_pids = sorted(elem.pid for elem in master_proc.children())

        now = datetime.fromtimestamp(time(), UTC)
        mater_proc_create_time = master_proc.create_time()
        mater_proc_create_time_utc = datetime.fromtimestamp(mater_proc_create_time, UTC)

        out['mater_proc_uptime'] = now - mater_proc_create_time_utc
        out['mater_proc_uptime_seconds'] = int(out['mater_proc_uptime'].total_seconds())

        out['master_proc_connections'] = format_connections(master_proc.connections(), format)
        out['master_proc_pid'] = master_proc.pid
        out['master_proc_create_time'] = datetime.fromtimestamp(mater_proc_create_time).isoformat()
        out['master_proc_create_time_utc'] = mater_proc_create_time_utc.isoformat()
        out['master_proc_username'] = master_proc.username()
        out['master_proc_name'] = master_proc.name()
        out['master_proc_servers_no'] = len(server_pids)
        out['master_proc_servers_pids'] = server_pids

        for pid in server_pids:
            server_process = Process(pid)

            server_create_time = server_process.create_time()
            server_create_time_utc = datetime.fromtimestamp(server_create_time, UTC)

            out['server_{}_uptime'.format(pid)] = now - server_create_time_utc
            out['server_{}_uptime_seconds'.format(pid)] = int(out['server_{}_uptime'.format(pid)].total_seconds())

            out['server_{}_create_time'.format(pid)] = datetime.fromtimestamp(server_create_time).isoformat()
            out['server_{}_create_time_utc'.format(pid)] = server_create_time_utc.isoformat()
            out['server_{}_connections'.format(pid)] = format_connections(server_process.connections(), format)

    # Final cleanup
    component_details_file.close()

    return out

def format_info(value:'stranydict', format:'str', cols_width:'str'='', dumper:'any_'=None) -> 'any_':
    if format in(INFO_FORMAT.DICT, INFO_FORMAT.JSON, INFO_FORMAT.YAML):
        value['component_details'] = json_loads(value['component_details'])

    if format == INFO_FORMAT.JSON:
        return json_dumps(value)

    elif format == INFO_FORMAT.YAML:
        buff = StringIO()
        yaml.dump_all([value], default_flow_style=False, indent=4, Dumper=dumper, stream=buff)
        out = buff.getvalue()
        buff.close()

        return out

    elif format == INFO_FORMAT.TEXT:

        col_widths:'intlist' = []

        for elem in cols_width.split(','):
            elem = elem.strip()
            col_widths.append(int(elem))

        table = Texttable()
        _ = table.set_cols_width(col_widths)

        # Use text ('t') instead of auto so that boolean values don't get converted into ints
        _ = table.set_cols_dtype(['t', 't'])

        rows:'anylist' = [['Key', 'Value']]
        rows.extend(sorted(value.items()))

        _ = table.add_rows(rows)

        return table.draw()

    else:
        return value
