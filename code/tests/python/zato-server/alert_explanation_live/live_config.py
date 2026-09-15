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

    # Where the server's MLLP listener accepts the messages of the MLLP channel proof - decided before the server starts
    mllp_port = 0

    # The LLM connection the enmasse document creates - the one the notification config names
    llm_conn_name = 'explain.live.llm'

    # Where the alerts are mailed from and to - what the enmasse document gives the server's own sweep job
    # and what each proof invokes the sweep with, so the two deliver alike
    email_from = 'zato@example.com'
    email_to = 'ops@example.com'

    # The hot-deployed service every call to which raises, and what it raises with
    raising_service = 'explain.live.always-raise'
    error_text = 'The orders backend is not reachable'

    # The hot-deployed service that answers every call with a FHIR OperationOutcome on a 500,
    # the issue code it carries and its diagnostics text
    outcome_service = 'explain.live.fhir.outcome'
    outcome_code = 'exception'
    outcome_text = 'The patient registry threw an exception'

    # The hot-deployed service every HL7 message to which fails, so the MLLP channel answers with an AR,
    # and what it fails with
    reject_service = 'explain.live.mllp.reject'
    reject_text = 'The ADT feed handler is not reachable'

    # The hot-deployed service that sends one HL7 message through a named outgoing MLLP connection and reports
    # the code it was acknowledged with - what the outgoing MLLP proof sends its messages through
    mllp_send_service = 'explain.live.mllp.send'

    # The hot-deployed service that asks a named outgoing LLM connection for one completion and reports what came
    # back or the error the provider answered with - what the outgoing LLM proof makes its calls through
    llm_invoke_service = 'explain.live.llm.invoke'

# ################################################################################################################################
# ################################################################################################################################
