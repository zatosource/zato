(function() {
    'use strict';

    var ZatoIDEEditorAce = {

        defaults: {
            theme: 'dark',
            language: 'python',
            fontSize: 12,
            tabSize: 4,
            lintDelay: 125,
            printMarginColumn: 120
        },

        completionMetaSelectedColor: '#ddd',

        getCompletionNameSelectedColor: function() {
            return getComputedStyle(document.documentElement).getPropertyValue('--zato-completion-name-selected-color').trim();
        },

        create: function(container, options) {
            var opts = {};
            for (var key in this.defaults) {
                opts[key] = this.defaults[key];
            }
            for (var key in options) {
                opts[key] = options[key];
            }

            var instanceId = 'zato-ide-ace-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);

            var instance = {
                id: instanceId,
                container: container,
                options: opts,
                content: opts.content || '',
                cursorLine: 1,
                cursorCol: 1,
                aceEditor: null
            };

            this.render(instance);
            this.setupCallbacks(instance);
            this.setupAutoSave(instance);

            return instance;
        },

        render: function(instance) {
            var container = instance.container;
            var opts = instance.options;

            var wrapper = document.createElement('div');
            wrapper.className = 'zato-ide-editor-wrapper';

            var editorContainer = document.createElement('div');
            editorContainer.className = 'zato-ide-ace-editor';
            editorContainer.id = instance.id + '-editor';

            wrapper.appendChild(editorContainer);
            container.appendChild(wrapper);

            var ideContainerId = opts.ideContainerId || container.id.replace('-editor-area', '');
            var statusbar = document.getElementById(ideContainerId + '-statusbar');

            instance.elements = {
                wrapper: wrapper,
                editorContainer: editorContainer,
                statusbar: statusbar
            };

            var aceTheme = opts.theme === 'dark' ? 'ace/theme/zato-dark' : 'ace/theme/zato';
            var aceMode = this.getAceMode(opts.language);

            var editor = ace.edit(editorContainer);
            editor.setTheme(aceTheme);
            editor.session.setMode(aceMode);
            editor.setFontSize(opts.fontSize + 'px');
            editor.session.setTabSize(opts.tabSize);
            editor.session.setUseSoftTabs(true);
            editor.setShowPrintMargin(true);
            editor.setPrintMarginColumn(opts.printMarginColumn);
            editor.setHighlightActiveLine(true);
            editor.setHighlightSelectedWord(true);
            editor.setDisplayIndentGuides(false);
            editor.setOption('fixedWidthGutter', true);
            editor.commands.removeCommand('foldall');
            editor.commands.removeCommand('unfoldall');
            editor.commands.removeCommand('toggleFoldWidget');
            editor.commands.removeCommand('togglerecording');
            editor.commands.removeCommand('replaymacro');
            var zubanCompleter = {
                getCompletions: function(aceEditor, session, pos, prefix, callback) {
                    console.log('[Complete] getCompletions called, pos:', pos, 'prefix:', prefix);
                    var code = aceEditor.getValue();
                    var line = pos.row + 1;
                    var column = pos.column;

                    if (!code.trim()) {
                        console.log('[Complete] Empty code, returning empty');
                        callback(null, []);
                        return;
                    }

                    var csrfToken = ZatoIDEEditorAce.getCsrfToken();
                    console.log('[Complete] Sending request to /zato/ide/complete/python/, line:', line, 'column:', column);
                    var xhr = new XMLHttpRequest();
                    xhr.open('POST', '/zato/ide/complete/python/', true);
                    xhr.setRequestHeader('Content-Type', 'application/json');
                    if (csrfToken) {
                        xhr.setRequestHeader('X-CSRFToken', csrfToken);
                    }
                    xhr.onreadystatechange = function() {
                        if (xhr.readyState === 4) {
                            console.log('[Complete] Response status:', xhr.status, 'response:', xhr.responseText.substring(0, 200));
                            if (xhr.status === 200) {
                                try {
                                    var response = JSON.parse(xhr.responseText);
                                    if (response.success && response.completions) {
                                        var results = [];
                                        for (var i = 0; i < response.completions.length; i++) {
                                            var item = response.completions[i];
                                            results.push({
                                                name: item.name,
                                                value: item.value,
                                                score: 1000 - i,
                                                meta: item.type
                                            });
                                        }
                                        console.log('[Complete] Returning', results.length, 'completions');
                                        callback(null, results);
                                        return;
                                    }
                                } catch (e) {
                                    console.warn('[Complete] Failed to parse response:', e);
                                }
                            }
                            callback(null, []);
                        }
                    };
                    var requestBody = JSON.stringify({
                        code: code,
                        line: line,
                        column: column
                    });
                    xhr.send(requestBody);
                }
            };

            var langTools = ace.require('ace/ext/language_tools');
            langTools.addCompleter(zubanCompleter);
            editor.setOptions({
                enableBasicAutocompletion: true,
                enableLiveAutocompletion: true,
                enableSnippets: false
            });
            editor.completers = [zubanCompleter];

            setInterval(function() {
                var allLines = document.querySelectorAll('.ace_autocomplete .ace_line');
                allLines.forEach(function(line) {
                    var isSelected = line.classList.contains('ace_selected');
                    var meta = line.querySelector('.ace_completion-meta');
                    var name = line.querySelector('.ace_');
                    if (isSelected) {
                        if (meta) {
                            meta.style.color = ZatoIDEEditorAce.completionMetaSelectedColor;
                            meta.style.opacity = '1';
                        }
                        if (name) {
                            name.style.color = ZatoIDEEditorAce.getCompletionNameSelectedColor();
                        }
                    } else {
                        if (meta) {
                            meta.style.color = '';
                            meta.style.opacity = '';
                        }
                        if (name) {
                            name.style.color = '';
                        }
                    }
                });
            }, 16);
            editor.commands.on('afterExec', function(e) {
                if (e.command.name === 'insertstring' && e.args === '.') {
                    console.log('[Complete] Dot pressed, triggering autocomplete');
                    editor.execCommand('startAutocomplete');
                }
            });

            var lintTimeout = null;
            var lintInProgress = false;
            var lintPending = false;
            var lintDelay = opts.lintDelay;
            editor.session.on('change', function() {
                console.log('[ZatoIDEEditorAce] session change event, language=' + instance.options.language);
                if (instance.options.language !== 'python') {
                    console.log('[ZatoIDEEditorAce] not python, skipping lint');
                    return;
                }
                if (lintTimeout) {
                    clearTimeout(lintTimeout);
                }
                if (lintInProgress) {
                    lintPending = true;
                    return;
                }
                lintTimeout = setTimeout(function() {
                    lintInProgress = true;
                    ZatoIDEEditorAce.lintPython(editor, function() {
                        lintInProgress = false;
                        if (lintPending) {
                            lintPending = false;
                            lintTimeout = setTimeout(function() {
                                lintInProgress = true;
                                ZatoIDEEditorAce.lintPython(editor, function() {
                                    lintInProgress = false;
                                });
                            }, lintDelay);
                        }
                    });
                }, lintDelay);
            });
            editor.renderer.$textLayer.$renderLine = (function(originalRenderLine) {
                return function(parent, row, onlyContents, foldLine) {
                    var result = originalRenderLine.call(this, parent, row, onlyContents, foldLine);
                    var firstChild = parent.firstChild;
                    if (firstChild && firstChild.nodeType === 3) {
                        var text = firstChild.textContent;
                        var match = text.match(/^( +)/);
                        if (match) {
                            var spaces = match[1];
                            var dots = '';
                            for (var i = 0; i < spaces.length; i++) {
                                dots += '·';
                            }
                            var span = document.createElement('span');
                            span.className = 'ace_indent_dot';
                            span.textContent = dots;
                            var rest = text.substring(spaces.length);
                            if (rest) {
                                var restNode = document.createTextNode(rest);
                                parent.replaceChild(restNode, firstChild);
                                parent.insertBefore(span, restNode);
                            } else {
                                parent.replaceChild(span, firstChild);
                            }
                        }
                    }
                    return result;
                };
            })(editor.renderer.$textLayer.$renderLine);
            editor.renderer.setScrollMargin(7, 7, 0, 0);
            editor.renderer.$gutterLayer.$fixedWidth = true;
            editor.renderer.$gutterLayer.gutterWidth = 50;
            editor.container.style.lineHeight = '1.32';

            var gutterEl = editor.renderer.$gutter;
            gutterEl.addEventListener('click', function(e) {
                var cell = e.target.closest('.ace_gutter-cell');
                if (!cell) {
                    return;
                }
                if (!cell.classList.contains('ace_error') && !cell.classList.contains('ace_warning') && !cell.classList.contains('ace_info')) {
                    return;
                }
                var row = parseInt(cell.textContent, 10) - 1;
                var annotations = editor.session.getAnnotations();
                var messages = [];
                for (var i = 0; i < annotations.length; i++) {
                    if (annotations[i].row === row) {
                        messages.push(annotations[i].text);
                    }
                }
                if (messages.length > 0) {
                    var text = messages.join('\n');
                    navigator.clipboard.writeText(text).then(function() {
                        if (instance.tooltipInstance) {
                            ZatoTooltip.showTemporary(instance.tooltipInstance, cell, 'Copied to clipboard', 1500);
                        }
                    });
                }
            });

            if (instance.content) {
                editor.setValue(instance.content, -1);
            }

            instance.aceEditor = editor;

            if (window.ZatoTooltip) {
                instance.tooltipInstance = ZatoTooltip.create(editorContainer.id, {
                    theme: 'dark'
                });
            }

            this.renderStatusbar(instance);
            this.updateStatusbar(instance);
        },

        getAceMode: function(language) {
            var modeMap = {
                'python': 'ace/mode/python',
                'javascript': 'ace/mode/javascript',
                'json': 'ace/mode/json',
                'xml': 'ace/mode/xml',
                'html': 'ace/mode/html',
                'css': 'ace/mode/css',
                'sql': 'ace/mode/sql',
                'yaml': 'ace/mode/yaml',
                'markdown': 'ace/mode/markdown',
                'text': 'ace/mode/text',
                'java': 'ace/mode/java',
                'rust': 'ace/mode/rust',
                'go': 'ace/mode/golang',
                'c': 'ace/mode/c_cpp',
                'cpp': 'ace/mode/c_cpp',
                'csharp': 'ace/mode/csharp',
                'ruby': 'ace/mode/ruby',
                'php': 'ace/mode/php',
                'swift': 'ace/mode/swift',
                'kotlin': 'ace/mode/kotlin',
                'scala': 'ace/mode/scala',
                'typescript': 'ace/mode/typescript',
                'tsx': 'ace/mode/tsx',
                'jsx': 'ace/mode/jsx',
                'shell': 'ace/mode/sh',
                'bash': 'ace/mode/sh',
                'powershell': 'ace/mode/powershell',
                'lua': 'ace/mode/lua',
                'perl': 'ace/mode/perl',
                'r': 'ace/mode/r',
                'dart': 'ace/mode/dart',
                'elixir': 'ace/mode/elixir',
                'erlang': 'ace/mode/erlang',
                'haskell': 'ace/mode/haskell',
                'clojure': 'ace/mode/clojure',
                'fsharp': 'ace/mode/fsharp',
                'ocaml': 'ace/mode/ocaml',
                'scss': 'ace/mode/scss',
                'sass': 'ace/mode/sass',
                'less': 'ace/mode/less',
                'dockerfile': 'ace/mode/dockerfile',
                'makefile': 'ace/mode/makefile',
                'ini': 'ace/mode/ini',
                'toml': 'ace/mode/toml',
                'properties': 'ace/mode/properties',
                'diff': 'ace/mode/diff',
                'gitignore': 'ace/mode/gitignore',
                'nginx': 'ace/mode/nginx',
                'apache': 'ace/mode/apache_conf'
            };
            return modeMap[language] || 'ace/mode/text';
        },

        isEditableFile: function(filename) {
            var ext = filename.split('.').pop().toLowerCase();
            var editableExtensions = [
                'py', 'pyw', 'pyi', 'js', 'mjs', 'jsx', 'ts', 'tsx',
                'json', 'xml', 'html', 'htm', 'css', 'scss', 'sass', 'less',
                'sql', 'yaml', 'yml', 'md', 'txt', 'rst', 'log', 'csv',
                'java', 'rs', 'go', 'c', 'h', 'cpp', 'cc', 'cxx', 'hpp',
                'cs', 'rb', 'php', 'swift', 'kt', 'kts', 'scala',
                'sh', 'bash', 'zsh', 'ps1', 'bat', 'cmd',
                'lua', 'pl', 'pm', 'r', 'R', 'dart',
                'ex', 'exs', 'erl', 'hrl', 'hs', 'lhs',
                'clj', 'cljs', 'fs', 'fsx', 'ml', 'mli',
                'ini', 'cfg', 'conf', 'toml', 'diff', 'patch',
                'gitignore', 'gitattributes', 'editorconfig',
                'makefile', 'dockerfile', 'svg'
            ];
            var editableFilenames = [
                'Makefile', 'makefile', 'Dockerfile', 'Vagrantfile',
                'Gemfile', 'Rakefile', 'Procfile', '.gitignore',
                '.gitattributes', '.editorconfig', '.env'
            ];
            if (editableFilenames.indexOf(filename) !== -1) {
                return true;
            }
            return editableExtensions.indexOf(ext) !== -1;
        },

        getLanguageFromExtension: function(filename) {
            var ext = filename.split('.').pop().toLowerCase();
            var extMap = {
                'py': 'python',
                'pyw': 'python',
                'pyi': 'python',
                'js': 'javascript',
                'mjs': 'javascript',
                'jsx': 'jsx',
                'ts': 'typescript',
                'tsx': 'tsx',
                'json': 'json',
                'xml': 'xml',
                'html': 'html',
                'htm': 'html',
                'css': 'css',
                'scss': 'scss',
                'sass': 'sass',
                'less': 'less',
                'sql': 'sql',
                'yaml': 'yaml',
                'yml': 'yaml',
                'md': 'markdown',
                'txt': 'text',
                'java': 'java',
                'rs': 'rust',
                'go': 'go',
                'c': 'c',
                'h': 'c',
                'cpp': 'cpp',
                'cc': 'cpp',
                'cxx': 'cpp',
                'hpp': 'cpp',
                'cs': 'csharp',
                'rb': 'ruby',
                'php': 'php',
                'swift': 'swift',
                'kt': 'kotlin',
                'kts': 'kotlin',
                'scala': 'scala',
                'sh': 'shell',
                'bash': 'bash',
                'zsh': 'shell',
                'ps1': 'powershell',
                'lua': 'lua',
                'pl': 'perl',
                'pm': 'perl',
                'r': 'r',
                'R': 'r',
                'dart': 'dart',
                'ex': 'elixir',
                'exs': 'elixir',
                'erl': 'erlang',
                'hrl': 'erlang',
                'hs': 'haskell',
                'lhs': 'haskell',
                'clj': 'clojure',
                'cljs': 'clojure',
                'fs': 'fsharp',
                'fsx': 'fsharp',
                'ml': 'ocaml',
                'mli': 'ocaml',
                'ini': 'ini',
                'cfg': 'ini',
                'conf': 'ini',
                'toml': 'toml',
                'diff': 'diff',
                'patch': 'diff'
            };
            return extMap[ext] || 'text';
        },

        renderStatusbar: function(instance) {
            var statusbar = instance.elements.statusbar;
            var items = [
                { id: 'position', text: 'Ln 1, Col 1' },
                { id: 'language', text: instance.options.language },
                { id: 'encoding', text: 'UTF-8' }
            ];

            var html = '';
            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                html += '<span class="zato-ide-editor-statusbar-item" data-item-id="' + item.id + '">' + item.text + '</span>';
            }
            statusbar.innerHTML = html;
        },

        updateStatusbar: function(instance) {
            var editor = instance.aceEditor;
            if (!editor) return;

            var cursor = editor.getCursorPosition();
            var line = cursor.row + 1;
            var col = cursor.column + 1;

            instance.cursorLine = line;
            instance.cursorCol = col;

            var posItem = instance.elements.statusbar.querySelector('[data-item-id="position"]');
            if (posItem) {
                posItem.textContent = 'Ln ' + line + ', Col ' + col;
            }
        },

        setupCallbacks: function(instance) {
            var self = this;
            var editor = instance.aceEditor;
            var opts = instance.options;

            editor.session.on('change', function() {
                instance.content = editor.getValue();
                if (opts.onContentChange) {
                    opts.onContentChange(instance.content);
                }
            });

            editor.selection.on('changeCursor', function() {
                self.updateStatusbar(instance);
                if (opts.onCursorChange) {
                    opts.onCursorChange(instance.cursorLine, instance.cursorCol);
                }
            });

            editor.on('focus', function() {
                instance.focused = true;
            });

            editor.on('blur', function() {
                instance.focused = false;
            });
        },

        getValue: function(instance) {
            return instance.aceEditor ? instance.aceEditor.getValue() : instance.content;
        },

        setValue: function(instance, value) {
            instance.content = value;
            if (instance.aceEditor) {
                this.applyUnusedMarkers(instance.aceEditor, []);
                var cursorPos = instance.aceEditor.getCursorPosition();
                instance.aceEditor.setValue(value, -1);
                instance.aceEditor.moveCursorToPosition(cursorPos);
            }
        },

        setLanguage: function(instance, language) {
            console.log('[ZatoIDEEditorAce] setLanguage: language=' + language + ', previous=' + instance.options.language);
            instance.options.language = language;
            if (instance.aceEditor) {
                console.log('[ZatoIDEEditorAce] setLanguage: setting mode to ' + this.getAceMode(language));
                instance.aceEditor.session.setMode(this.getAceMode(language));
                if (language !== 'python') {
                    console.log('[ZatoIDEEditorAce] setLanguage: clearing annotations for non-python');
                    instance.aceEditor.session.setAnnotations([]);
                }
            }
            var langItem = instance.elements.statusbar.querySelector('[data-item-id="language"]');
            if (langItem) {
                langItem.textContent = language;
            }
        },

        focus: function(instance) {
            if (instance.aceEditor) {
                instance.aceEditor.focus();
            }
        },

        resize: function(instance) {
            if (instance.aceEditor) {
                instance.aceEditor.resize();
            }
        },

        scrollToLine: function(instance, line) {
            if (instance.aceEditor) {
                instance.aceEditor.scrollToLine(line - 1, true, true);
                instance.aceEditor.gotoLine(line, 0, true);
            }
        },

        getCursorPosition: function(instance) {
            if (instance.aceEditor) {
                var pos = instance.aceEditor.getCursorPosition();
                return { line: pos.row + 1, col: pos.column + 1 };
            }
            return { line: 1, col: 1 };
        },

        destroy: function(instance) {
            if (instance.aceEditor) {
                instance.aceEditor.destroy();
                instance.aceEditor = null;
            }
            if (instance.elements.wrapper && instance.elements.wrapper.parentNode) {
                instance.elements.wrapper.parentNode.removeChild(instance.elements.wrapper);
            }
        },

        lintPython: function(editor, callback) {
            var code = editor.getValue();
            if (!code.trim()) {
                editor.session.setAnnotations([]);
                if (callback) {
                    callback();
                }
                return;
            }

            var csrfToken = this.getCsrfToken();
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/zato/ide/lint/python/', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            if (csrfToken) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
            }
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        try {
                            var response = JSON.parse(xhr.responseText);
                            console.log('[Lint] response:', JSON.stringify(response));
                            if (response.success && response.annotations) {
                                editor.session.setAnnotations(response.annotations);
                            }
                            console.log('[Lint] markers:', JSON.stringify(response.markers));
                            ZatoIDEEditorAce.applyUnusedMarkers(editor, response.markers || []);
                        } catch (e) {
                            console.warn('[Lint] Failed to parse response:', e);
                        }
                    }
                    if (callback) {
                        callback();
                    }
                }
            };
            xhr.send(JSON.stringify({ code: code }));
        },

        unusedMarkerIds: [],

        unusedMarkerRanges: [],
        unusedHoverBound: false,
        unusedTooltipInstance: null,

        applyUnusedMarkers: function(editor, markers) {
            console.log('[Lint] applyUnusedMarkers: START, markers.length=' + markers.length);
            var session = editor.session;
            console.log('[Lint] applyUnusedMarkers: session=' + (session ? 'exists' : 'null'));
            var Range = ace.require('ace/range').Range;
            console.log('[Lint] applyUnusedMarkers: Range=' + (Range ? 'exists' : 'null'));

            console.log('[Lint] applyUnusedMarkers: removing old markers, count=' + this.unusedMarkerIds.length);
            for (var i = 0; i < this.unusedMarkerIds.length; i++) {
                session.removeMarker(this.unusedMarkerIds[i]);
            }
            this.unusedMarkerIds = [];
            this.unusedMarkerRanges = [];

            for (var i = 0; i < markers.length; i++) {
                var m = markers[i];
                console.log('[Lint] applyUnusedMarkers: marker ' + i + ': startRow=' + m.startRow + ' startCol=' + m.startCol + ' endRow=' + m.endRow + ' endCol=' + m.endCol + ' message=' + m.message);
                var range = new Range(m.startRow, m.startCol, m.endRow, m.endCol);
                console.log('[Lint] applyUnusedMarkers: range created: ' + JSON.stringify({start: range.start, end: range.end}));
                var markerId = session.addMarker(range, 'ace_unused_variable', 'text', true);
                console.log('[Lint] applyUnusedMarkers: markerId=' + markerId);
                this.unusedMarkerIds.push(markerId);
                this.unusedMarkerRanges.push({
                    range: range,
                    message: m.message || 'Unused'
                });
            }
            console.log('[Lint] applyUnusedMarkers: END, total markers added=' + this.unusedMarkerIds.length);
            console.log('[Lint] applyUnusedMarkers: unusedMarkerRanges.length=' + this.unusedMarkerRanges.length);

            this.setupUnusedHover(editor);
        },

        setupUnusedHover: function(editor) {
            console.log('[Tooltip] setupUnusedHover: START');
            console.log('[Tooltip] setupUnusedHover: unusedHoverBound=' + this.unusedHoverBound);
            console.log('[Tooltip] setupUnusedHover: ZatoTooltip=' + (typeof ZatoTooltip));
            console.log('[Tooltip] setupUnusedHover: editor=' + (editor ? 'exists' : 'null'));
            console.log('[Tooltip] setupUnusedHover: editor.container=' + (editor.container ? 'exists' : 'null'));
            console.log('[Tooltip] setupUnusedHover: editor.container.id=' + (editor.container ? editor.container.id : 'N/A'));

            if (this.unusedHoverBound) {
                console.log('[Tooltip] setupUnusedHover: already bound, skipping');
                return;
            }
            this.unusedHoverBound = true;
            console.log('[Tooltip] setupUnusedHover: setting unusedHoverBound=true');

            var self = this;

            if (typeof ZatoTooltip !== 'undefined' && !this.unusedTooltipInstance) {
                console.log('[Tooltip] setupUnusedHover: creating ZatoTooltip instance');
                this.unusedTooltipInstance = ZatoTooltip.create(editor.container.id, { theme: 'dark' });
                console.log('[Tooltip] setupUnusedHover: unusedTooltipInstance=' + JSON.stringify(this.unusedTooltipInstance ? 'created' : 'null'));
            } else {
                console.log('[Tooltip] setupUnusedHover: ZatoTooltip not available or instance already exists');
            }

            var lastMessage = null;
            var lastRow = -1;
            var lastCol = -1;
            var tooltipHovered = false;
            var tooltipLocked = false;

            if (self.unusedTooltipInstance && self.unusedTooltipInstance.tooltipEl) {
                var tooltipEl = self.unusedTooltipInstance.tooltipEl;
                tooltipEl.style.pointerEvents = 'auto';
                tooltipEl.style.userSelect = 'text';
                tooltipEl.style.cursor = 'pointer';

                tooltipEl.addEventListener('mouseenter', function() {
                    console.log('[Tooltip] tooltipEl mouseenter');
                    tooltipHovered = true;
                });

                tooltipEl.addEventListener('mouseleave', function() {
                    console.log('[Tooltip] tooltipEl mouseleave, tooltipLocked=' + tooltipLocked);
                    if (tooltipLocked) {
                        return;
                    }
                    tooltipHovered = false;
                    lastMessage = null;
                    ZatoTooltip.hide(self.unusedTooltipInstance);
                });

                tooltipEl.addEventListener('click', function() {
                    console.log('[Tooltip] tooltipEl click');
                    var textToCopy = tooltipEl.textContent;
                    var originalLeft = parseFloat(tooltipEl.style.left);
                    var originalTop = parseFloat(tooltipEl.style.top);
                    var originalRect = tooltipEl.getBoundingClientRect();
                    var originalCenterX = originalRect.left + (originalRect.width / 2);

                    navigator.clipboard.writeText(textToCopy).then(function() {
                        console.log('[Tooltip] copied to clipboard: ' + textToCopy);
                        tooltipLocked = true;
                        tooltipEl.textContent = 'Copied to clipboard';

                        var newRect = tooltipEl.getBoundingClientRect();
                        var newLeft = originalCenterX - (newRect.width / 2);
                        tooltipEl.style.left = newLeft + 'px';
                        tooltipEl.style.top = originalTop + 'px';

                        console.log('[Tooltip] showing Copied to clipboard message at left=' + newLeft);
                        setTimeout(function() {
                            console.log('[Tooltip] hiding after copied message');
                            tooltipLocked = false;
                            tooltipHovered = false;
                            lastMessage = null;
                            tooltipEl.style.opacity = '0';
                            tooltipEl.style.visibility = 'hidden';
                        }, 350);
                    }).catch(function(err) {
                        console.log('[Tooltip] clipboard write failed: ' + err);
                    });
                });
            }

            console.log('[Tooltip] setupUnusedHover: adding mousemove listener to editor');
            editor.on('mousemove', function(e) {
                var pos = e.getDocumentPosition();
                var row = pos.row;
                var col = pos.column;

                if (row === lastRow && col === lastCol) {
                    return;
                }
                lastRow = row;
                lastCol = col;

                var foundMessage = null;
                var foundRange = null;
                console.log('[Tooltip] mousemove: row=' + row + ' col=' + col + ' unusedMarkerRanges.length=' + self.unusedMarkerRanges.length);

                var lineLength = editor.session.getLine(row).length;
                console.log('[Tooltip] mousemove: lineLength=' + lineLength);

                if (col > lineLength) {
                    console.log('[Tooltip] mousemove: col > lineLength, skipping');
                } else {
                    for (var i = 0; i < self.unusedMarkerRanges.length; i++) {
                        var item = self.unusedMarkerRanges[i];
                        var r = item.range;
                        console.log('[Tooltip] mousemove: checking range ' + i + ': startRow=' + r.start.row + ' startCol=' + r.start.column + ' endRow=' + r.end.row + ' endCol=' + r.end.column);
                        if (row === r.start.row && col >= r.start.column && col < r.end.column) {
                            foundMessage = item.message;
                            foundRange = r;
                            console.log('[Tooltip] mousemove: MATCH! message=' + foundMessage);
                            break;
                        }
                    }
                }

                if (foundMessage && foundMessage !== lastMessage) {
                    console.log('[Tooltip] mousemove: showing tooltip, message=' + foundMessage);
                    lastMessage = foundMessage;
                    if (self.unusedTooltipInstance && self.unusedTooltipInstance.tooltipEl) {
                        var coords = editor.renderer.textToScreenCoordinates(row, col);
                        console.log('[Tooltip] mousemove: coords=' + JSON.stringify(coords));

                        var tooltipEl = self.unusedTooltipInstance.tooltipEl;
                        tooltipEl.textContent = foundMessage;
                        tooltipEl.style.display = 'block';
                        var tooltipRect = tooltipEl.getBoundingClientRect();

                        var tooltipWidth = tooltipRect.width;
                        var left = coords.pageX - (tooltipWidth / 2);
                        if (left < 5) {
                            left = 5;
                        }
                        var top = coords.pageY - tooltipRect.height - 2;
                        if (top < 5) {
                            top = coords.pageY + 20;
                        }
                        console.log('[Tooltip] mousemove: positioning ABOVE text, left=' + left + ' top=' + top);

                        tooltipEl.style.left = left + 'px';
                        tooltipEl.style.top = top + 'px';
                        tooltipEl.style.opacity = '1';
                        tooltipEl.style.visibility = 'visible';
                        console.log('[Tooltip] mousemove: tooltip shown at left=' + left + ' top=' + top);
                    } else {
                        console.log('[Tooltip] mousemove: no unusedTooltipInstance or tooltipEl');
                    }
                } else if (!foundMessage && lastMessage && !tooltipHovered) {
                    if (self.unusedTooltipInstance && self.unusedTooltipInstance.tooltipEl) {
                        var tooltipEl = self.unusedTooltipInstance.tooltipEl;
                        var rect = tooltipEl.getBoundingClientRect();
                        var mouseCoords = editor.renderer.textToScreenCoordinates(row, col);
                        console.log('[Tooltip] mousemove: checking if mouse near tooltip, mouseY=' + mouseCoords.pageY + ' rect.bottom=' + rect.bottom);
                        if (mouseCoords.pageY >= rect.top - 5 && mouseCoords.pageY <= rect.bottom + 20) {
                            console.log('[Tooltip] mousemove: mouse is near tooltip area, not hiding');
                            return;
                        }
                    }
                    console.log('[Tooltip] mousemove: hiding tooltip');
                    lastMessage = null;
                    if (self.unusedTooltipInstance) {
                        try {
                            ZatoTooltip.hide(self.unusedTooltipInstance);
                            console.log('[Tooltip] mousemove: ZatoTooltip.hide called');
                        } catch (err) {
                            console.log('[Tooltip] mousemove: ZatoTooltip.hide ERROR: ' + err.message);
                        }
                    }
                }
            });

            console.log('[Tooltip] setupUnusedHover: adding mouseleave listener to editor.container');
            editor.container.addEventListener('mouseleave', function(e) {
                console.log('[Tooltip] mouseleave: tooltipHovered=' + tooltipHovered);
                if (tooltipHovered) {
                    console.log('[Tooltip] mouseleave: tooltip is hovered, not hiding');
                    return;
                }
                if (self.unusedTooltipInstance && self.unusedTooltipInstance.tooltipEl) {
                    var tooltipEl = self.unusedTooltipInstance.tooltipEl;
                    var rect = tooltipEl.getBoundingClientRect();
                    var mouseX = e.clientX;
                    var mouseY = e.clientY;
                    console.log('[Tooltip] mouseleave: mouseX=' + mouseX + ' mouseY=' + mouseY + ' rect=' + JSON.stringify({left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom}));
                    if (mouseX >= rect.left - 10 && mouseX <= rect.right + 10 && mouseY >= rect.top - 10 && mouseY <= rect.bottom + 10) {
                        console.log('[Tooltip] mouseleave: mouse is heading to tooltip, not hiding');
                        return;
                    }
                }
                console.log('[Tooltip] mouseleave: hiding tooltip');
                lastMessage = null;
                lastRow = -1;
                lastCol = -1;
                if (self.unusedTooltipInstance) {
                    try {
                        ZatoTooltip.hide(self.unusedTooltipInstance);
                        console.log('[Tooltip] mouseleave: ZatoTooltip.hide called');
                    } catch (err) {
                        console.log('[Tooltip] mouseleave: ZatoTooltip.hide ERROR: ' + err.message);
                    }
                }
            });

            console.log('[Tooltip] setupUnusedHover: END');
        },

        getCsrfToken: function() {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.indexOf('csrftoken=') === 0) {
                    return cookie.substring('csrftoken='.length);
                }
            }
            return null;
        },

        storageNamespace: 'zato-ide-editor',

        getStorageKey: function(instance) {
            var pageId = instance.options.storageId || window.location.pathname;
            return this.storageNamespace + ':' + pageId;
        },

        saveState: function(instance) {
            var editor = instance.aceEditor;
            if (!editor) return;

            var session = editor.session;
            var state = {
                content: editor.getValue(),
                cursor: editor.getCursorPosition(),
                selection: editor.getSelectionRange(),
                scroll: {
                    top: session.getScrollTop(),
                    left: session.getScrollLeft()
                },
                folds: session.getAllFolds().map(function(fold) {
                    return {
                        start: { row: fold.start.row, column: fold.start.column },
                        end: { row: fold.end.row, column: fold.end.column }
                    };
                }),
                undoStack: session.getUndoManager().$undoStack,
                redoStack: session.getUndoManager().$redoStack,
                tabSize: session.getTabSize(),
                useSoftTabs: session.getUseSoftTabs(),
                fontSize: editor.getFontSize(),
                bookmarks: session.getBreakpoints(),
                searchOptions: editor.$search ? {
                    needle: editor.$search.$options.needle,
                    caseSensitive: editor.$search.$options.caseSensitive,
                    wholeWord: editor.$search.$options.wholeWord,
                    regExp: editor.$search.$options.regExp
                } : null,
                autocompleteOpen: editor.completer && editor.completer.activated,
                autocompletePos: editor.completer && editor.completer.activated ? editor.getCursorPosition() : null,
                timestamp: Date.now()
            };

            try {
                localStorage.setItem(this.getStorageKey(instance), JSON.stringify(state));
            } catch (e) {
                console.warn('[IDE] Failed to save state:', e);
            }
        },

        loadState: function(instance) {
            var editor = instance.aceEditor;
            if (!editor) return false;

            var key = this.getStorageKey(instance);
            var stored = localStorage.getItem(key);
            if (!stored) return false;

            try {
                var state = JSON.parse(stored);
                var session = editor.session;

                if (state.content !== undefined) {
                    editor.setValue(state.content, -1);
                }

                if (state.undoStack) {
                    var undoManager = session.getUndoManager();
                    undoManager.$undoStack = state.undoStack;
                    undoManager.$redoStack = state.redoStack || [];
                }

                if (state.folds && state.folds.length > 0) {
                    state.folds.forEach(function(fold) {
                        try {
                            session.addFold('...', new ace.Range(fold.start.row, fold.start.column, fold.end.row, fold.end.column));
                        } catch (e) {}
                    });
                }

                if (state.cursor) {
                    editor.moveCursorToPosition(state.cursor);
                }

                if (state.selection) {
                    editor.selection.setSelectionRange(state.selection);
                }

                if (state.scroll) {
                    session.setScrollTop(state.scroll.top);
                    session.setScrollLeft(state.scroll.left);
                }

                if (state.tabSize) {
                    session.setTabSize(state.tabSize);
                }

                if (state.useSoftTabs !== undefined) {
                    session.setUseSoftTabs(state.useSoftTabs);
                }

                if (state.fontSize) {
                    editor.setFontSize(state.fontSize);
                }

                if (state.bookmarks && state.bookmarks.length > 0) {
                    state.bookmarks.forEach(function(bp, row) {
                        if (bp) {
                            session.setBreakpoint(row, bp);
                        }
                    });
                }

                if (state.searchOptions && state.searchOptions.needle) {
                    editor.$search.$options.needle = state.searchOptions.needle;
                    editor.$search.$options.caseSensitive = state.searchOptions.caseSensitive;
                    editor.$search.$options.wholeWord = state.searchOptions.wholeWord;
                    editor.$search.$options.regExp = state.searchOptions.regExp;
                }

                if (state.autocompleteOpen && state.autocompletePos) {
                    setTimeout(function() {
                        editor.moveCursorToPosition(state.autocompletePos);
                        editor.execCommand('startAutocomplete');
                    }, 100);
                }

                return true;
            } catch (e) {
                console.warn('[IDE] Failed to load state:', e);
                return false;
            }
        },

        clearState: function(instance) {
            try {
                localStorage.removeItem(this.getStorageKey(instance));
            } catch (e) {}
        },

        setupAutoSave: function(instance) {
            var self = this;
            var editor = instance.aceEditor;
            if (!editor) return;

            var saveTimeout = null;
            var saveDelay = 500;

            var triggerSave = function() {
                if (saveTimeout) {
                    clearTimeout(saveTimeout);
                }
                saveTimeout = setTimeout(function() {
                    self.saveState(instance);
                }, saveDelay);
            };

            editor.session.on('change', triggerSave);
            editor.session.on('changeFold', triggerSave);
            editor.session.on('changeScrollTop', triggerSave);
            editor.session.on('changeScrollLeft', triggerSave);
            editor.selection.on('changeCursor', triggerSave);
            editor.selection.on('changeSelection', triggerSave);

            window.addEventListener('beforeunload', function() {
                self.saveState(instance);
            });
        }
    };

    window.ZatoIDEEditorAce = ZatoIDEEditorAce;

})();
