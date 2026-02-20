(function() {
    'use strict';

    var ZatoIDEEditorAce = {

        defaults: {
            theme: 'dark',
            language: 'python',
            fontSize: 12,
            tabSize: 4,
            lintDelay: 125
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

            var statusbar = document.createElement('div');
            statusbar.className = 'zato-ide-editor-statusbar zato-ide-ace-statusbar';

            wrapper.appendChild(editorContainer);
            wrapper.appendChild(statusbar);
            container.appendChild(wrapper);

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
            editor.setShowPrintMargin(false);
            editor.setHighlightActiveLine(true);
            editor.setHighlightSelectedWord(true);
            editor.setDisplayIndentGuides(false);
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
            var lintLanguage = opts.language;
            var lintDelay = opts.lintDelay;
            editor.session.on('change', function() {
                if (lintLanguage !== 'python') {
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
            instance.lintLanguage = lintLanguage;
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

            setTimeout(function() {
                editor.resize();
            }, 0);
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
                'text': 'ace/mode/text'
            };
            return modeMap[language] || 'ace/mode/text';
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
                var cursorPos = instance.aceEditor.getCursorPosition();
                instance.aceEditor.setValue(value, -1);
                instance.aceEditor.moveCursorToPosition(cursorPos);
            }
        },

        setLanguage: function(instance, language) {
            instance.options.language = language;
            if (instance.aceEditor) {
                instance.aceEditor.session.setMode(this.getAceMode(language));
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
                            if (response.success && response.annotations) {
                                editor.session.setAnnotations(response.annotations);
                            }
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

        getCsrfToken: function() {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.indexOf('csrftoken=') === 0) {
                    return cookie.substring('csrftoken='.length);
                }
            }
            return null;
        }
    };

    window.ZatoIDEEditorAce = ZatoIDEEditorAce;

})();
