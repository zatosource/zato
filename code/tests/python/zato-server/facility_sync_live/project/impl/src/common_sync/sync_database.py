# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# oracledb
import oracledb

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.odb.api import SessionWrapper
    from zato.common.typing_ import any_, anydict, anylist, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

class DatabaseSession:
    """ One session out of an outgoing connection's pool and a cursor on its connection. Nothing commits until commit is called.
    """

    def __init__(self, wrapper:'SessionWrapper') -> 'None':
        self.session = wrapper.session()

        sqlalchemy_connection = self.session.connection()
        connection = sqlalchemy_connection.connection
        self.cursor = connection.cursor()

# ################################################################################################################################

    def execute(self, statement:'str', parameters:'anydict') -> 'int':
        """ Runs one statement and returns how many rows it touched.
        """
        self.cursor.execute(statement, parameters)

        out = self.cursor.rowcount
        return out

# ################################################################################################################################

    def fetch_all(self, statement:'str', parameters:'anydict') -> 'dictlist':
        """ The rows one query returns, each as a dict of lower-case column names to values.
        """
        self.cursor.execute(statement, parameters)

        names:'strlist' = []

        for column in self.cursor.description:
            name = column[0]
            name = name.lower()
            names.append(name)

        out:'dictlist' = []

        for row in self.cursor.fetchall():
            pairs = zip(names, row)
            out.append(dict(pairs))

        return out

# ################################################################################################################################

    def fetch_values(self, statement:'str', parameters:'anydict') -> 'anylist':
        """ The first column of every row one query returns.
        """
        self.cursor.execute(statement, parameters)

        out:'anylist' = []

        for row in self.cursor.fetchall():
            out.append(row[0])

        return out

# ################################################################################################################################

    def timestamp(self, value:'any_') -> 'any_':
        """ A datetime bound as a TIMESTAMP.
        """
        out = self.cursor.var(oracledb.DB_TYPE_TIMESTAMP)
        out.setvalue(0, value)

        return out

# ################################################################################################################################

    def call_function(self, name:'str', parameters:'anylist') -> 'int':
        """ Calls a PL/SQL function that returns a NUMBER.
        """
        out = self.cursor.callfunc(name, int, parameters)
        return out

# ################################################################################################################################

    def commit(self) -> 'None':
        self.session.commit()

# ################################################################################################################################

    def rollback(self) -> 'None':
        self.session.rollback()

# ################################################################################################################################

    def close(self) -> 'None':
        self.cursor.close()
        self.session.close()

# ################################################################################################################################
# ################################################################################################################################
