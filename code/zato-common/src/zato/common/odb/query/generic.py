# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
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
    from zato.common.typing_ import any_, dictlist, intnone, strdict, strintnone, strnone

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

    def get(self, name:'str', type_:'strnone'=None) -> 'any_':

        # Local variables
        type_ = type_ or self.type_

        item = self.session.query(self.model_class).\
            filter(self.model_class.name==name).\
            filter(self.model_class.type_==type_).\
            filter(self.model_class.cluster_id==self.cluster_id).\
            first()

        return cast_('any_', get_dict_with_opaque(item) if item else None)

# ################################################################################################################################

    def get_list(self, type_:'strnone'=None, subtype:'strnone'=None, *, parent_object_id:'intnone'=None) -> 'dictlist':

        # Local variables
        type_ = type_ or self.type_
        subtype = subtype or self.subtype

        # Our response to produce
        out:'dictlist' = []

        items = self.session.query(self.model_class).\
            filter(self.model_class.type_==type_).\
            filter(self.model_class.cluster_id==self.cluster_id)

        if subtype:
            items = items.filter(self.model_class.subtype==subtype)

        if parent_object_id:
            items = items.filter(self.model_class.parent_object_id==parent_object_id)

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

    def create_many(
        self,
        item_list:'dictlist',
        type_:'strnone'=None,
        subtype:'strnone'=None,
        *,
        parent_object_id:'intnone'=None,
    ) -> 'any_':

        # Local variables
        type_ = type_ or self.type_
        subtype = subtype or self.subtype
        now = datetime.utcnow()

        # Preprocess each item we have on input
        for item in item_list:
            item['type_'] = type_
            item['subtype'] = subtype
            item['parent_object_id'] = parent_object_id
            item['cluster_id'] = self.cluster_id
            item['creation_time'] = now
            item['last_modified'] = now

        result = insert(self.model_class).values(item_list)
        return result

# ################################################################################################################################

    def create(
        self,
        name:'str',
        opaque:'str',
        type_:'strnone'=None,
        subtype:'strnone'=None,
        *,
        parent_object_id:'intnone'=None
    ) -> 'any_':
        """ Creates a row based on the input data.
        """

        item = {
            'name': name,
            _generic_attr_name: opaque,
        }

        result = self.create_many([item], type_, subtype, parent_object_id=parent_object_id)
        return result

# ################################################################################################################################

    def update(self, name:'str', opaque:'any_'=NotGiven, type_:'strnone'=None, *, id:'int'=False) -> 'any_':
        """ Updates an already existing object.
        """

        # Local variables
        type_ = type_ or self.type_

        # Name will be always updated ..
        values = {
            'name': name
        }

        # .. whereas opaque attributes are optional ..
        if opaque is not NotGiven:
            values[_generic_attr_name] = opaque

        # .. build a basic filter for the query ..
        and_filter:'any_' = (
            ModelGenericObjectTable.c.type_==type_,
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

    def delete_by_id(self, id:'int') -> 'any_':
        """ Deletes an existing object by its ID.
        """
        query = delete(ModelGenericObjectTable).where(ModelGenericObjectTable.c.id==id)
        return query

# ################################################################################################################################

    def delete_by_parent_object_id(self, parent_object_id:'int') -> 'any_':
        """ Deletes objects by their parent object's ID.
        """
        query = delete(ModelGenericObjectTable).where(ModelGenericObjectTable.c.parent_object_id==parent_object_id)
        return query

# ################################################################################################################################

    def delete_by_name(self, name:'str', *, parent_object_id:'strintnone'=None) -> 'any_':
        """ Deletes an existing object by its and and, potentially, other attributes.
        """

        # This is always used ..
        criteria = [ModelGenericObjectTable.c.name==name]

        # .. this is optional ..
        if parent_object_id:
            if parent_object_id:
                criteria.append(ModelGenericObjectTable.c.parent_object_id==parent_object_id)

        # .. regardless of what we had, build an 'and' operator of it ..
        criteria = and_(*criteria)

        # .. build a query object now ..
        query = delete(ModelGenericObjectTable).where(criteria)

        # .. and return it to our caller.
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
        out['group_id'] = row['parent_object_id']

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
