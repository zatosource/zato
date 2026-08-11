# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps, loads
from logging import getLogger
from traceback import format_exc
from typing import NamedTuple

# Django
from django.http import HttpResponse
from django.http.response import HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.common.util.open_ import open_r, open_w

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist

    anydict = anydict
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# A file larger than this is edited outside the dashboard so its contents are not sent to the browser
max_editable_size = 256 * 1024

# ################################################################################################################################
# ################################################################################################################################

class ContentInfo(NamedTuple):
    kind: str
    section_count: int
    entry_count: int

# ################################################################################################################################
# ################################################################################################################################

def to_directory(path:'str') -> 'str':
    """ A directory in the form all the directories here are kept and compared in, that is,
    an absolute path with a trailing separator.
    """
    out = os.path.abspath(os.path.expanduser(path)) + os.sep
    return out

# ################################################################################################################################
# ################################################################################################################################

class Definition:
    """ What one screen built on the config files kit provides - where its files live,
    what each of them holds, and which template draws it. A screen subclasses this and
    hands its instance to the two kit views below.
    """
    template_name = ''
    log_prefix = ''

# ################################################################################################################################

    def get_directory_list(self) -> 'strlist':
        """ The directories the screen reads and writes files in. The first one is where
        new files land.
        """
        raise Exception('get_directory_list must be given by a subclass')

# ################################################################################################################################

    def build_content_info(self, file_name:'str', content:'str') -> 'ContentInfo':
        """ What a file holds - the kind of file it is and how much there is in it.
        """
        raise Exception('build_content_info must be given by a subclass')

# ################################################################################################################################

    def get_display_name(self, file_name:'str') -> 'str':
        """ What the file is reached by on the page, out of what it is called on disk.
        """
        return file_name

# ################################################################################################################################

    def is_listed(self, file_name:'str') -> 'bool':
        """ Whether a file of this name has a line in the listing at all.
        """
        out = not file_name.startswith('.')
        return out

# ################################################################################################################################

    def get_full_path(self, directory:'str', file_name:'str') -> 'str':
        """ The full path to the file that the request names. A file name names a file and
        nothing else, and the directory it is in is one of the directories the screen works with.
        """
        base_name = os.path.basename(file_name)

        if base_name != file_name:
            raise Exception(f'Invalid file name `{file_name}`')

        directory = to_directory(directory)

        if directory not in self.get_directory_list():
            raise Exception(f'Invalid directory `{directory}`')

        out = os.path.join(directory, base_name)
        return out

# ################################################################################################################################

    def build_file_item(self, directory:'str', file_name:'str', full_path:'str') -> 'anydict':
        """ One file as the page reads it. A file larger than the browser edits in place is
        reported without its contents because they would not be used, and so is one that is
        not text at all, a directory holding whatever the user put in it.
        """
        size = os.path.getsize(full_path)
        is_editable = size <= max_editable_size
        content = ''

        if is_editable:
            try:
                with open_r(full_path) as opened:
                    content = opened.read()
            except UnicodeDecodeError:
                is_editable = False

        info = self.build_content_info(file_name, content)

        out = {
            'name': self.get_display_name(file_name),
            'file_name': file_name,
            'directory': directory,
            'path': full_path,
            'kind': info.kind,
            'section_count': info.section_count,
            'entry_count': info.entry_count,
            'size': size,
            'is_editable': is_editable,
            'content': content,
        }

        return out

# ################################################################################################################################

    def get_file_list(self, directory_list:'strlist') -> 'anylist':
        """ Every file the screen works with in the directories given, with what each of them holds.
        """
        out:'anylist' = []

        for directory in directory_list:

            # A directory the screen reads from does not have to exist yet
            if not os.path.exists(directory):
                continue

            for file_name in sorted(os.listdir(directory)):

                if not self.is_listed(file_name):
                    continue

                full_path = os.path.join(directory, file_name)

                if not os.path.isfile(full_path):
                    continue

                item = self.build_file_item(directory, file_name, full_path)
                out.append(item)

        return out

