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

            this.setupCompletion(editor);
            this.setupLinting(editor, instance, opts);
            this.setupIndentDots(editor);
            this.setupGutterAnnotationClick(editor, instance);
            this.setupGotoDefinition(editor, instance);

            editor.renderer.setScrollMargin(7, 7, 0, 0);
            editor.renderer.$gutterLayer.$fixedWidth = true;
            editor.renderer.$gutterLayer.gutterWidth = 50;
            editor.container.style.lineHeight = '1.32';

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

        setupIndentDots: function(editor) {
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
        },

        setupGutterAnnotationClick: function(editor, instance) {
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

            editor.session.on('changeScrollTop', function() {
                if (opts.onScrollChange) {
                    opts.onScrollChange(editor.getFirstVisibleRow());
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
        }
    };

    window.ZatoIDEEditorAce = ZatoIDEEditorAce;

})();
