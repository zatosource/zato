from typing import Any, TYPE_CHECKING

from zato.common.typing_ import dataclass
from zato.server.service import Model
from zato.common.typing_ import datetime, dtnone, intnone, stranydict, timedelta


class BearerTokenConfig(Model):
    sec_def_name: str
    username: str
    password: str
    scopes: str
    grant_type: str
    extra_fields: stranydict
    auth_server_url: str
    client_id_field: str
    client_secret_field: str

class BearerTokenInfo(Model):
    creation_time: datetime
    sec_def_name: str
    token: str
    token_type: str
    expires_in: timedelta | None
    expires_in_sec: intnone
    expiration_time: dtnone
    scopes: str
    username: str

class BearerTokenInfoResult(Model):
    info: BearerTokenInfo
    is_cache_hit: bool
    cache_expiry: float
    cache_hits: int
