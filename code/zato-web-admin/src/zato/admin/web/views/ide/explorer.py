# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os

# Django
from django.http import FileResponse, JsonResponse

# Zato
from zato.admin.web.views import method_allowed

if 0:
    from django.http import HttpRequest

def get_icon_for_extension(extension):
    extension_to_icon = {
        '.py': 'file_type_python.svg',
        '.pyw': 'file_type_python.svg',
        '.pyi': 'file_type_python.svg',
        '.js': 'file_type_js.svg',
        '.mjs': 'file_type_js.svg',
        '.jsx': 'file_type_reactjs.svg',
        '.ts': 'file_type_typescript.svg',
        '.tsx': 'file_type_reactts.svg',
        '.json': 'file_type_json.svg',
        '.xml': 'file_type_xml.svg',
        '.html': 'file_type_html.svg',
        '.htm': 'file_type_html.svg',
        '.css': 'file_type_css.svg',
        '.scss': 'file_type_scss.svg',
        '.sass': 'file_type_sass.svg',
        '.less': 'file_type_less.svg',
        '.sql': 'file_type_sql.svg',
        '.yaml': 'file_type_yaml.svg',
        '.yml': 'file_type_yaml.svg',
        '.ini': 'file_type_ini.svg',
        '.cfg': 'file_type_config.svg',
        '.conf': 'file_type_config.svg',
        '.toml': 'file_type_toml.svg',
        '.md': 'file_type_markdown.svg',
        '.txt': 'file_type_text.svg',
        '.rst': 'file_type_text.svg',
        '.log': 'file_type_log.svg',
        '.csv': 'file_type_text.svg',
        '.java': 'file_type_java.svg',
        '.c': 'file_type_c.svg',
        '.h': 'file_type_cheader.svg',
        '.cpp': 'file_type_cpp.svg',
        '.hpp': 'file_type_cppheader.svg',
        '.cc': 'file_type_cpp.svg',
        '.cxx': 'file_type_cpp.svg',
        '.cs': 'file_type_csharp.svg',
        '.go': 'file_type_go.svg',
        '.rs': 'file_type_rust.svg',
        '.rb': 'file_type_ruby.svg',
        '.php': 'file_type_php.svg',
        '.swift': 'file_type_swift.svg',
        '.kt': 'file_type_kotlin.svg',
        '.kts': 'file_type_kotlin.svg',
        '.scala': 'file_type_scala.svg',
        '.clj': 'file_type_clojure.svg',
        '.cljs': 'file_type_clojure.svg',
        '.ex': 'file_type_elixir.svg',
        '.exs': 'file_type_elixir.svg',
        '.erl': 'file_type_erlang.svg',
        '.hrl': 'file_type_erlang.svg',
        '.hs': 'file_type_haskell.svg',
        '.lhs': 'file_type_haskell.svg',
        '.ml': 'file_type_ocaml.svg',
        '.mli': 'file_type_ocaml.svg',
        '.fs': 'file_type_fsharp.svg',
        '.fsx': 'file_type_fsharp.svg',
        '.lua': 'file_type_lua.svg',
        '.dart': 'file_type_dart.svg',
        '.elm': 'file_type_elm.svg',
        '.nim': 'file_type_nim.svg',
        '.jl': 'file_type_julia.svg',
        '.r': 'file_type_r.svg',
        '.R': 'file_type_r.svg',
        '.sh': 'file_type_shell.svg',
        '.bash': 'file_type_shell.svg',
        '.zsh': 'file_type_shell.svg',
        '.fish': 'file_type_shell.svg',
        '.ps1': 'file_type_powershell.svg',
        '.bat': 'file_type_bat.svg',
        '.cmd': 'file_type_bat.svg',
        '.exe': 'file_type_binary.svg',
        '.dll': 'file_type_binary.svg',
        '.so': 'file_type_binary.svg',
        '.dylib': 'file_type_binary.svg',
        '.a': 'file_type_binary.svg',
        '.lib': 'file_type_binary.svg',
        '.zip': 'file_type_zip.svg',
        '.tar': 'file_type_zip.svg',
        '.gz': 'file_type_zip.svg',
        '.bz2': 'file_type_zip.svg',
        '.xz': 'file_type_zip.svg',
        '.7z': 'file_type_zip.svg',
        '.rar': 'file_type_zip.svg',
        '.pdf': 'file_type_pdf.svg',
        '.doc': 'file_type_word.svg',
        '.docx': 'file_type_word.svg',
        '.xls': 'file_type_excel.svg',
        '.xlsx': 'file_type_excel.svg',
        '.ppt': 'file_type_powerpoint.svg',
        '.pptx': 'file_type_powerpoint.svg',
        '.odt': 'file_type_word.svg',
        '.ods': 'file_type_excel.svg',
        '.odp': 'file_type_powerpoint.svg',
        '.png': 'file_type_image.svg',
        '.jpg': 'file_type_image.svg',
        '.jpeg': 'file_type_image.svg',
        '.gif': 'file_type_image.svg',
        '.bmp': 'file_type_image.svg',
        '.webp': 'file_type_image.svg',
        '.ico': 'file_type_image.svg',
        '.svg': 'file_type_svg.svg',
        '.mp3': 'file_type_audio.svg',
        '.wav': 'file_type_audio.svg',
        '.ogg': 'file_type_audio.svg',
        '.flac': 'file_type_audio.svg',
        '.mp4': 'file_type_video.svg',
        '.avi': 'file_type_video.svg',
        '.mkv': 'file_type_video.svg',
        '.mov': 'file_type_video.svg',
        '.webm': 'file_type_video.svg',
        '.ttf': 'file_type_font.svg',
        '.otf': 'file_type_font.svg',
        '.woff': 'file_type_font.svg',
        '.woff2': 'file_type_font.svg',
        '.gitignore': 'file_type_git.svg',
        '.gitattributes': 'file_type_git.svg',
        '.gitmodules': 'file_type_git.svg',
        'Makefile': 'file_type_cmake.svg',
        'makefile': 'file_type_cmake.svg',
        'Dockerfile': 'file_type_docker.svg',
        'docker-compose.yml': 'file_type_docker.svg',
        'docker-compose.yaml': 'file_type_docker.svg',
    }
    return extension_to_icon.get(extension, 'default_file.svg')

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
                item['icon'] = 'default_folder.svg'
                item['icon_expanded'] = 'default_folder_opened.svg'
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

