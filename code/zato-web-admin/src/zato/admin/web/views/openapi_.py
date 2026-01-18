# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import sys
import tempfile
from logging import getLogger

# Django
from django.http import HttpResponse
from django.http.response import HttpResponseServerError

# Zato
from zato.admin.web.views import method_allowed
from zato.common.json_internal import dumps
from zato.common.util import openapi_ as openapi_module

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def json_response(data, success=True):
    response_json = dumps(data)
    response_class = HttpResponse if success else HttpResponseServerError
    return response_class(response_json, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def parse(req):

    response_data = {}
    response_data['success'] = False

    try:
        openapi_data = req.body.decode('utf-8')

        openapi_dir = os.path.dirname(os.path.abspath(openapi_module.__file__))
        parser_path = os.path.join(openapi_dir, 'parser.py')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(openapi_data)
            temp_file_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, parser_path, '--from-file', temp_file_path],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                error_msg = result.stderr or 'Parser returned non-zero exit code'
                response_data['error'] = error_msg
                return json_response(response_data, success=False)

            response_data['success'] = True
            response_data['result'] = result.stdout

            return json_response(response_data)

        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        logger.exception('parse exception')
        response_data['error'] = str(e)
        return json_response(response_data, success=False)

# ################################################################################################################################
# ################################################################################################################################
