from importlib import import_module

from redis.backoff import default_backoff
from redis.client import Redis, StrictRedis
from redis.driver_info import DriverInfo
from redis.connection import (
    BlockingConnectionPool,
    Connection,
    ConnectionPool,
    SSLConnection,
    UnixDomainSocketConnection,
)
from redis.credentials import CredentialProvider, UsernamePasswordCredentialProvider
from redis.exceptions import (
    AuthenticationError,
    AuthenticationWrongNumberOfArgsError,
    BusyLoadingError,
    ChildDeadlockedError,
    ConnectionError,
    CrossSlotTransactionError,
    DataError,
    InvalidPipelineStack,
    InvalidResponse,
    MaxConnectionsError,
    OutOfMemoryError,
    PubSubError,
    ReadOnlyError,
    RedisClusterException,
    RedisError,
    ResponseError,
    TimeoutError,
    WatchError,
)
from redis.sentinel import (
    Sentinel,
    SentinelConnectionPool,
    SentinelManagedConnection,
    SentinelManagedSSLConnection,
)
from redis.typing import Subscription
from redis.utils import from_url


def int_or_str(value):
    try:
        return int(value)
    except ValueError:
        return value


__version__ = "8.1.0"

VERSION = tuple(map(int_or_str, __version__.split(".")))


__all__ = [
    "AuthenticationError",
    "AuthenticationWrongNumberOfArgsError",
    "BlockingConnectionPool",
    "BusyLoadingError",
    "ChannelType",
    "ChildDeadlockedError",
    "ClusterKeyspaceNotifications",
    "Connection",
    "ConnectionError",
    "ConnectionPool",
    "CredentialProvider",
    "CrossSlotTransactionError",
    "DataError",
    "DriverInfo",
    "EventType",
    "from_url",
    "default_backoff",
    "InvalidPipelineStack",
    "InvalidResponse",
    "KeyeventChannel",
    "KeyNotification",
    "KeyspaceChannel",
    "KeyspaceNotifications",
    "KeyspaceNotificationsInterface",
    "KeyspaceWorkerThread",
    "SubkeyeventChannel",
    "SubkeyspaceChannel",
    "SubkeyspaceeventChannel",
    "SubkeyspaceitemChannel",
    "get_channel_type",
    "MaxConnectionsError",
    "OutOfMemoryError",
    "PubSubError",
    "ReadOnlyError",
    "Redis",
    "RedisCluster",
    "RedisClusterException",
    "RedisError",
    "ResponseError",
    "Sentinel",
    "SentinelConnectionPool",
    "SentinelManagedConnection",
    "SentinelManagedSSLConnection",
    "SSLConnection",
    "UsernamePasswordCredentialProvider",
    "StrictRedis",
    "Subscription",
    "TimeoutError",
    "UnixDomainSocketConnection",
    "WatchError",
]

# Zato - the asyncio client, the cluster client and the keyspace notifications are imported
# on the first access to them rather than with the package.
_asyncio_module = "redis.asyncio"
_cluster_module = "redis.cluster"
_keyspace_notifications_module = "redis.keyspace_notifications"

_lazy_names = {
    "RedisCluster": _cluster_module,
    "ChannelType": _keyspace_notifications_module,
    "ClusterKeyspaceNotifications": _keyspace_notifications_module,
    "EventType": _keyspace_notifications_module,
    "KeyeventChannel": _keyspace_notifications_module,
    "KeyNotification": _keyspace_notifications_module,
    "KeyspaceChannel": _keyspace_notifications_module,
    "KeyspaceNotifications": _keyspace_notifications_module,
    "KeyspaceNotificationsInterface": _keyspace_notifications_module,
    "KeyspaceWorkerThread": _keyspace_notifications_module,
    "SubkeyeventChannel": _keyspace_notifications_module,
    "SubkeyspaceChannel": _keyspace_notifications_module,
    "SubkeyspaceeventChannel": _keyspace_notifications_module,
    "SubkeyspaceitemChannel": _keyspace_notifications_module,
    "get_channel_type": _keyspace_notifications_module,
}


def __getattr__(name):
    if name == "asyncio":
        return import_module(_asyncio_module)
    if name not in _lazy_names:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(_lazy_names[name])
    value = getattr(module, name)
    globals()[name] = value
    return value
