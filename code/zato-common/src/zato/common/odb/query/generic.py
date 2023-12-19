# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger

# SQLAlchemy
from sqlalchemy import and_, delete, exists, insert, update

# Zato
from zato.common.api import GENERIC, FILE_TRANSFER, NotGiven
from zato.common.odb.model import GenericConn as ModelGenericConn, GenericObject as ModelGenericObject
from zato.common.odb.query import query_wrapper
from zato.common.typing_ import cast_
from zato.common.util.sql import get_dict_with_opaque

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm import Session as SASession
    from zato.common.typing_ import any_, dictlist, strdict, strnone, type_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

_generic_attr_name = GENERIC.ATTR_NAME
ModelGenericObjectTable:'any_' = ModelGenericObject.__table__

# ################################################################################################################################
# ################################################################################################################################

class GenericObjectWrapper:
    """ Wraps access to generic objects.
    """
    type_:'strnone' = None
    subtype:'strnone' = None
    model_class:'type_[ModelGenericObject]' = ModelGenericObject

    def __init__(self, session:'SASession', cluster_id:'int') -> 'None':
        self.session = session
        self.cluster_id = cluster_id

# ################################################################################################################################

    def build_list_item_from_sql_row(self, row:'strdict') -> 'strdict':
        return row

# ################################################################################################################################

    def _build_get_where_query(self, name:'str') -> 'any_':
        return and_(
            self.model_class.name==name,
            self.model_class.type_==self.type_,
            self.model_class.cluster_id==self.cluster_id,
        )

# ################################################################################################################################

    def get(self, name:'str') -> 'any_':

        item = self.session.query(self.model_class).\
            filter(self.model_class.name==name).\
            filter(self.model_class.type_==self.type_).\
            filter(self.model_class.cluster_id==self.cluster_id).\
            first()

        return cast_('any_', get_dict_with_opaque(item) if item else None)

# ################################################################################################################################

    def get_list(self) -> 'dictlist':

        out:'dictlist' = []

        items = self.session.query(self.model_class).\
            filter(self.model_class.type_==self.type_).\
            filter(self.model_class.cluster_id==self.cluster_id)

        if self.subtype:
            items = items.filter(self.model_class.subtype==self.subtype)

        items = items.order_by(self.model_class.name)
        items = items.all()

        for item in items:
            item:'strdict' = get_dict_with_opaque(item)
            item = self.build_list_item_from_sql_row(item)
            out.append(item)

        return out

# ################################################################################################################################

    def exists(self, name:'str') -> 'bool':
        """ Returns a boolean flag indicating whether the input name is already stored in the ODB. False otherwise.
        """
        where_query = self._build_get_where_query(name)
        exists_query = exists().where(where_query)

        return cast_('bool', self.session.query(exists_query).\
            scalar())

# ################################################################################################################################

    def create(self, name:'str', opaque:'str') -> 'any_':
        """ Creates a new row for input data.
        """
        result = insert(self.model_class).values(**{
            'name': name,
            'type_': self.type_,
            'subtype': self.subtype,
            'cluster_id': self.cluster_id,
            'creation_time': datetime.utcnow(),
            'last_modified': datetime.utcnow(),
            _generic_attr_name: opaque,
        })
        return result

# ################################################################################################################################

    def update(self, name:'str', opaque:'any_'=NotGiven, *, id:'int'=False) -> 'any_':
        """ Updates an already existing object.
        """
        # Name will be always updated ..
        values = {
            'name': name
        }

        # .. whereas opaque attributes are optional ..
        if opaque is not NotGiven:
            values[_generic_attr_name] = opaque

        # .. build a basic filter for the query ..
        and_filter:'any_' = (
            ModelGenericObjectTable.c.type_==self.type_,
            ModelGenericObjectTable.c.cluster_id==self.cluster_id,
        )

        # .. if we have an ID on input, we update by its value ..
        # .. which will let us do a rename  ..
        if id:
            and_filter = and_filter + (ModelGenericObjectTable.c.id==id,)

        # .. otherwise, match by name ..
        else:
            and_filter = and_filter + (ModelGenericObjectTable.c.name==name,)

        # .. turn the tuple of parameters into an actual filter ..
        and_filter = and_(*and_filter)

        # .. build a query that will update the object ..
        query = update(ModelGenericObjectTable).\
            values(values).\
            where(and_filter)

        # .. and return it to our caller.
        return query

# ################################################################################################################################

    def delete(self, id:'int') -> 'any_':
        """ Creates a new row for input data.
        """
        query = delete(ModelGenericObjectTable).where(ModelGenericObjectTable.c.id==id)
        return query

# ################################################################################################################################

    def store(self, name:'str', opaque:'str') -> 'None':
        """ Inserts new data or updates an already existing row matching the input.
        """
        already_exists = self.exists(name)
        query = self.update(name, opaque) if already_exists else self.create(name, opaque)

        self.session.execute(query)
        self.session.commit()

# ################################################################################################################################
# ################################################################################################################################

class FileTransferWrapper(GenericObjectWrapper):
    type_ = GENERIC.CONNECTION.TYPE.CHANNEL_FILE_TRANSFER

class FTPFileTransferWrapper(FileTransferWrapper):
    subtype = FILE_TRANSFER.SOURCE_TYPE.FTP.id

class SFTPFileTransferWrapper(FileTransferWrapper):
    subtype = FILE_TRANSFER.SOURCE_TYPE.SFTP.id

# ################################################################################################################################
# ################################################################################################################################

class GroupsWrapper(GenericObjectWrapper):

    def build_list_item_from_sql_row(self, row: 'strdict') -> 'strdict':

        out:'strdict' = {}

        out['name'] = row['name']
        out['type'] = row['subtype']
        out['id'] = row['id']

        return out

# ################################################################################################################################
# ################################################################################################################################

@query_wrapper
def connection_list(session:'SASession', cluster_id:'int', type_:'strnone'=None, needs_columns:'bool'=False) -> 'any_':
    """ A list of generic connections by their type.
    """
    q = session.query(ModelGenericConn).\
        filter(ModelGenericConn.cluster_id==cluster_id)

    if type_:
        q = q.filter(ModelGenericConn.type_==type_)

    q = q.order_by(ModelGenericConn.name)

    return q

# ################################################################################################################################
# ################################################################################################################################
