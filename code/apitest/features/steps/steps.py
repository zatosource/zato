# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Behave
from behave import given, then

import base64

# Zato
from zato.apitest import steps as default_steps
from zato.apitest.steps.json import set_pointer
from zato.apitest.util import obtain_values, utcnow

@given('I store a format string "{value}" under "{name}"')
def given_i_store_format_string_value_under_name(ctx, value, name):
    ctx.zato.user_ctx[name] = str(value).format(**ctx.zato.user_ctx)

@given('I store UTC now under "{name}" "{format}"')
@obtain_values
def given_i_store_utc_now_under_name(ctx, name, format):
    ctx.zato.user_ctx[name] = utcnow(format=ctx.zato.date_formats[format])

@then('I decode "{value}" using Base64 under "{name}"')
@obtain_values
def then_i_decode_value_using_base64_under_name(ctx, value, name):
    ctx.zato.user_ctx[name] = value.decode('base64','strict')

@given('I decode "{value}" using Base64 under "{name}"')
@obtain_values
def given_i_decode_value_using_base64_under_name(ctx, value, name):
    ctx.zato.user_ctx[name] = value.decode('base64','strict')