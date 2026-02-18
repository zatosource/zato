(function() {
    'use strict';

    /**
     * ZatoIDE - reusable text editor component with theme support.
     *
     * Usage:
     *   var instance = ZatoIDE.create('my-container-id', {
     *       theme: 'dark',
     *       language: 'python',
     *       fontSize: 13,
     *       tabSize: 4
     *   });
     *
     *   ZatoIDE.setValue(instance, 'print("Hello")');
     *   var code = ZatoIDE.getValue(instance);
     *   ZatoIDE.setTheme(instance, 'light');
     *   ZatoIDE.destroy('my-container-id');
     *
     * The container element must exist in the DOM before calling create().
     * The editor renders a toolbar, tabs area, editor textarea, and status bar.
     * Toolbar and tabs are placeholders for future implementation.
     *
     * Themes are applied via CSS classes: .zato-ide-theme-dark, .zato-ide-theme-light
     * Theme CSS files define CSS variables for colors.
     *
     * localStorage key: none (editor content is not persisted automatically)
     */
    var ZatoIDE = {

        /**
         * Default options for new IDE instances.
         * @property {string} theme - theme name, maps to .zato-ide-theme-{name} CSS class
         * @property {string} language - language for syntax highlighting (future)
         * @property {number} fontSize - editor font size in pixels
         * @property {number} tabSize - number of spaces inserted when Tab is pressed
         * @property {boolean} lineNumbers - whether to show line numbers (future)
         */
        defaultOptions: {
            theme: 'dark',
            language: 'python',
            fontSize: 13,
            tabSize: 4,
            lineNumbers: true
        },

        /**
         * Map of container ID to instance object.
         * Used to retrieve instances later via getInstance().
         */
        instances: {},

        /**
         * Creates a new IDE instance in the specified container.
         *
         * @param {string} containerId - ID of the DOM element to render into
         * @param {Object} options - configuration options (see defaultOptions)
         * @returns {Object|null} instance object, or null if container not found
         *
         * The returned instance object contains:
         *   - id: the container ID
         *   - container: the DOM element
         *   - options: merged options
         *   - editor: the textarea element
         *   - content: current editor content
         */
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

        /**
         * Renders the IDE HTML structure into the instance container.
         * Called automatically by create(). Structure:
         *   - .zato-ide-container (with theme class)
         *     - .zato-ide-toolbar (left: dropdown placeholder, right: switch placeholder)
         *     - .zato-ide-tabs-area (placeholder for ZatoTabsManager)
         *     - .zato-ide-editor-area
         *       - textarea.zato-ide-editor
         *     - .zato-ide-statusbar (left: line/col, right: language, encoding)
         *
         * @param {Object} instance - the IDE instance object
         */
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

        /**
         * Binds event listeners to the editor textarea.
         * Handles: input, keyup, click (for status bar updates), Tab key (inserts spaces).
         *
         * @param {Object} instance - the IDE instance object
         */
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

        /**
         * Updates the status bar with current cursor position (line and column).
         * Called automatically on input, keyup, and click events.
         *
         * @param {Object} instance - the IDE instance object
         */
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

        /**
         * Gets the current editor content.
         *
         * @param {Object} instance - the IDE instance object
         * @returns {string} the editor content, or empty string if instance is invalid
         */
        getValue: function(instance) {
            if (instance && instance.editor) {
                return instance.editor.value;
            }
            return '';
        },

        /**
         * Sets the editor content.
         *
         * @param {Object} instance - the IDE instance object
         * @param {string} value - the content to set
         */
        setValue: function(instance, value) {
            if (instance && instance.editor) {
                instance.editor.value = value;
                instance.content = value;
                this.updateStatusBar(instance);
            }
        },

        /**
         * Changes the editor theme.
         * Updates the CSS class on .zato-ide-container to .zato-ide-theme-{theme}.
         *
         * @param {Object} instance - the IDE instance object
         * @param {string} theme - theme name (e.g., 'dark', 'light')
         */
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

        /**
         * Retrieves an existing IDE instance by container ID.
         *
         * @param {string} containerId - ID of the container element
         * @returns {Object|null} the instance object, or null if not found
         */
        getInstance: function(containerId) {
            return this.instances[containerId] || null;
        },

        /**
         * Destroys an IDE instance and clears its container.
         * Removes the instance from the internal registry.
         *
         * @param {string} containerId - ID of the container element
         */
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
