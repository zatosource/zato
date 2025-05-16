# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# oracledb
import oracledb as oracledb_impl

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
        self.var = cursor.var(oracledb_impl.NUMBER)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class StringIn(OracleParam):
    def bind(self, cursor):
        size = self.size or 200
        self.var = cursor.var(oracledb_impl.STRING, size)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class FixedCharIn(OracleParam):
    def bind(self, cursor):
        size = self.size or 200
        self.var = cursor.var(oracledb_impl.FIXED_CHAR, size)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class DateTimeIn(OracleParam):
    def bind(self, cursor):
        self.var = cursor.var(oracledb_impl.DATETIME)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class BlobIn(OracleParam):
    def bind(self, cursor):
        self.var = cursor.var(oracledb_impl.BLOB)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class ClobIn(OracleParam):
    def bind(self, cursor):
        self.var = cursor.var(oracledb_impl.CLOB)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

# ################################################################################################################################
# ################################################################################################################################

class _OutBase(OracleParam):
    is_out = True

class NumberOut(_OutBase):

    def bind(self, cursor):
        self.var = cursor.var(oracledb_impl.NUMBER)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class StringOut(_OutBase):
    def bind(self, cursor):
        size = self.size or 200
        self.var = cursor.var(oracledb_impl.STRING, size)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class FixedCharOut(_OutBase):
    def bind(self, cursor):
        size = self.size or 200
        self.var = cursor.var(oracledb_impl.FIXED_CHAR, size)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class DateTimeOut(_OutBase):
    def bind(self, cursor):
        self.var = cursor.var(oracledb_impl.DATETIME)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class BlobOut(_OutBase):
    def bind(self, cursor):
        self.var = cursor.var(oracledb_impl.BLOB)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class ClobOut(_OutBase):
    def bind(self, cursor):
        self.var = cursor.var(oracledb_impl.CLOB)
        if self.value is not None:
            self.var.setvalue(0, self.value)
        return self.var

class RowsOut(_OutBase):
    def bind(self, cursor):
        self.var = cursor.var(oracledb_impl.CURSOR)
        return self.var

# ################################################################################################################################
# ################################################################################################################################
