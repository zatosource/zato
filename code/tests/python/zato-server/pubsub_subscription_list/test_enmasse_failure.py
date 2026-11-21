# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_failed_enmasse_import_returns_nonzero(in_process_server:'any_') -> 'None':
    """ An enmasse file whose import fails returns a non-zero exit code.
    """
    server, _push_endpoint = in_process_server

    bad_yaml = f"""
pubsub_topic:
  - name: bad.topic.{CryptoManager.generate_hex_string(8)}
    is_active: not-a-boolean
"""

    exit_code = server.apply_enmasse('failure', bad_yaml)

    assert exit_code != 0

# ################################################################################################################################
# ################################################################################################################################
