from typing import Any, TYPE_CHECKING



class BrokerConfig:
    protocol: str
    address: str
    vhost: str
    username: str
    password: str
    management_port: int
    def to_url(self: Any) -> str: ...
