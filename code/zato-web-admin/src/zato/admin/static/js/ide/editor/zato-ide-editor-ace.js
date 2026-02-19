(function() {
    'use strict';

    var ZatoIDEEditorAce = {

        defaults: {
            theme: 'dark',
            language: 'python',
            fontSize: 13,
            tabSize: 4
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
            editor.renderer.setScrollMargin(7, 7, 0, 0);
            editor.renderer.$gutterLayer.$fixedWidth = true;
            editor.renderer.$gutterLayer.gutterWidth = 50;

            if (instance.content) {
                editor.setValue(instance.content, -1);
            }

            instance.aceEditor = editor;

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
        }
    };

    window.ZatoIDEEditorAce = ZatoIDEEditorAce;

})();
