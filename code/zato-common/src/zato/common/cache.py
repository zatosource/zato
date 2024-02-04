'''
# -*- coding: utf-8 -*-

# stdlib
from time import time

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Cache_Name_Pattern = 'zato.dictholder.{}'

# ################################################################################################################################
# ################################################################################################################################

class InfoResult:

    data: 'any_'
    is_cache_hit: 'bool'
    cache_expiry: 'float'
    cache_hits: 'int' = 0

# ################################################################################################################################
# ################################################################################################################################

class DictHolderConfig:

    name: 'str'
    server: 'ParallelServer'
    on_data_missing_func: 'callable_'
    use_json: 'bool' = False

# ################################################################################################################################
# ################################################################################################################################

class DictHolder:

    def __init__(self, config:'DictHolderConfig'):
        self.name = config.name
        self.server = config.server
        self.on_data_missing_func = config.on_data_missing_func

    def get_all(self) -> 'InfoResult':

        # Local variables
        cache_entry:'any_'

        # Our response to produce
        out = InfoResult()

        # If we have anything in our cache, we can return it immediately ..
        if cache_entry := self._get_entry_from_cache():

            # .. assign the actual value ..
            out.data = cache_entry.value

            # .. indicate that it came from the cache ..
            out.is_cache_hit = True
            out.cache_hits = cache_entry.hits

            # .. build the remaining expiration time, in seconds ..
            # .. rounded down to make sure it does not take too much log space  ..
            expiry:'float' = cache_entry.expires_at - time()
            expiry = round(expiry, 2)

            # .. now, can assign the expiration time ..
            out.cache_expiry = expiry

            # .. and return the result to the caller.
            return out

        # .. we are here if the cache is empty ..
        else:

            # .. since we had nothing in the cache, we need to obtain it from our callback function ..
            data = self.on_data_missing_func()

            # .. then we can cache it ..
            expiry:'float' = self._store_data_in_cache(data)

            # .. build the result ..
            out.data = data
            out.is_cache_hit = False
            out.cache_expiry = expiry

            # .. and now, we can return it to our caller.
            return out

# ################################################################################################################################
# ################################################################################################################################

class MyService(Service):

    def on_key_missing(self) -> 'any_':
        pass

# ################################################################################################################################

    def handle(self) -> 'None':

        config = DictHolderConfig()
        config.name = 'Testing'
        config.server = self.server
        config.on_data_missing_func = self.on_key_missing

        holder = DictHolder(config)
        data = holder.get_all()

        data

# ################################################################################################################################
# ################################################################################################################################
'''
