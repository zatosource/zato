# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Runs one write API in a process of its own, with the native fault library preloaded. The writes that the API needs
# before it run with no fault, the fault is turned on for the directory of the database and the write runs. The process
# reports whether the write raised and ends at once, without closing the database, as a process ends after a failure.

# gevent
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import json
import os
import sys
from time import sleep

sys.path.insert(0, os.path.dirname(__file__))

# Zato
from write_apis import Write_APIs
from zato.common.test.zato_database import file_database_engine

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the fault library takes to read its control file again, in seconds, with a margin
    Control_Reload_Seconds = 0.3

    # Every fsync and fdatasync of a file under the directory fails with EIO, while the writes themselves proceed
    Control_Template = 'prefix={directory}\nerror_percent=100\nerrno=EIO\ncalls=sync\n'

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    name, token, directory, control_path = sys.argv[1:]

    api = Write_APIs[name](token)

    with file_database_engine(directory):
        api.prepare()

        # The fault applies from the next file system call on ..
        with open(control_path, 'w') as control_file:
            _ = control_file.write(ModuleCtx.Control_Template.format(directory=directory))

        sleep(ModuleCtx.Control_Reload_Seconds)

        # .. and the write runs under it.
        try:
            api.write()
        except Exception as e:
            result = {'is_raised': True, 'error': repr(e)}
        else:
            result = {'is_raised': False, 'error': ''}

        print(json.dumps(result), flush=True)

        os._exit(0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
