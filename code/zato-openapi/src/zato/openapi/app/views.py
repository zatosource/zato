# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import logging
import os

# Django
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render

# ################################################################################################################################
# ################################################################################################################################

# Logger for this module
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def swagger_view(request):
    """ Render the Swagger UI page pointing to our OpenAPI specification.
    """
    context = {
        'swagger_version': settings.SWAGGER_VERSION,
    }
    return render(request, 'swagger.html', context)

# ################################################################################################################################

def serve_openapi(request):
    """ Serve the OpenAPI specification file.
    """
    openapi_path = settings.OPENAPI_PATH

    if not os.path.exists(openapi_path):
        logger.error(f'OpenAPI specification file not found at {openapi_path}')
        raise Http404('OpenAPI specification file not found')

    try:
        with open(openapi_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/yaml')
    except Exception as e:
        logger.error(f'Error reading OpenAPI specification file: {e}')
        raise Http404('Error reading OpenAPI specification file')

# ################################################################################################################################
# ################################################################################################################################
