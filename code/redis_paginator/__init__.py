# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under the BSD 3-clause license, see LICENSE.txt for terms and conditions.
"""

#
# * Django-like Redis pagination - a drop-in replacement except for the __init__ method.
#
# * Originally part of Zato - ESB, SOA and cloud integrations in Python https://zato.io
#

# Django
from django.core.paginator import Paginator

# ##############################################################################    

class _ListObjectList(object):
    """ List-backed list of results to paginate.
    """
    def __init__(self, conn, key, *ignored):
        self.conn = conn
        self.key = key
        
    def __getslice__(self, start, stop):
        return self.conn.lrange(self.key, start, stop-1)
        
    def count(self):
        return self.conn.llen(self.key)
    
class _ZSetObjectList(object):
    """ Sorted set-backed list of results to paginate.
    """
    def __init__(self, conn, key, score_min, score_max):
        self.conn = conn
        self.key = key
        self.score_min = score_min
        self.score_max = score_max
        self._use_zrangebyscore = score_min != '-inf' or score_max != '+inf'
        self._zrangebyscore_results = None
        
    def _get_zrangebyscore(self):
        if not self._zrangebyscore_results:
            self._zrangebyscore_results = self.conn.zrangebyscore(self.key, self.score_min, self.score_max)
        return self._zrangebyscore_results
        
    def __getslice__(self, start, stop):
        if self._use_zrangebyscore:
            return self._get_zrangebyscore()[start:stop]
        else:
            return self.conn.zrange(self.key, start, stop-1)
        
    def count(self):
        if self._use_zrangebyscore:
            return len(self._get_zrangebyscore())
        else:
            return self.conn.zcard(self.key)

# ##############################################################################    
    
_source_type_object_list = {
    'list': _ListObjectList,
    'zset': _ZSetObjectList,
}

class RedisPaginator(Paginator):
    """ A subclass of Django's paginator that can paginate results kept in Redis. 
    
    Data in Redis can be 
    
    1) a list,
    2) sorted set or
    3) a range of a sorted set's members with a score between min and max.
    
    For 1) and 2) data won't be fetched prior to pagination
    
    For 3) however the whole subset as specified by score_min and score_max will be fetched
           locally the first time it's needed and any changes in Redis won't be reflected
           in the paginator until a new one is created. This is needed because ZRANGEBYSCORE
           doesn't provide means to learn how many results there are without first fetching
           them so even though the command has a 'LIMIT offset count' parameter, it cannot
           be used here.
    
    conn - a connection handle to Redis (subclass of such as redis.StrictRedis)
    key - Redis key where data is stored
    per_page - how many results per page to return
    orphans - as in Django
    allow_empty_first_page - as in Django
    score_min - (ignored if key is not a list) 'min' parameter to ZRANGEBYSCORE, defaults to '-inf'
    score_max - (ignored if key is not a list) 'max' parameter to ZRANGEBYSCORE, defaults to '+inf'
    source_type - must be either 'list' or 'zset' to indicate what datatype is kept under given key
    """
    def __init__(self, conn, key, per_page, orphans=0, allow_empty_first_page=True, score_min='-inf', score_max='+inf', source_type=None):
        object_list_class = _source_type_object_list[source_type]
        object_list = object_list_class(conn, key, score_min, score_max)
        super(RedisPaginator, self).__init__(object_list, per_page, orphans, allow_empty_first_page)
        
# ##############################################################################    
        
class ListPaginator(RedisPaginator):
    """ A paginator for Redis list. See parent class's docstring for details.
    """
    def __init__(self, *args, **kwargs):
        kwargs['source_type'] = 'list'
        super(ListPaginator, self).__init__(*args, **kwargs)
        
class ZSetPaginator(RedisPaginator):
    """ A paginator for Redis sorted sets. See parent class's docstring for details.
    """
    def __init__(self, *args, **kwargs):
        kwargs['source_type'] = 'zset'
        super(ZSetPaginator, self).__init__(*args, **kwargs)
