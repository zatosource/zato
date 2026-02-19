from typing import Any

import logging
import os
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render

def swagger_view(request: Any) -> None: ...

def serve_openapi(request: Any) -> None: ...