@method_allowed('GET')
def read_file(req:'HttpRequest'):

    path = req.GET.get('path', '')

    if not path:
        return JsonResponse({'success': False, 'error': 'Path is required'}, status=400)

    path = os.path.expanduser(path)
    path = os.path.abspath(path)

    if not os.path.exists(path):
        return JsonResponse({'success': False, 'error': 'File does not exist'}, status=404)

    if not os.path.isfile(path):
        return JsonResponse({'success': False, 'error': 'Path is not a file'}, status=400)

    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except PermissionError:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

    filename = os.path.basename(path)

    return JsonResponse({
        'success': True,
        'path': path,
        'filename': filename,
        'content': content
    })

@method_allowed('GET')
def download_file(req:'HttpRequest'):

    path = req.GET.get('path', '')

    if not path:
        return JsonResponse({'success': False, 'error': 'Path is required'}, status=400)

    path = os.path.expanduser(path)
    path = os.path.abspath(path)

    if not os.path.exists(path):
        return JsonResponse({'success': False, 'error': 'File does not exist'}, status=404)

    if not os.path.isfile(path):
        return JsonResponse({'success': False, 'error': 'Path is not a file'}, status=400)

    try:
        response = FileResponse(open(path, 'rb'), as_attachment=True, filename=os.path.basename(path))
        return response
    except PermissionError:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
