# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the live explain suite's fixtures and tests share.

# The password the IMAP server requires - a login with any other one is rejected
IMAP_Password = 'imap-live-secret-1'

# ################################################################################################################################
# ################################################################################################################################

class LiveServer:
    """ The quickstart server the REST channel proof runs against - what the fixture decides
    before the server starts and what it fills in once the server answers.
    """

    # Where the server listens and how its admin services are invoked
    host = ''
    server_port = 0
    invoke_password = ''
    server_directory = ''

    # The LLM connection the enmasse document creates - the one the notification config names
    llm_conn_name = 'explain.live.llm'

    # The hot-deployed service every call to which raises, and what it raises with
    raising_service = 'explain.live.always-raise'
    error_text = 'The orders backend is not reachable'

# ################################################################################################################################
# ################################################################################################################################
