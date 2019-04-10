# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
import logging
from json import loads
from logging import getLogger

# JSON Schema
from jsonschema import validate as js_validate
from jsonschema.exceptions import ValidationError as JSValidationError
from jsonschema.validators import validator_for

# Zato
from zato.common import CHANNEL

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:

    # stdlib
    from typing import Callable

    # Bunch
    from bunch import Bunch

    # For pyflakes
    Bunch = Bunch
    Callable = Callable

# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ValidationException(Exception):
    pass

# ################################################################################################################################
# ################################################################################################################################

class ValidationError(object):
    """ Base class for validation error-related classes.
    """

# ################################################################################################################################
# ################################################################################################################################

class RESTError(ValidationError):
    """ An error reporter that serializes JSON Schema validation errors into regular REST responses.
    """

# ################################################################################################################################
# ################################################################################################################################

class JSONRPCError(ValidationError):
    """ An error reporter that serializes JSON Schema validation errors into JSON-RPC responses.
    """

# ################################################################################################################################
# ################################################################################################################################

class ValidationConfig(object):
    """ An individual set of configuration options - each object requiring validation (e.g. each channel)
    will have its own instance of this class assigned to its validator.
    """
    __slots__ = 'is_enabled', 'object_type', 'object_name', 'schema_path', 'schema', 'validator', 'should_report_errors'

    def __init__(self):
        self.is_enabled = None   # type: bool

        # Object type is channel type or, in the future, one of outgoing connections
        # whose requests to external resources we may also want to validate.
        self.object_type = None # type: unicode

        self.object_name = None # type: unicode
        self.schema_path = None # type: unicode
        self.schema = None      # type: dict
        self.validator = None   # type: object
        self.should_report_errors = None # type: bool

# ################################################################################################################################
# ################################################################################################################################

class Result(object):
    def __init__(self):
        self.is_ok = None # type: bool
        self.error = None # type: unicode

# ################################################################################################################################
# ################################################################################################################################

class Validator(object):
    """ Validates JSON requests against a previously assigned schema and serializes errors according to the caller's type,
    e.g. using REST or JSON-RPC.
    """
    __slots__ = 'is_initialized', 'config'

    def __init__(self):
        self.is_initialized = False # type: bool
        self.config = None # type: ValidationConfig

    def init(self):
        if not os.path.exists(self.config.schema_path):
            raise ValidationException('JSON schema not found `{}` ({})'.format(self.config.schema_path, self.config.object_name))

        # The file is sure to exist
        with open(self.config.schema_path) as f:
            schema = f.read()

        # Parse the contents as JSON
        schema = loads(schema)

        # Assign the schema and validator for the schema for later use
        self.config.schema = schema
        self.config.validator = validator_for(schema)

        # Everything is set up = we are initialized
        self.is_initialized = True

    def validate(self, data, _validate=js_validate):
        # type: (object, Callable) -> Result

        # Result we will return
        out = Result()

        try:
            js_validate(data, self.config.schema, self.config.validator)
        except JSValidationError as e:
            out.is_ok = False
            if self.config.should_report_errors:
                out.error = str(e)
        else:
            out.is_ok = True

        return out

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    schema_path = './schema1.json'

    config = ValidationConfig()
    config.is_enabled = True
    config.object_name = 'My Channel'
    config.object_type = CHANNEL.JSON_RPC
    config.schema_path = schema_path

    validator = Validator()
    validator.config = config
    validator.init()

    data = {'aaa': 'bbb'}
    validator.validate(data)

# ################################################################################################################################
# ################################################################################################################################
