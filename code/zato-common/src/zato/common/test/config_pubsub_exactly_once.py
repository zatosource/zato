# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from logging import Logger
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:

    base_url = ''
    password = ''
    server_directory = ''
    server_port = 0
    zato_bin = ''

    # The enmasse template of the suite, the values it is rendered with and the variables of the server
    template_path = ''
    placeholders:'strstrdict' = {}
    extra_server_env:'strstrdict' = {}

    # The state of the session, through which the tests stop, kill and start the server
    session_state:'SessionState'
    logger:'Logger'

    publisher_username = ''
    publisher_password = ''

    reader_username = ''
    reader_password = ''

    orders_username = ''
    orders_password = ''

    verifier_username = ''
    verifier_password = ''

# ################################################################################################################################
# ################################################################################################################################
