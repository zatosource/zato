# -*- coding: utf-8 -*-

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.api import CommonObject
from zato.common.exception import BadRequest
from zato.common.typing_ import any_, anylist, anylistnone, intlistnone, intnone, strdict, strlistnone, strnone
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DataItem(Model):
    name: str
    object_type: str
    initial_data: any_

@dataclass(init=False)
class CreateObjectsRequest(Model):
    object_type: str
    id: intnone
    id_list: intlistnone
    name: strnone
    name_list: strlistnone
    object_list: anylistnone
    pattern: strnone
    initial_data: any_

@dataclass(init=False)
class CreateObjectsResponse(Model):
    objects: anylist

# ################################################################################################################################
# ################################################################################################################################

class CreateObjects(Service):

    name = 'zato.common.create-objects'
    input = CreateObjectsRequest
    output = CreateObjectsResponse

# ################################################################################################################################

    def _get_basic_security_basic_auth(self, name:'str', initial_data:'strdict') -> 'strdict':

        request = {
            'is_active': True,
            'username': 'zato-test-' + name,
            'realm': 'Zato.Test',
        }

        return request

# ################################################################################################################################

    def _extract_response_items(self, response:'strdict') -> 'strdict':

        # Our response to produce
        out:'strdict' = {}

        if len(response) == 1:
            keys = list(response)
            response_wrapper = keys[0]
            if response_wrapper.startswith('zato'):
                response = response[response_wrapper]

        out.update(response)

        return out

# ################################################################################################################################

    def _turn_names_into_objects_list(self, input:'CreateObjectsRequest') -> 'CreateObjectsRequest':

        # Requests of these types will not have any names on input ..
        no_name_requests = {}

        # .. populate empty names per the above ..
        if input.object_type in no_name_requests:
            input.name_list = ['']

        # .. or build a list of names out of what we have on input ..
        else:
            input.name_list = input.name_list or []

        # .. at this point, we know that we have a list of names ..
        # .. so we can turn them into objects, unless we already have objects on input ..
        if not input.object_list:

            # .. a list for us to populate ..
            object_list = []

            # .. go through each input name ..
            for name in input.name_list:

                # .. turn it into an object ..
                data = DataItem()

                # .. populate its fields ..
                data.name = name
                data.object_type = input.object_type
                data.initial_data = input.initial_data

                # .. append it for later use ..
                object_list.append(data)

            # .. assign the object list to what we are to return ..
            input.object_list = object_list

        # .. finally, we can return everything to our caller.
        return input

# ################################################################################################################################

    def handle(self):

        # Zato
        from zato.server.service.internal.security.basic_auth import Create as SecBasicAuthCreate

        # Local variables
        input:'CreateObjectsRequest' = self.request.input

        # Our response to produce:
        out = CreateObjectsResponse()
        out.objects = []

        # Maps object types to services that create them

        # Maps incoming string names of objects to services that actually delete them
        service_map = {
            CommonObject.Security_Basic_Auth: SecBasicAuthCreate,
        }

        # Maps incoming string names of objects to functions that prepare basic create requests
        request_func_map = {
            CommonObject.Security_Basic_Auth: self._get_basic_security_basic_auth,
        }

        # Get the service that will create the object
        service = service_map[input.object_type]

        # Turn names into objects
        input = self._turn_names_into_objects_list(input)

        # At this point, we know we have a list of objects, even if empty.
        if not input.object_list:
            return

        # Log what we are about to do
        self.logger.info('Creating objects -> len=%s', len(input.object_list))

        # .. go through each name we are given on input ..
        for data in input.object_list:

            # .. get a request with basic details ..
            request_func = request_func_map[data.object_type]
            request = request_func(data.name, data.initial_data)

            # .. add the name from input ..
            request['name'] = data.name

            # .. populate the request with initial data ..
            if data.initial_data:
                for key, value in data.initial_data.items():
                    request[key] = value

            # .. create an object now ..
            try:
                response = self.invoke(service.get_name(), request)
                response = self._extract_response_items(response)
                out.objects.append(response)
            except BadRequest as e:

                # .. ignore objects that already exist ..
                self.logger.info('Ignoring -> %s', e)

            else:
                # .. finally, store information in logs that we are done.
                self.logger.info('Object created -> %s -> %s', data.name, response)

        # Produce the response for our caller
        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################
