(function() {
    'use strict';

    var ZatoIDE = {

        defaultOptions: {
            theme: 'dark',
            language: 'python',
            fontSize: 13,
            tabSize: 4,
            lineNumbers: true
        },

        instances: {},

        create: function(containerId, options) {
            var opts = {};
            var key;
            for (key in this.defaultOptions) {
                opts[key] = this.defaultOptions[key];
            }
            for (key in options) {
                opts[key] = options[key];
            }

            var container = document.getElementById(containerId);
            if (!container) {
                console.error('ZatoIDE: container not found:', containerId);
                return null;
            }

            var instance = {
                id: containerId,
                container: container,
                options: opts,
                editor: null,
                content: ''
            };

            this.render(instance);
            this.instances[containerId] = instance;

            return instance;
        },

        render: function(instance) {
            var themeClass = 'zato-ide-theme-' + instance.options.theme;
            var html = '';

            html += '<div class="zato-ide-container ' + themeClass + '">';

            html += '<div class="zato-ide-toolbar">';
            html += '<div class="zato-ide-toolbar-left">';
            html += '<span class="zato-ide-toolbar-placeholder">[Dropdown placeholder]</span>';
            html += '</div>';
            html += '<div class="zato-ide-toolbar-right">';
            html += '<span class="zato-ide-toolbar-placeholder">[Switch placeholder]</span>';
            html += '</div>';
            html += '</div>';

            html += '<div class="zato-ide-tabs-area">';
            html += '<span class="zato-ide-tabs-placeholder">[Tabs via ZatoTabsManager]</span>';
            html += '</div>';

            html += '<div class="zato-ide-editor-area">';
            html += '<textarea class="zato-ide-editor" spellcheck="false"></textarea>';
            html += '</div>';

            html += '<div class="zato-ide-statusbar">';
            html += '<div class="zato-ide-statusbar-left">';
            html += '<span class="zato-ide-statusbar-item">Ln 1, Col 1</span>';
            html += '</div>';
            html += '<div class="zato-ide-statusbar-right">';
            html += '<span class="zato-ide-statusbar-item">Python</span>';
            html += '<span class="zato-ide-statusbar-item">UTF-8</span>';
            html += '</div>';
            html += '</div>';

            html += '</div>';

            instance.container.innerHTML = html;
            instance.editor = instance.container.querySelector('.zato-ide-editor');

            this.bindEvents(instance);
        },

        bindEvents: function(instance) {
            var self = this;

            if (instance.editor) {
                instance.editor.addEventListener('input', function() {
                    instance.content = instance.editor.value;
                    self.updateStatusBar(instance);
                });

                instance.editor.addEventListener('keyup', function() {
                    self.updateStatusBar(instance);
                });

                instance.editor.addEventListener('click', function() {
                    self.updateStatusBar(instance);
                });

                instance.editor.addEventListener('keydown', function(e) {
                    if (e.key === 'Tab') {
                        e.preventDefault();
                        var start = instance.editor.selectionStart;
                        var end = instance.editor.selectionEnd;
                        var spaces = '';
                        for (var i = 0; i < instance.options.tabSize; i++) {
                            spaces += ' ';
                        }
                        instance.editor.value = instance.editor.value.substring(0, start) + spaces + instance.editor.value.substring(end);
                        instance.editor.selectionStart = instance.editor.selectionEnd = start + instance.options.tabSize;
                        instance.content = instance.editor.value;
                    }
                });
            }
        },

        updateStatusBar: function(instance) {
            var editor = instance.editor;
            if (!editor) {
                return;
            }

            var value = editor.value;
            var selectionStart = editor.selectionStart;

            var lines = value.substring(0, selectionStart).split('\n');
            var lineNumber = lines.length;
            var columnNumber = lines[lines.length - 1].length + 1;

            var statusLeft = instance.container.querySelector('.zato-ide-statusbar-left');
            if (statusLeft) {
                statusLeft.innerHTML = '<span class="zato-ide-statusbar-item">Ln ' + lineNumber + ', Col ' + columnNumber + '</span>';
            }
        },

        getValue: function(instance) {
            if (instance && instance.editor) {
                return instance.editor.value;
            }
            return '';
        },

        setValue: function(instance, value) {
            if (instance && instance.editor) {
                instance.editor.value = value;
                instance.content = value;
                this.updateStatusBar(instance);
            }
        },

        setTheme: function(instance, theme) {
            if (!instance) {
                return;
            }
            instance.options.theme = theme;
            var container = instance.container.querySelector('.zato-ide-container');
            if (container) {
                container.className = 'zato-ide-container zato-ide-theme-' + theme;
            }
        },

        getInstance: function(containerId) {
            return this.instances[containerId] || null;
        },

        destroy: function(containerId) {
            var instance = this.instances[containerId];
            if (instance) {
                instance.container.innerHTML = '';
                delete this.instances[containerId];
            }
        }
    };

    window.ZatoIDE = ZatoIDE;

})();
