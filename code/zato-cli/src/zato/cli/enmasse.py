# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ManageCommand

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dictlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    class Include_Type:
        All  = 'all'
        Cache = 'cache'
        LDAP = 'ldap'
        Microsoft_365 = 'cloud-microsoft-365'
        SQL  = 'sql'
        PubSub = 'pubsub'
        REST = 'rest'
        Scheduler = 'scheduler'
        Security = 'security'
        WebSockets = 'websockets'

        # How many seconds to wait for servers to start up
        Initial_Wait_Time = 60 * 60 * 12 # In seconds = 12 hours

        # How many seconds to wait for missing objects
        Missing_Wait_Time = 120

# ################################################################################################################################
# ################################################################################################################################

class Enmasse(ManageCommand):

    opts:'dictlist' = [

        {'name':'--import', 'help':'Import definitions from a local file (excludes --export-*)', 'action':'store_true'},
        {'name':'--export', 'help':'Export server objects to a file', 'action':'store_true'},

        {'name':'--input', 'help':'Path to input file with objects to import'},
        {'name':'--output', 'help':'Path to a file to export data to', 'action':'store'},

        {'name':'--include-type', 'help':'A list of definition types to include in an export', 'action':'store', 'default':'all'},
        {'name':'--include-name', 'help':'Only objects containing any of the names provided will be exported', 'action':'store', 'default':'all'},

        {'name':'--ignore-missing-includes', 'help':'Ignore include files that do not exist', 'action':'store_true'},
        {'name':'--exit-on-missing-file', 'help':'If input file does not exist, exit with status code 0', 'action':'store_true'},

        {'name':'--initial-wait-time', 'help':'How many seconds to initially wait for a server', 'default':ModuleCtx.Initial_Wait_Time},
        {'name':'--missing-wait-time', 'help':'How many seconds to wait for missing objects', 'default':ModuleCtx.Missing_Wait_Time},

        {'name':'--env-file', 'help':'Path to an .ini file with environment variables'},

        {'name':'--replace', 'help':'Ignored. Kept for backward compatibility', 'action':'store_true'},
        {'name':'--replace-odb-objects', 'help':'Ignored. Kept for backward compatibility', 'action':'store_true'},
        {'name':'--export-odb', 'help':'Same as --export. Kept for backward compatibility', 'action':'store_true'},

        # zato enmasse --import --input=/path/to/input-enmasse.yaml   ~/qs-1/server1     --verbose
        # zato enmasse --export --output /path/to/output-enmasse.yaml ~/env/qs-1/server1 --verbose

        # zato enmasse --export --include-type=cache               --output /path/to/output-enmasse.yaml ~/env/qs-1/server1 --verbose
        # zato enmasse --export --include-type=cloud-microsoft-365 --output /path/to/output-enmasse.yaml ~/env/qs-1/server1 --verbose
    ]

# ################################################################################################################################
# ################################################################################################################################
