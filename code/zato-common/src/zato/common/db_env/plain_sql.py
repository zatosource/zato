# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, CursorResult
    from sqlalchemy.engine.interfaces import Dialect
    from sqlalchemy.sql.compiler import SQLCompiler
    from zato.common.typing_ import any_, anydict, anylist, callable_, strlist

    plain_source_list = list['PlainSource']

# ################################################################################################################################
# ################################################################################################################################

# The most bind parameters that one multi-row insert carries, below the limit of SQLite, which is the lower of the two
_max_insert_parameters = 30_000

# What precedes the expression of the values of an insert in its compiled SQL
_values_keyword = ' VALUES ('

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PlainSource:
    """ Where the value of one positional parameter of a compiled statement comes from.
    """

    # The name of the parameter that the caller gives, or an empty string for a value fixed in the statement
    name: 'str'

    # The position of the value in the list of an expanding parameter, or -1 for a parameter that does not expand
    index: 'int'

    # The position of the value in a tuple of the list of an expanding parameter, or -1 for a list of scalar values
    position: 'int'

    # The value fixed in the statement, already converted for the driver
    constant: 'any_'

    # What converts the value of the caller for the driver, if its type needs a conversion
    processor: 'callable_ | None'

# ################################################################################################################################

@dataclass(init=False)
class PlainPlan:
    """ The SQL of a statement for one database and the sources of its positional parameters.
    """
    sql: 'str'
    sources: 'plain_source_list'

    # The expression of the values of one row of an insert, which a multi-row insert repeats once per row
    values_expr: 'str'

# ################################################################################################################################
# ################################################################################################################################

def _new_source(name:'str', index:'int', constant:'any_', processor:'callable_ | None', position:'int'=-1) -> 'PlainSource':
    out = PlainSource()
    out.name = name
    out.index = index
    out.position = position
    out.constant = constant
    out.processor = processor
    return out

# ################################################################################################################################

def _new_plan(sql:'str', sources:'plain_source_list', values_expr:'str') -> 'PlainPlan':
    out = PlainPlan()
    out.sql = sql
    out.sources = sources
    out.values_expr = values_expr
    return out

# ################################################################################################################################

def _get_values_expr(sql:'str') -> 'str':
    """ Returns the parenthesized expression of the values of a single-row insert, up to its matching parenthesis,
    which also covers the parentheses of the type casts within it.
    """
    start = sql.index(_values_keyword) + len(_values_keyword) - 1
    depth = 0

    for position in range(start, len(sql)):
        char = sql[position]

        if char == '(':
            depth += 1

        elif char == ')':
            depth -= 1
            if depth == 0:
                return sql[start:position + 1]

    raise ValueError(f'Unbalanced parentheses in the values of `{sql}`')

# ################################################################################################################################

def _get_tuple_size(values:'anylist') -> 'int':
    """ Returns the size of the tuples of the values of an expanding parameter, or 0 for a list of scalar values.
    """
    out = 0

    if values:
        first_value = values[0]
        if isinstance(first_value, tuple):
            out = len(first_value)

    return out

# ################################################################################################################################

def _convert(sources:'plain_source_list', parameters:'anydict', out:'anylist') -> 'None':
    """ Appends to a list the values of the positional parameters of one statement or of one row.
    """
    for source in sources:

        # A value fixed in the statement was converted when the statement was compiled ..
        if not source.name:
            out.append(source.constant)
            continue

        # .. while the caller gives each other value, either directly or as one of the values of an expanding parameter.
        value = parameters[source.name]

        if source.index >= 0:
            value = value[source.index]

        # .. a value of a tuple is one of its elements ..
        if source.position >= 0:
            value = value[source.position]

        if source.processor:
            value = source.processor(value)

        out.append(value)

# ################################################################################################################################
# ################################################################################################################################

class PlainStatement:
    """ A SQLAlchemy Core statement that is compiled once per database and per number of the values of its expanding
    parameters, and is then executed as plain SQL through the driver, without the compilation, the cache lookup
    and the parameter processing of SQLAlchemy for each execution. The events of the engine apply to it as to any other
    statement. Only drivers with positional parameters are supported, and the rows that a statement returns
    have the values that the driver gives, without the result processing of SQLAlchemy.
    """

    def __init__(self, statement:'any_') -> 'None':
        self.statement = statement

        # The compiled statement of each database, by the name of its dialect
        self._compiled:'anydict' = {}

        # The names of the expanding parameters of the statement, by the name of the dialect
        self._expanding:'anydict' = {}

        # The plans of the statement, by the dialect name and the numbers of the values of the expanding parameters
        self._plans:'anydict' = {}

