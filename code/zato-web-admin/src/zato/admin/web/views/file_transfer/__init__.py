# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from zato.admin.web.views.file_transfer.transaction import (
    Index as TransactionIndex,
    transaction_detail,
    transaction_content,
    transaction_activity,
    transaction_tasks,
    transaction_resubmit,
    transaction_reprocess,
)

from zato.admin.web.views.file_transfer.rule import (
    Index as RuleIndex,
    rule_create,
    rule_edit,
    rule_delete,
    rule_reorder,
)

from zato.admin.web.views.file_transfer.doc_type import (
    Index as DocTypeIndex,
    doc_type_create,
    doc_type_edit,
    doc_type_delete,
)

from zato.admin.web.views.file_transfer.activity_log import (
    Index as ActivityLogIndex,
)

from zato.admin.web.views.file_transfer.settings import (
    index as settings_index,
    settings_update,
)

from zato.admin.web.views.file_transfer.pgp_key import (
    Index as PGPKeyIndex,
    pgp_key_import,
    pgp_key_generate,
    pgp_key_edit,
    pgp_key_delete,
)

from zato.admin.web.views.file_transfer.user_status import (
    Index as UserStatusIndex,
    user_status_create,
    user_status_delete,
)

from zato.admin.web.views.file_transfer.pickup_channel import (
    Index as PickupChannelIndex,
    pickup_channel_create,
    pickup_channel_edit,
    pickup_channel_delete,
)

from zato.admin.web.views.file_transfer.submit import (
    Index as SubmitIndex,
    submit_file,
)
