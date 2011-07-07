# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy.orm.query import orm_exc

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.common import ZatoException, ZATO_OK
from zato.common.odb.model import WSSDefinition
from zato.common.util import TRACE1
from zato.server.service.internal import _get_params, AdminService

class GetDefinitionList(AdminService):
    """ Returns a list of WS-Security definitions available.
    """
    def handle(self, *args, **kwargs):
        definition_list = Element("definition_list")

        definitions = self.server.odb.query(WSSDefinition).order_by("name").all()

        for definition in definitions:

            definition_elem = Element("definition")
            definition_elem.id = definition.id

            definition_elem.name = definition.name
            definition_elem.username = definition.username
            definition_elem.reject_empty_nonce_ts = definition.reject_empty_nonce_ts
            definition_elem.reject_stale_username = definition.reject_stale_username
            definition_elem.expiry_limit = definition.expiry_limit
            definition_elem.nonce_freshness = definition.nonce_freshness

            definition_list.append(definition_elem)

        return ZATO_OK, etree.tostring(definition_list)

class GetDetails(AdminService):
    """ Returns details of a particular WS-S definition.
    """
    def handle(self, *args, **kwargs):

        payload = kwargs.get("payload")
        request_params = ["id"]
        new_params = _get_params(payload, request_params, "definition.")
        def_id = new_params["id"]

        try:
            definition = self.server.odb.query(WSSDefinition).filter_by(id=def_id).one()
        except orm_exc.NoResultFound:
            raise ZatoException("WS-S definition [%s] does not exist" % definition_name)
        else:
            definition_elem = Element("definition")
            definition_elem.id = definition.id

            definition_elem.name = definition.name
            definition_elem.username = definition.username
            definition_elem.reject_empty_nonce_ts = definition.reject_empty_nonce_ts
            definition_elem.reject_stale_username = definition.reject_stale_username
            definition_elem.expiry_limit = definition.expiry_limit
            definition_elem.nonce_freshness = definition.nonce_freshness

            return ZATO_OK, etree.tostring(definition_elem)

class EditDefinition(AdminService):
    """ Updates a WS-S definition.
    """
    def handle(self, *args, **kwargs):

        payload = kwargs.get("payload")
        request_params = ["id", "name", "original_name", "username", "reject_empty_nonce_ts",
                          "reject_stale_username", "expiry_limit", "nonce_freshness"]
        new_params = _get_params(payload, request_params, "definition.")
        def_id = new_params["id"]

        try:
            definition = self.server.odb.query(WSSDefinition).filter_by(id=def_id).one()
        except orm_exc.NoResultFound:
            raise ZatoException("WS-S definition [%s] does not exist" % new_params["original_name"])
        else:
            definition.name = new_params["name"]
            definition.username = new_params["username"]
            definition.reject_empty_nonce_ts = new_params["reject_empty_nonce_ts"]
            definition.reject_stale_username = new_params["reject_stale_username"]
            definition.expiry_limit = new_params["expiry_limit"]
            definition.nonce_freshness = new_params["nonce_freshness"]

            self.server.odb.add(definition)
            self.server.odb.commit()

        return ZATO_OK, ""