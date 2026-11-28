# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The membership of a column in a list of values that the caller gives under one parameter name. The condition is
# `column = ANY(CAST(:name AS <type>[]))` and the list is bound as one binary array parameter, so that the statement
# has one text whatever the number of the values.

# stdlib
from functools import partial

# SQLAlchemy
from sqlalchemy import bindparam, Boolean
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.visitors import InternalTraversal
from sqlalchemy.types import UserDefinedType

# zato_pg_wire
from zato_pg_wire.zato_pg_wire import ArrayParameter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine.interfaces import Dialect
    from sqlalchemy.sql.compiler import SQLCompiler
    from sqlalchemy.types import TypeEngine
    from zato.common.typing_ import any_, callable_

    any_ = any_
    callable_ = callable_
    Dialect = Dialect
    SQLCompiler = SQLCompiler
    TypeEngine = TypeEngine

# ################################################################################################################################
# ################################################################################################################################

# The name of the dialect whose statements bind a list as one array parameter
_postgresql = 'postgresql'

# ################################################################################################################################
# ################################################################################################################################

def type_name_of(type_:'TypeEngine[any_]', dialect:'Dialect') -> 'str':
    """ Returns the name of a column type in a database without its length, e.g. VARCHAR for VARCHAR(200).
    """
    compiled = type_.compile(dialect=dialect)
    name, _, _ = compiled.partition('(')

    out = name.strip()
    return out

# ################################################################################################################################
# ################################################################################################################################

class ArrayOf(UserDefinedType[ArrayParameter]):
    """ The type of a parameter whose value is a list, bound as one binary array of elements of the type given.
    """
    cache_ok = True

    def __init__(self, type_name:'str') -> 'None':
        self.type_name = type_name

# ################################################################################################################################

    def get_col_spec(self, **kwargs:'any_') -> 'str':
        out = f'{self.type_name}[]'
        return out

# ################################################################################################################################

    def bind_processor(self, dialect:'Dialect') -> 'callable_':
        out = partial(ArrayParameter, self.type_name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class AnyOf(ColumnElement[bool]):
    """ The condition that a column has one of the values of a list given under a parameter name.
    """
    inherit_cache = True

    _traverse_internals = [
        ('column', InternalTraversal.dp_clauseelement),
        ('name', InternalTraversal.dp_string),
    ]

    type = Boolean()

    # The condition is a predicate already, which a database without a native boolean type does not compare with 1
    _is_implicitly_boolean = True

    def __init__(self, column:'ColumnElement[any_]', name:'str') -> 'None':
        self.column = column
        self.name = name

# ################################################################################################################################
# ################################################################################################################################

@compiles(AnyOf, _postgresql)
def compile_any(element:'AnyOf', compiler:'SQLCompiler', **kwargs:'any_') -> 'str':
    """ Compiles the condition as = ANY of one array parameter, cast to an array of the type of the column.
    """
    type_name = type_name_of(element.column.type, compiler.dialect)
    array_type = ArrayOf(type_name)
    values = bindparam(element.name, type_=array_type)
    column = element.column.self_group()

    column_sql = compiler.process(column, **kwargs)
    values_sql = compiler.process(values, **kwargs)

    out = f'{column_sql} = ANY (CAST({values_sql} AS {type_name}[]))'
    return out

# ################################################################################################################################
# ################################################################################################################################

def any_of(column:'ColumnElement[any_]', name:'str') -> 'AnyOf':
    """ Returns the condition that a column has one of the values of the list given under the parameter name.
    """
    out = AnyOf(column, name)
    return out

# ################################################################################################################################
# ################################################################################################################################
