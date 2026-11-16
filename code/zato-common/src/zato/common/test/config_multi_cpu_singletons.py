# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class SingletonsConfig:
    """ The enmasse file that the server of the suite imports once at startup and the channel that the file defines.
    """

    # The variable that points the start command to the directory with the assets deployed at startup
    Deploy_From_Env = 'Zato_Deploy_From'

    # The directory under the deployment root from which the server imports enmasse files at startup
    Enmasse_Dir = 'enmasse'

    Startup_File_Name = 'enmasse-multi-cpu-startup.yaml'

    Startup_Channel_Name = 'test.multi-cpu.singletons.startup'
    Startup_Channel_Path = '/test/multi-cpu/singletons/startup'

    # How many days audit log retention keeps the events of the REST channels
    Retention_Days = '0'

    # The root of the deployment, set by the conftest of the suite
    deploy_root = ''

    # The directory into which audit log retention archives the events it deletes, set by the conftest of the suite
    archive_dir = ''

# ################################################################################################################################
# ################################################################################################################################
