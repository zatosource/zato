from typing import Any, TYPE_CHECKING

import os
from dataclasses import dataclass
from datetime import timedelta
from operator import itemgetter
from pathlib import Path
from time import sleep
from zato.common.api import Default_Service_File_Data
from zato.common.exception import BadRequest
from zato.common.typing_ import anylist, intnone, list_field, strnone
from zato.common.util.api import get_demo_py_fs_locations, wait_for_file, utcnow
from zato.common.util.open_ import open_r, open_w
from zato.server.service import Model, Service
from zato.common.typing_ import any_, dictlist, strlistdict


def make_fs_location_url_safe(data: str) -> str: ...

class IDERequest(Model):
    service_name: strnone
    fs_location: strnone
    should_wait_for_services: bool
    should_convert_pickup_to_work_dir: bool

class IDEResponse(Model):
    service_count: intnone
    service_count_human: strnone
    file_count: intnone
    file_count_human: strnone
    current_file_source_code: strnone
    service_list: anylist
    current_file_name: strnone
    current_fs_location: strnone
    current_fs_location_url_safe: strnone
    current_root_directory: strnone
    root_directory_count: intnone
    current_file_service_list: anylist
    current_service_file_list: anylist

class RootDirInfo(Model):
    current_root_directory: strnone
    root_directory_count: intnone

class _IDEBase(Service):
    input: Any
    output: Any
    def _normalize_fs_location(self: Any, fs_location: str) -> str: ...
    def _validate_path(self: Any, orig_path: str) -> None: ...
    def before_handle(self: Any) -> None: ...
    def _get_service_list_by_fs_location(self: Any, deployment_info_list: any_, fs_location: str) -> dictlist: ...
    def _get_all_root_directories(self: Any) -> strlistdict: ...
    def _get_default_root_directory(self: Any, all_root_dirs: strlistdict | None = ...) -> str: ...
    def _get_current_root_dir_info(self: Any, fs_location: str, all_root_dirs: strlistdict | None = ...) -> RootDirInfo: ...
    def get_deployment_info_list(self: Any) -> None: ...
    def _convert_work_to_pickup_dir(self: Any, fs_location: str) -> str: ...
    def _convert_pickup_to_work_dir(self: Any, fs_location: str) -> str: ...
    def _wait_for_services(self: Any, fs_location: str, max_wait_time: int = ...) -> None: ...

class ServiceIDE(_IDEBase):
    def handle(self: Any) -> None: ...

class _GetBase(_IDEBase):
    def _build_get_response(self: Any, deployment_info_list: any_, fs_location: str) -> IDEResponse: ...

class GetService(_GetBase):
    def handle(self: Any) -> None: ...

class GetFile(_GetBase):
    def handle(self: Any) -> None: ...

class GetFileList(_GetBase):
    def handle(self: Any) -> None: ...

class CreateFile(_GetBase):
    input: Any
    output: Any
    def handle(self: Any) -> None: ...

class DeleteFile(_GetBase):
    input: Any
    output: Any
    def _validate_fs_location(self: Any, fs_location: str) -> None: ...
    def handle(self: Any) -> None: ...

class RenameFile(_GetBase):
    input: Any
    output: Any
    def handle(self: Any) -> None: ...
