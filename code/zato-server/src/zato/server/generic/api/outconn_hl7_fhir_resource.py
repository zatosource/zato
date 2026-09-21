# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The resource an outgoing FHIR connection's client builds - fhirpy's, except that a write which went to the
# connection's queue comes back as its SendResult rather than being read into the resource.

# fhirpy
from fhirpy.base.resource import BaseResource
from fhirpy.lib import SyncFHIRResource

# Zato
from zato.common.pubsub.outgoing import SendResult

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class HL7FHIRResource(SyncFHIRResource):
    """ A resource whose save, create, update, patch and delete hand back the SendResult of a queued write and otherwise
    do what fhirpy's do.
    """

    def save(self, fields:'any_'=None, search_params:'any_'=None) -> 'any_':
        response_data = self.__client__.save(self, fields, _search_params=search_params, _as_dict=True)

        # A write that went to the queue has no answer to read into this resource
        if isinstance(response_data, SendResult):
            return response_data

        if response_data:
            resource_type = self.resource_type
            super(BaseResource, self).clear()
            super(BaseResource, self).update(**self.__client__.resource(resource_type, **response_data))

        return self

# ################################################################################################################################

    def create(self, **kwargs:'any_') -> 'any_':
        out = self.save(search_params=kwargs)
        return out

# ################################################################################################################################

    def update(self) -> 'any_':
        if not self.id:
            raise TypeError('Resource `id` is required for update operation')

        out = self.save()
        return out

# ################################################################################################################################

    def patch(self, **kwargs:'any_') -> 'any_':
        if not self.id:
            raise TypeError('Resource `id` is required for patch operation')

        super(BaseResource, self).update(**kwargs)

        out = self.save(fields=list(kwargs.keys()))
        return out

# ################################################################################################################################
# ################################################################################################################################
