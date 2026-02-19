from typing import Any

import itertools
from ipaddress import ip_address, ip_network
from netifaces import AF_INET, ifaddresses as net_ifaddresses, interfaces as net_ifaces
from builtins import bytes
from zato.common.ext.future.moves.urllib.parse import urlparse
from six import PY2

def to_ip_network(adddress: Any) -> None: ...

def ip_list_from_interface(interface: Any, allow_loopback: Any = ...) -> None: ...

def get_preferred_ip(base_bind: Any, user_prefs: Any) -> str: ...
