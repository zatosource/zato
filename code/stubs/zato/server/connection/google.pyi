from typing import Any, TYPE_CHECKING

import os
from logging import getLogger
from pathlib import Path
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from stroll import stroll
from zato.common.typing_ import cast_, list_field
from zato.common.util.file_system import fs_safe_now
from zato.common.typing_ import any_, anylist, stranydict, strnone


class GoogleClient:
    conn: any_
    files: any_
    api_name: Any
    api_version: Any
    user: Any
    scopes: Any
    service_file_dict: Any
    dir_map: stranydict
    _dir_map: Any
    def __init__(self: Any, api_name: str, api_version: str, user: str, scopes: anylist, service_file_dict: str) -> None: ...
    def connect(self: Any) -> any_: ...
    def reset(self: Any) -> None: ...
    def _create_remote_resource(self: Any, name: str, resource_type: str, mime_type: strnone) -> str: ...
    def create_remote_directory(self: Any, name: str) -> str: ...
    def create_remote_file(self: Any, name: str, full_path: str) -> str: ...
    def add_directory(self: Any, new_dir_root: Path, new_dir_root_str: str, item_relative: Path) -> None: ...
    def sync_to_google_drive(self: Any, local_path: str, new_root_name: str, parent_directory_id: str) -> str: ...
