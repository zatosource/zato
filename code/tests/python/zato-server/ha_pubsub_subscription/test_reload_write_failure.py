# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

# Local
from _support import assert_rows_equal_list, get_msg_ids, publish_accepted, publish_client, pull_all, pull_client, \
    wait_for_no_unconfirmed, wait_for_unconfirmed, yaml_subscription

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_reload_write_failure(
    environment:'any_',
    pickup:'any_',
    runtime:'any_',
    names:'any_',
    write_fault:'any_',
    ) -> 'None':
    """ An enmasse file applied while the writes to the pub/sub database fail leaves its pair pending, the reconciliation
    after the recovery writes its row, and a publication after that reaches the subscriber.
    """
    sub_key = runtime.sub_key(names.security_pull)
    added_pair = (sub_key, names.topic_second.lower())

    # The writes fail while the server applies the file ..
    write_fault.apply()

    pickup.apply('add-second-while-writes-fail', yaml_subscription(names.security_pull, [names.topic_pull, names.topic_second]))
    wait_for_unconfirmed(runtime)

    assert added_pair not in runtime.governed_pairs()

    # .. once they succeed again, the reconciliation writes the row ..
    write_fault.remove()
    wait_for_no_unconfirmed(runtime)

    assert added_pair in runtime.governed_pairs()
    assert_rows_equal_list(runtime)

    # .. and the subscriber receives what is published to the topic added.
    publisher = publish_client(environment, names)
    msg_id = publish_accepted(publisher, names.topic_second, 'reload.' + CryptoManager.generate_hex_string(32))

    subscriber = pull_client(environment, names, names.security_pull)
    messages = pull_all(subscriber)

    assert msg_id in get_msg_ids(messages)

# ################################################################################################################################
# ################################################################################################################################
