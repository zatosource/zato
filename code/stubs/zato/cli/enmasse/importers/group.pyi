from typing import Any, TYPE_CHECKING

from contextlib import closing
import logging
from sqlalchemy import and_, select, delete
from zato.common.api import Groups
from zato.common.odb.model import GenericObject
from zato.common.odb.query.generic import GroupsWrapper
from sqlalchemy.orm.session import Session as SASession
from zato.common.typing_ import any_, anydict, anylist, strlist


class GroupImporter:
    importer: Any
    group_defs: Any
    def __init__(self: Any, importer: Any) -> None: ...
    def get_groups_from_db(self: Any, session: SASession) -> anydict: ...
    def delete_group(self: Any, group_name: Any, group_id: Any, session: SASession) -> None: ...
    def create_group(self: Any, group: anydict, session: SASession) -> any_: ...
    def _resolve_member_names(self: Any, member_names: strlist) -> strlist: ...
    def sync_groups(self: Any, group_list: anylist, session: SASession) -> tuple[anylist, anylist]: ...
