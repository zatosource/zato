# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queries that a worker sends to every worker through the control channel. The body of a query names
# the query and carries its data, and each worker answers it with the handler registered under that name.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, callable_, dict_

    any_ = any_
    anydict = anydict
    callable_ = callable_

    handlerdict = dict_[str, callable_]

# ################################################################################################################################
# ################################################################################################################################

class QueryName:

    # The runtime state of the worker of each slot
    Worker_Get_List = 'zato.server.worker.get-list'

# ################################################################################################################################
# ################################################################################################################################

class QueryKey:
    Name = 'name'
    Data = 'data'

# ################################################################################################################################
# ################################################################################################################################

def new_query(name:'str', data:'any_') -> 'anydict':
    """ Returns the body of a query of the given name.
    """
    out = {
        QueryKey.Name: name,
        QueryKey.Data: data,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class QueryRouter:
    """ Answers each query that a worker receives with the handler registered under the name of the query.
    """
    def __init__(self) -> 'None':
        self.handlers:'handlerdict' = {}

# ################################################################################################################################

    def register(self, name:'str', handler:'callable_') -> 'None':
        """ Makes the handler answer the queries of the given name, each with the data of the query.
        """
        self.handlers[name] = handler

# ################################################################################################################################

    def on_query(self, body:'anydict') -> 'any_':
        """ Returns the answer of this worker to a query, which the control client sends to the arbiter.
        """
        handler:'callable_' = self.handlers[body[QueryKey.Name]]

        out = handler(body[QueryKey.Data])
        return out

# ################################################################################################################################
# ################################################################################################################################
