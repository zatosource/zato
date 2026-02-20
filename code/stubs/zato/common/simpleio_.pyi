from typing import Any, TYPE_CHECKING

from zato.simpleio import BoolConfig, Elem, IntConfig, SecretConfig, SIOServerConfig
from zato.common.py23_.past.builtins import basestring, unicode
from zato.common.typing_ import any_
from zato.cy.simpleio import BoolConfig as PyBoolConfig
from zato.cy.simpleio import IntConfig as PyIntConfig
from zato.cy.simpleio import SecretConfig as PySecretConfig
from zato.cy.simpleio import SIOServerConfig as PySIOServerConfig


def get_bytes_to_str_encoding() -> None: ...

def c18n_sio_fs_config(sio_fs_config: Any) -> None: ...

def get_sio_server_config(sio_fs_config: Any) -> None: ...

def drop_sio_elems(elems: any_, *to_drop: any_) -> any_: ...