# ################################################################################################################################

    def save(self, request_data:'anydict') -> 'anydict':
        """ Writes the file's contents as the page has them now.
        """
        directory = request_data['directory']
        full_path = self.get_full_path(directory, request_data['file_name'])

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open_w(full_path) as opened:
            _ = opened.write(request_data['data'])

        logger.info('%s: saved %s', self.log_prefix, full_path)

        out = {'path': full_path}
        return out

# ################################################################################################################################

    def create(self, request_data:'anydict') -> 'anydict':
        """ Creates a file that was not there before, with the contents that the page starts it with.
        """
        directory = request_data['directory']
        full_path = self.get_full_path(directory, request_data['file_name'])

        if os.path.exists(full_path):
            raise Exception(f'File already exists `{full_path}`')

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open_w(full_path) as opened:
            _ = opened.write(request_data['data'])

        logger.info('%s: created %s', self.log_prefix, full_path)

        out = {'path': full_path}
        return out

# ################################################################################################################################

    def rename(self, request_data:'anydict') -> 'anydict':
        """ Gives the file another name in the directory it is in.
        """
        directory = request_data['directory']

        full_path = self.get_full_path(directory, request_data['file_name'])
        new_full_path = self.get_full_path(directory, request_data['new_file_name'])

        if os.path.exists(new_full_path):
            raise Exception(f'File already exists `{new_full_path}`')

        os.rename(full_path, new_full_path)

        logger.info('%s: renamed %s to %s', self.log_prefix, full_path, new_full_path)

        out = {'path': new_full_path}
        return out

# ################################################################################################################################

    def delete(self, request_data:'anydict') -> 'anydict':
        """ Removes the file from the directory it is kept in.
        """
        full_path = self.get_full_path(request_data['directory'], request_data['file_name'])

        if os.path.exists(full_path):
            os.remove(full_path)
            logger.info('%s: deleted %s', self.log_prefix, full_path)

        out = {'path': full_path}
        return out

# ################################################################################################################################
# ################################################################################################################################

def _json_response(data:'anydict', is_ok:'bool'=True) -> 'HttpResponse':

    serialized = dumps(data)
    payload = serialized.encode('utf-8')
    response_class = HttpResponse if is_ok else HttpResponseServerError

    out = response_class(payload, content_type='application/json')
    return out

# ################################################################################################################################
# ################################################################################################################################

def build_index_response(req:'any_', definition:'Definition') -> 'TemplateResponse':
    """ The screen's files, one of which is looked at and edited at a time.
    """
    directory_list = definition.get_directory_list()
    file_list:'anylist' = []
    error = ''

    try:
        file_list = definition.get_file_list(directory_list)
    except Exception as e:
        error = str(e)
        logger.error('%s: could not read the files: %s', definition.log_prefix, format_exc())

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'file_list_json': dumps(file_list),
        'default_directory': directory_list[0],
        'max_editable_size': max_editable_size,
        'error': error,
        'zato_clusters': True,
        'zato_template_name': definition.template_name,
    }

    out = TemplateResponse(req, definition.template_name, return_data)
    return out

# ################################################################################################################################
# ################################################################################################################################

def handle_persist(req:'any_', definition:'Definition') -> 'HttpResponse':
    """ Carries out one change that the page has made to a file.
    """
    action_handler = {
        'save': definition.save,
        'add': definition.create,
        'upload': definition.create,
        'rename': definition.rename,
        'delete': definition.delete,
    }

    try:
        request_data = loads(req.body.decode('utf-8'))
        action = request_data['action']

        if action not in action_handler:
            raise Exception(f'Unknown action `{action}`')

        handler = action_handler[action]
        data = handler(request_data['data'])

        out = _json_response({'success': True, 'data': data})
        return out

    except Exception as e:
        logger.error('%s: %s', definition.log_prefix, format_exc())

        out = _json_response({'success': False, 'error': str(e)}, False)
        return out

# ################################################################################################################################
# ################################################################################################################################
