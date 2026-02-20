# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os

# Django
from django.http import JsonResponse

# Zato
from zato.admin.web.views import method_allowed

if 0:
    from django.http import HttpRequest

def get_icon_for_extension(extension):
    extension_to_icon = {
        '.py': 'python.png',
        '.pyw': 'python.png',
        '.pyi': 'python.png',
        '.js': 'javascript.png',
        '.mjs': 'javascript.png',
        '.jsx': 'react.png',
        '.ts': 'typescript.png',
        '.tsx': 'react.png',
        '.json': 'json.png',
        '.xml': 'xml.png',
        '.html': 'html.png',
        '.htm': 'html.png',
        '.css': 'css.png',
        '.scss': 'sass.png',
        '.sass': 'sass.png',
        '.less': 'less.png',
        '.sql': 'database.png',
        '.yaml': 'settings.png',
        '.yml': 'settings.png',
        '.ini': 'settings.png',
        '.cfg': 'settings.png',
        '.conf': 'settings.png',
        '.toml': 'settings.png',
        '.md': 'text.png',
        '.txt': 'text.png',
        '.rst': 'text.png',
        '.log': 'text.png',
        '.csv': 'text.png',
        '.java': 'java.png',
        '.c': 'c.png',
        '.h': 'header.png',
        '.cpp': 'cpp.png',
        '.hpp': 'header.png',
        '.cc': 'cpp.png',
        '.cxx': 'cpp.png',
        '.cs': 'csharp.png',
        '.go': 'go.png',
        '.rs': 'rust.png',
        '.rb': 'ruby.png',
        '.php': 'php.png',
        '.swift': 'swift.png',
        '.kt': 'kotlin.png',
        '.kts': 'kotlin.png',
        '.scala': 'scala.png',
        '.clj': 'clojure.png',
        '.cljs': 'clojure.png',
        '.ex': 'elixir.png',
        '.exs': 'elixir.png',
        '.erl': 'erlang.png',
        '.hrl': 'erlang.png',
        '.hs': 'haskell.png',
        '.lhs': 'haskell.png',
        '.ml': 'ocaml.png',
        '.mli': 'ocaml.png',
        '.fs': 'fsharp.png',
        '.fsx': 'fsharp.png',
        '.lua': 'lua.png',
        '.dart': 'dart.png',
        '.elm': 'elm.png',
        '.nim': 'nim.png',
        '.jl': 'julia.png',
        '.r': 'text.png',
        '.R': 'text.png',
        '.sh': 'console.png',
        '.bash': 'console.png',
        '.zsh': 'console.png',
        '.fish': 'console.png',
        '.ps1': 'powershell.png',
        '.bat': 'console.png',
        '.cmd': 'console.png',
        '.exe': 'executable.png',
        '.dll': 'lib.png',
        '.so': 'lib.png',
        '.dylib': 'lib.png',
        '.a': 'lib.png',
        '.lib': 'lib.png',
        '.zip': 'archive.png',
        '.tar': 'archive.png',
        '.gz': 'archive.png',
        '.bz2': 'archive.png',
        '.xz': 'archive.png',
        '.7z': 'archive.png',
        '.rar': 'archive.png',
        '.pdf': 'pdf.png',
        '.doc': 'office-word.png',
        '.docx': 'office-word.png',
        '.xls': 'office-excel.png',
        '.xlsx': 'office-excel.png',
        '.ppt': 'office-powerpoint.png',
        '.pptx': 'office-powerpoint.png',
        '.odt': 'libreoffice-writer.png',
        '.ods': 'libreoffice-spreadsheet.png',
        '.odp': 'libreoffice-presentation.png',
        '.png': 'raster.png',
        '.jpg': 'raster.png',
        '.jpeg': 'raster.png',
        '.gif': 'raster.png',
        '.bmp': 'raster.png',
        '.webp': 'raster.png',
        '.ico': 'icon.png',
        '.svg': 'vector.png',
        '.mp3': 'sound.png',
        '.wav': 'sound.png',
        '.ogg': 'sound.png',
        '.flac': 'sound.png',
        '.mp4': 'video.png',
        '.avi': 'video.png',
        '.mkv': 'video.png',
        '.mov': 'video.png',
        '.webm': 'video.png',
        '.ttf': 'font.png',
        '.otf': 'font.png',
        '.woff': 'font.png',
        '.woff2': 'font.png',
        '.gitignore': 'git.png',
        '.gitattributes': 'git.png',
        '.gitmodules': 'git.png',
        'Makefile': 'make.png',
        'makefile': 'make.png',
        'Dockerfile': 'console.png',
        'docker-compose.yml': 'console.png',
        'docker-compose.yaml': 'console.png',
    }
    return extension_to_icon.get(extension, 'file.png')

def get_icon_for_file(filename):
    if filename in ('Makefile', 'makefile', 'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml'):
        return get_icon_for_extension(filename)
    ext = os.path.splitext(filename)[1].lower()
    return get_icon_for_extension(ext)

@method_allowed('GET')
def list_directory(req:'HttpRequest'):

    path = req.GET.get('path', '')

    if not path:
        return JsonResponse({'success': False, 'error': 'Path is required'}, status=400)

    path = os.path.expanduser(path)
    path = os.path.abspath(path)

    if not os.path.exists(path):
        return JsonResponse({'success': False, 'error': 'Path does not exist'}, status=404)

    if not os.path.isdir(path):
        return JsonResponse({'success': False, 'error': 'Path is not a directory'}, status=400)

    items = []

    try:
        entries = os.listdir(path)
        entries.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))

        for entry in entries:
            if entry.startswith('.'):
                continue

            full_path = os.path.join(path, entry)
            is_dir = os.path.isdir(full_path)

            item = {
                'name': entry,
                'path': full_path,
                'is_dir': is_dir,
            }

            if is_dir:
                item['icon'] = 'folder.png'
                item['icon_expanded'] = 'folder-expanded.png'
            else:
                item['icon'] = get_icon_for_file(entry)
                try:
                    item['size'] = os.path.getsize(full_path)
                except OSError:
                    item['size'] = 0

            items.append(item)

    except PermissionError:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    return JsonResponse({
        'success': True,
        'path': path,
        'items': items
    })
