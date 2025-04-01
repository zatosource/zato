# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import mimetypes
import posixpath
from logging import getLogger
from pathlib import Path

# Django
from django.http import FileResponse, Http404, HttpResponseNotModified
from django.template.response import TemplateResponse
from django.utils._os import safe_join
from django.utils.http import http_date, parse_http_date

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.json_internal import loads
from zato.common.util.platform_ import is_windows

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

windows_disabled = [
    'jms-wmq',
    'sftp'
]

# ################################################################################################################################
# ################################################################################################################################

def get_template_response(req, template_name, return_data):

    if is_windows:
        for name in windows_disabled:
            if name in template_name:
                return_data['is_disabled'] = True
                return_data['disabled_template_name'] = template_name

    return TemplateResponse(req, template_name, return_data)

# ################################################################################################################################
# ################################################################################################################################

def get_user_profile(user, needs_logging=True):
    if needs_logging:
        logger.info('Getting profile for user `%s`', user)

    from zato.admin.web.models import UserProfile

    try:
        user_profile = UserProfile.objects.get(user=user)
        if needs_logging:
            logger.info('Found an existing profile for user `%s`', user)
    except UserProfile.DoesNotExist:

        if needs_logging:
            logger.info('Did not find an existing profile for user `%s`', user)

        user_profile = UserProfile(user=user)
        user_profile.save()

        if needs_logging:
            logger.info('Created a profile for user `%s`', user)

    finally:
        if needs_logging:
            logger.info('Returning a user profile for `%s`', user)
        return user_profile

# ################################################################################################################################
# ################################################################################################################################

def set_user_profile_totp_key(user_profile, zato_secret_key, totp_key, totp_key_label=None, opaque_attrs=None):

    if not opaque_attrs:
        opaque_attrs = user_profile.opaque1
        opaque_attrs = loads(opaque_attrs) if opaque_attrs else {}

    cm = CryptoManager(secret_key=zato_secret_key)

    # TOTP key is always encrypted
    totp_key = cm.encrypt(totp_key.encode('utf8'))
    opaque_attrs['totp_key'] = totp_key

    # .. and so is its label
    if totp_key_label:
        totp_key_label = cm.encrypt(totp_key_label.encode('utf8'))
        opaque_attrs['totp_key_label'] = totp_key_label

    return opaque_attrs

# ################################################################################################################################
# ################################################################################################################################

#
# Taken from Django to change the content type from application/json to application/javascript.
#
def static_serve(request, path, document_root=None, show_indexes=False):
    """
    Serve static files below a given point in the directory structure.

    To use, put a URL pattern such as::

        from django.views.static import serve

        path('<path:path>', serve, {'document_root': '/path/to/my/files/'})

    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  This index view will use the template hardcoded below,
    but if you'd like to override it, you can create a template called
    ``static/directory_index.html``.
    """

    path = posixpath.normpath(path).lstrip("/")
    fullpath = Path(safe_join(document_root, path))
    if fullpath.is_dir():
        if show_indexes:
            return directory_index(path, fullpath)
        raise Http404('Directory indexes are not allowed here.')
    if not fullpath.exists():
        raise Http404(f'Path {fullpath} does not exist')
    # Respect the If-Modified-Since header.
    statobj = fullpath.stat()
    if not was_modified_since(
        request.META.get("HTTP_IF_MODIFIED_SINCE"), statobj.st_mtime
    ):
        return HttpResponseNotModified()
    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or "application/octet-stream"

    # Explicitly set the content type for JSON resources.
    # Note that this needs to be combined with SECURE_CONTENT_TYPE_NOSNIFF=False in settings.py
    if fullpath.name.endswith('.js'):
        content_type = 'application/javascript'

    response = FileResponse(fullpath.open("rb"), content_type=content_type)
    response.headers["Last-Modified"] = http_date(statobj.st_mtime)
    if encoding:
        response.headers["Content-Encoding"] = encoding
    return response

def was_modified_since(header=None, mtime=0):
    """
    Was something modified since the user last downloaded it?

    header
      This is the value of the If-Modified-Since header.  If this is None,
      I'll just return True.

    mtime
      This is the modification time of the item we're talking about.
    """
    try:
        if header is None:
            raise ValueError
        header_mtime = parse_http_date(header)
        if int(mtime) > header_mtime:
            raise ValueError
    except (ValueError, OverflowError):
        return True
    return False

# ################################################################################################################################
# ################################################################################################################################
