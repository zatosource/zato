# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.queue_bridge_stand_in import QueueBridgeStandIn

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

    # The variable that names the file to which the service of the Kafka channel appends each message it handles,
    # and the name of the file
    Bridge_Record_Env = 'Zato_Test_Multi_CPU_Bridge_Record'
    Bridge_Record_File = 'bridge-records.txt'

    # The service of the Kafka channel and the service that pings a connection through the queue bridge client of a worker
    Bridge_Record_Service = 'test.multi-cpu.queue-bridge-record'
    Bridge_Ping_Service = 'test.multi-cpu.queue-bridge-ping'

    # The services that open a file transfer run through a worker and that conclude the interrupted runs of a schedule
    Transfer_Open_Service = 'test.multi-cpu.file-transfer-open'
    Transfer_Close_Service = 'test.multi-cpu.file-transfer-close'

    # The root of the deployment, set by the conftest of the suite
    deploy_root = ''

    # The directory into which audit log retention archives the events it deletes, set by the conftest of the suite
    archive_dir = ''

    # The stand-in for the queue bridge, set by the conftest of the suite
    bridge_stand_in:'QueueBridgeStandIn'

# ################################################################################################################################
# ################################################################################################################################