# ################################################################################################################################

    def _get_compiled(self, dialect:'Dialect') -> 'SQLCompiler':
        if not (out := self._compiled.get(dialect.name)):
            out = self.statement.compile(dialect=dialect)

            expanding:'strlist' = []
            for bind in out.binds.values():
                if bind.expanding:
                    expanding.append(bind.key)

            self._compiled[dialect.name] = out
            self._expanding[dialect.name] = expanding

        return out

# ################################################################################################################################

    def _new_expanded_plan(self, compiled:'SQLCompiler', parameters:'anydict') -> 'PlainPlan':
        """ Expands the statement for the numbers of values of its expanding parameters that the parameters have.
        """
        # SQLAlchemy replaces the expanding parameters in the dict it receives with their expanded names
        expanded = compiled._process_parameters_for_postcompile(dict(parameters))

        # Each positional parameter of an expanding parameter is one of its values, or one element of one of its tuples,
        # whose positional parameters SQLAlchemy names one after another, tuple by tuple ..
        expansion_of:'anydict' = {}

        for name, expanded_names in expanded.parameter_expansion.items():
            tuple_size = _get_tuple_size(parameters[name])

            for flat_index, expanded_name in enumerate(expanded_names):
                if tuple_size:
                    index, position = divmod(flat_index, tuple_size)
                else:
                    index, position = flat_index, -1
                expansion_of[expanded_name] = (name, index, position)

        sources:'plain_source_list' = []

        for name in cast_('strlist', expanded.positiontup):

            processor = expanded.processors.get(name)

            # .. any other is given by the caller ..
            if name in expansion_of:
                original_name, index, position = expansion_of[name]
                source = _new_source(original_name, index, None, processor, position)

            elif name in parameters:
                source = _new_source(name, -1, None, processor)

            # .. or it is fixed in the statement.
            else:
                constant = compiled.binds[name].value
                if processor:
                    constant = processor(constant)
                source = _new_source('', -1, constant, None)

            sources.append(source)

        out = _new_plan(expanded.statement, sources, '')
        return out

# ################################################################################################################################

    def execute(self, connection:'Connection', parameters:'anydict') -> 'CursorResult[any_]':
        """ Executes the statement with one set of parameters.
        """
        dialect_name = connection.dialect.name
        compiled = self._get_compiled(connection.dialect)

        # The plan depends on how many values each expanding parameter has ..
        key:'anylist' = [dialect_name]

        for name in self._expanding[dialect_name]:
            key.append(len(parameters[name]))

        plan_key = tuple(key)

        if not (plan := self._plans.get(plan_key)):
            plan = self._new_expanded_plan(compiled, parameters)
            self._plans[plan_key] = plan

        # .. and the values follow the order of the positional parameters of the plan.
        values:'anylist' = []
        _convert(plan.sources, parameters, values)

        out = connection.exec_driver_sql(plan.sql, tuple(values))
        return out

# ################################################################################################################################

    def _new_insert_plan(self, dialect:'Dialect', column_keys:'strlist') -> 'PlainPlan':
        """ Compiles an insert of one row with the given columns, for repeating its values once per row.
        """
        compiled = cast_('SQLCompiler', self.statement.compile(dialect=dialect, column_keys=column_keys))

        sources:'plain_source_list' = []

        for name in cast_('strlist', compiled.positiontup):
            processor = compiled._bind_processors.get(name)
            sources.append(_new_source(name, -1, None, processor))

        sql = compiled.string
        values_expr = _get_values_expr(sql)

        out = _new_plan(sql, sources, values_expr)
        return out

# ################################################################################################################################

    def insert_rows(self, connection:'Connection', rows:'anylist') -> 'anylist':
        """ Inserts rows that all have the same keys, with as few multi-row statements as the parameter limit allows,
        and returns the rows that the statements returned.
        """
        dialect = connection.dialect
        column_keys = sorted(rows[0])
        key = (dialect.name, 'insert', tuple(column_keys))

        if not (plan := self._plans.get(key)):
            plan = self._new_insert_plan(dialect, column_keys)
            self._plans[key] = plan

        rows_per_statement = _max_insert_parameters // len(plan.sources)
        single_values = 'VALUES ' + plan.values_expr

        out:'anylist' = []

        for start in range(0, len(rows), rows_per_statement):
            chunk = rows[start:start + rows_per_statement]

            # Each row of the chunk contributes one expression of values ..
            values_exprs:'strlist' = []
            for _ in chunk:
                values_exprs.append(plan.values_expr)

            sql = plan.sql.replace(single_values, 'VALUES ' + ', '.join(values_exprs), 1)

            # .. and its parameters, in the order of the columns of the statement.
            values:'anylist' = []
            for row in chunk:
                _convert(plan.sources, row, values)

            result = connection.exec_driver_sql(sql, tuple(values))

            if result.returns_rows:
                out.extend(result.all())

        return out

# ################################################################################################################################
# ################################################################################################################################
