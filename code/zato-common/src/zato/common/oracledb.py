# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from importlib import import_module

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, anylistnone, intnone

# ################################################################################################################################
# ################################################################################################################################

# The driver of Oracle, which the cursor of a parameter belongs to, so it is imported by the time a parameter is bound
_oracledb_module_name = 'oracledb'

# ################################################################################################################################
# ################################################################################################################################

def _get_oracledb() -> 'any_':
    out = import_module(_oracledb_module_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

class OracleParam:

    is_out = False

    def __init__(self, value=None, size=None):
        self.value = value
        self.size = size
        self.var = None

    def bind(self, cursor):
        raise NotImplementedError('Subclasses must implement bind()')

    def get(self):
        if self.var is not None:
            return self.var.getvalue()
        return self.value

# ################################################################################################################################
# ################################################################################################################################

class NumberIn(OracleParam):
    def bind(self, cursor):
        self.var = cursor.var(_get_oracledb().NUMBER)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class StringIn(OracleParam):
    def bind(self, cursor):
        size = self.size or 200
        self.var = cursor.var(_get_oracledb().STRING, size)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class FixedCharIn(OracleParam):
    def bind(self, cursor):
        size = self.size or 200
        self.var = cursor.var(_get_oracledb().FIXED_CHAR, size)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class DateTimeIn(OracleParam):
    def bind(self, cursor):
        self.var = cursor.var(_get_oracledb().DATETIME)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class BlobIn(OracleParam):
    def bind(self, cursor):
        self.var = cursor.var(_get_oracledb().BLOB)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class ClobIn(OracleParam):
    def bind(self, cursor):
        self.var = cursor.var(_get_oracledb().CLOB)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

# ################################################################################################################################
# ################################################################################################################################

class _OutBase(OracleParam):
    is_out = True

class NumberOut(_OutBase):

    def bind(self, cursor):
        self.var = cursor.var(_get_oracledb().NUMBER)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class StringOut(_OutBase):
    def bind(self, cursor):
        size = self.size or 200
        self.var = cursor.var(_get_oracledb().STRING, size)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class FixedCharOut(_OutBase):
    def bind(self, cursor):
        size = self.size or 200
        self.var = cursor.var(_get_oracledb().FIXED_CHAR, size)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class DateTimeOut(_OutBase):
    def bind(self, cursor):
        self.var = cursor.var(_get_oracledb().DATETIME)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class BlobOut(_OutBase):
    def bind(self, cursor):
        self.var = cursor.var(_get_oracledb().BLOB)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class ClobOut(_OutBase):
    def bind(self, cursor):
        self.var = cursor.var(_get_oracledb().CLOB)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class RowsOut(_OutBase):
    """ A REF CURSOR parameter - once fetched, its rows are a list of dicts, one per row.
    """
    def __init__(self, value:'any_'=None, size:'intnone'=None) -> 'None':
        super().__init__(value, size)
        self.rows:'anylistnone' = None

    def bind(self, cursor:'any_') -> 'any_':
        self.var = cursor.var(_get_oracledb().CURSOR)
        return self.var

    def fetch(self) -> 'anylist':
        """ Reads all the rows out of the cursor while its connection is still checked out.
        Column names follow what SQLAlchemy does with Oracle - an all-uppercase name,
        which is what an unquoted identifier becomes, is returned in lowercase.
        """
        cursor = self.var.getvalue()
        column_names = [_normalize_column_name(elem[0]) for elem in cursor.description]
        self.rows = [dict(zip(column_names, row)) for row in cursor]
        return self.rows

    def get(self) -> 'any_':

        # The cursor was read in full by the call that produced it ..
        if self.rows is not None:
            return self.rows

        # .. otherwise there is only the cursor itself to hand over.
        return super().get()

# ################################################################################################################################
# ################################################################################################################################

def _normalize_column_name(name:'str') -> 'str':
    if name.isupper():
        return name.lower()
    return name

# ################################################################################################################################
# ################################################################################################################################
