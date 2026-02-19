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
                codeEditor: null,
                content: '',
                files: {},
                activeFile: null
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
            html += '<select id="' + instance.id + '-symbol-select" class="zato-ide-symbol-select">';
            html += '<option value="">-- symbols --</option>';
            html += '</select>';
            html += '</div>';
            html += '<div class="zato-ide-toolbar-right">';
            html += '<span class="zato-ide-search-button" title="Search"></span>';
            html += '</div>';
            html += '</div>';

            html += '<div class="zato-ide-tabs-area">';
            html += '<div id="' + instance.id + '-tabs">';
            html += '</div>';
            html += '</div>';

            html += '<div class="zato-ide-editor-area" id="' + instance.id + '-editor-area">';
            html += '</div>';

            html += '</div>';

            instance.container.innerHTML = html;

            console.log('[ZatoIDE] render: container set, initializing files');
            this.initFiles(instance);
            console.log('[ZatoIDE] render: files initialized, initializing code editor');
            this.initCodeEditor(instance);
            console.log('[ZatoIDE] render: code editor initialized');

            var self = this;
            var symbolSelect = document.getElementById(instance.id + '-symbol-select');
            if (symbolSelect && typeof ZatoDropdown !== 'undefined') {
                instance.symbolDropdown = ZatoDropdown.init(symbolSelect, {
                    theme: instance.options.theme,
                    id: instance.id + '-symbol-dropdown',
                    onBeforeOpen: function(container) {
                        var menu = container.querySelector('.zato-dropdown-menu');
                        var trigger = container.querySelector('.zato-dropdown-trigger');
                        if (menu && trigger) {
                            var rect = trigger.getBoundingClientRect();
                            menu.style.position = 'fixed';
                            menu.style.bottom = 'auto';
                            menu.style.left = rect.left + 'px';
                            menu.style.top = (rect.bottom + 2) + 'px';
                            menu.style.minWidth = rect.width + 'px';
                        }
                    },
                    onChange: function(value, text) {
                        if (value) {
                            var line = parseInt(value, 10);
                            self.jumpToLine(instance, line);
                        }
                    }
                });

            }

            console.log('[ZatoIDE] render: initializing tabs');
            this.initTabs(instance);

            this.loadSearchIcon(instance);

            this.bindEvents(instance);

            console.log('[ZatoIDE] render: switching to initial file my_service.py');
            this.switchToFile(instance, 'my_service.py');
            console.log('[ZatoIDE] render: complete');
        },

        /**
         * Initializes sample files with content.
         */
        initFiles: function(instance) {
            instance.files = {
                'my_service.py': {
                    content: '# -*- coding: utf-8 -*-\n\n# Zato\nfrom zato.server.service import Service\n\nclass MyService(Service):\n\n    def handle(self):\n\n        # Connect to a Microsoft 365 IMAP connection by its name ..\n        conn = self.email.imap.get(\'My Automation\').conn\n\n        # .. get all messages matching filter criteria ("unread" by default)..\n        for msg_id, msg in conn.get():\n\n            # .. and access each of them.\n            self.logger.info(msg.data)\n\n\nclass MyService2(Service):\n\n    def handle(self):\n        pass\n\n\nclass MyService3(Service):\n\n    def handle(self):\n        pass\n',
                    language: 'python'
                },
                'queries.sql': {
                    content: '-- Database queries\n\nSELECT id, name, created_at\nFROM users\nWHERE status = \'active\'\nORDER BY created_at DESC\nLIMIT 100;\n\n-- Insert new record\nINSERT INTO logs (message, level)\nVALUES (\'Application started\', \'INFO\');\n',
                    language: 'sql'
                },
                'config.yaml': {
                    content: '# Configuration file\n\nserver:\n  host: localhost\n  port: 8080\n  debug: true\n\ndatabase:\n  engine: postgresql\n  name: myapp\n  pool_size: 10\n',
                    language: 'yaml'
                },
                'data.json': {
                    content: '{\n  "name": "My Application",\n  "version": "1.0.0",\n  "settings": {\n    "enabled": true,\n    "maxItems": 100,\n    "tags": ["production", "api"]\n  }\n}\n',
                    language: 'json'
                },
                'settings.ini': {
                    content: '; Application settings\n\n[general]\nname = MyApp\nversion = 1.0\n\n[logging]\nlevel = INFO\nformat = %(asctime)s - %(message)s\n\n[features]\nenable_cache = true\nmax_connections = 50\n',
                    language: 'ini'
                }
            };
            instance.activeFile = 'my_service.py';
        },

        /**
         * Initializes the code editor component.
         */
        initCodeEditor: function(instance) {
            console.log('[ZatoIDE] initCodeEditor: starting, instance.id=' + instance.id);
            var self = this;
            var editorArea = document.getElementById(instance.id + '-editor-area');
            if (!editorArea) {
                console.log('[ZatoIDE] initCodeEditor: editor area not found, id=' + instance.id + '-editor-area');
                return;
            }
            console.log('[ZatoIDE] initCodeEditor: editor area found');

            if (typeof ZatoIDEEditor === 'undefined') {
                console.log('[ZatoIDE] initCodeEditor: ZatoIDEEditor is undefined, editor JS not loaded');
                return;
            }
            console.log('[ZatoIDE] initCodeEditor: ZatoIDEEditor is available');

            var file = instance.files[instance.activeFile];
            console.log('[ZatoIDE] initCodeEditor: creating editor, activeFile=' + instance.activeFile + ', language=' + (file ? file.language : 'none'));
            instance.codeEditor = ZatoIDEEditor.create(editorArea, {
                theme: instance.options.theme,
                language: file ? file.language : 'python',
                fontSize: instance.options.fontSize,
                tabSize: instance.options.tabSize,
                content: file ? file.content : '',
                onContentChange: function(content) {
                    if (instance.activeFile && instance.files[instance.activeFile]) {
                        instance.files[instance.activeFile].content = content;
                    }
                    instance.content = content;
                },
                onCursorChange: function(line, col) {
                }
            });
            console.log('[ZatoIDE] initCodeEditor: editor created, codeEditor=' + (instance.codeEditor ? 'ok' : 'null'));
        },

        /**
         * Switches to a different file.
         */
        switchToFile: function(instance, filename) {
            console.log('[ZatoIDE] switchToFile: filename=' + filename);
            if (!instance.files[filename]) {
                console.log('[ZatoIDE] switchToFile: file not found in instance.files');
                return;
            }

            if (instance.activeFile && instance.codeEditor) {
                instance.files[instance.activeFile].content = ZatoIDEEditor.getValue(instance.codeEditor);
            }

            instance.activeFile = filename;
            var file = instance.files[filename];

            if (instance.codeEditor) {
                ZatoIDEEditor.setContent(instance.codeEditor, file.content);
                ZatoIDEEditor.setLanguage(instance.codeEditor, file.language);
            }

            this.syncTabToFile(instance, filename);
            this.updateSymbols(instance);
        },

        /**
         * Syncs the active tab to match the current file.
         */
        syncTabToFile: function(instance, filename) {
            if (!instance.tabsManager) {
                return;
            }

            var tabs = instance.tabsManager.tabs;
            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i].title === filename) {
                    instance.tabsManager.activeTabId = tabs[i].id;
                    this.renderTabs(instance);
                    break;
                }
            }
        },

        /**
         * Updates the symbol dropdown with symbols from the current file.
         */
        updateSymbols: function(instance) {
            if (!instance.symbolDropdown || !window.ZatoIDESymbols) {
                return;
            }

            var file = instance.files[instance.activeFile];
            if (!file) {
                return;
            }

            var symbols = ZatoIDESymbols.extract(file.content, file.language);
            var container = instance.symbolDropdown;
            var menu = container.querySelector('.zato-dropdown-menu');
            var textSpan = container.querySelector('.zato-dropdown-text');

            if (!menu) {
                return;
            }

            menu.innerHTML = '';

            if (symbols.length === 0) {
                var emptyItem = document.createElement('div');
                emptyItem.className = 'zato-dropdown-item disabled';
                emptyItem.textContent = '(no symbols)';
                menu.appendChild(emptyItem);
                if (textSpan) {
                    textSpan.textContent = '-- symbols --';
                }
                return;
            }

            for (var i = 0; i < symbols.length; i++) {
                var symbol = symbols[i];
                var item = document.createElement('div');
                item.className = 'zato-dropdown-item';
                item.setAttribute('data-value', symbol.line);
                item.textContent = symbol.name;
                menu.appendChild(item);
            }

            if (textSpan) {
                textSpan.textContent = symbols[0].name;
            }
            container.setAttribute('data-value', symbols[0].line);
        },

        /**
         * Jumps to a specific line in the editor.
         */
        jumpToLine: function(instance, line) {
            if (!instance.codeEditor) {
                return;
            }

            var targetLine = Math.max(1, line - 4);
            ZatoIDEEditor.scrollToLine(instance.codeEditor, targetLine);
        },

        loadSearchIcon: function(instance) {
            var searchButton = instance.container.querySelector('.zato-ide-search-button');
            if (!searchButton) {
                return;
            }

            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/static/img/search.svg', true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var svgContent = xhr.responseText;
                    svgContent = svgContent.replace(/width="24"/, 'width="25"');
                    svgContent = svgContent.replace(/height="24"/, 'height="25"');
                    searchButton.innerHTML = svgContent;
                }
            };
            xhr.send();
        },

        /**
         * Initializes the tabs manager and renders tabs for all files.
         *
         * @param {Object} instance - the IDE instance object
         */
        initTabs: function(instance) {
            if (typeof ZatoTabsManager === 'undefined') {
                return;
            }

            var tabsContainerId = instance.id + '-tabs';
            instance.tabsManager = ZatoTabsManager.create(tabsContainerId, {
                theme: instance.options.theme,
                onTabChange: function(tab) {
                    if (instance.onTabChange) {
                        instance.onTabChange(tab);
                    }
                }
            });

            var files = [
                { id: 'file-1', title: 'my_service.py' },
                { id: 'file-2', title: 'queries.sql' },
                { id: 'file-3', title: 'config.yaml' },
                { id: 'file-4', title: 'data.json' },
                { id: 'file-5', title: 'settings.ini' }
            ];

            instance.tabsManager.tabs = files;
            instance.tabsManager.activeTabId = files[0].id;
            instance.tabsManager.container = document.getElementById(tabsContainerId);

            this.renderTabs(instance);
            this.bindTabEvents(instance);
        },

        /**
         * Renders the tabs HTML into the tabs container.
         *
         * @param {Object} instance - the IDE instance object
         */
        renderTabs: function(instance) {
            if (!instance.tabsManager || !instance.tabsManager.container) {
                return;
            }

            var tabsInstance = {
                containerId: instance.id + '-tabs',
                tabs: instance.tabsManager.tabs,
                activeTabId: instance.tabsManager.activeTabId,
                theme: instance.options.theme,
                closedTabsHistory: instance.closedTabsHistory || [],
                clearedMessagesBuffer: instance.clearedMessagesBuffer || {}
            };

            var options = {
                theme: instance.options.theme,
                showAddButton: true,
                showCloseButton: true,
                showPinIcon: true,
                showLockIcon: true,
                addButtonTitle: 'New file',
                containerClass: 'zato-ide-tabs'
            };

            var html = ZatoTabsRenderer.buildTabsHtml(tabsInstance, options);
            instance.tabsManager.container.innerHTML = html;
        },

        /**
         * Binds all tab events using ZatoTabsEvents.
         *
         * @param {Object} instance - the IDE instance object
         */
        bindTabEvents: function(instance) {
            var self = this;
            var container = instance.tabsManager.container;
            if (!container) {
                return;
            }

            instance.closedTabsHistory = [];
            instance.clearedMessagesBuffer = {};

            var tabsInstance = {
                containerId: instance.id + '-tabs',
                tabs: instance.tabsManager.tabs,
                activeTabId: instance.tabsManager.activeTabId,
                theme: instance.options.theme,
                closedTabsHistory: instance.closedTabsHistory,
                clearedMessagesBuffer: instance.clearedMessagesBuffer
            };

            var callbacks = {
                onTabChange: function(tab) {
                    if (tab && tab.title) {
                        self.switchToFile(instance, tab.title);
                    }
                    if (instance.onTabChange) {
                        instance.onTabChange(tab);
                    }
                },
                onSave: function() {
                },
                onRender: function() {
                    instance.tabsManager.activeTabId = tabsInstance.activeTabId;
                    instance.tabsManager.tabs = tabsInstance.tabs;
                    self.renderTabs(instance);
                },
                createTabData: function(tabNumber) {
                    return {
                        title: 'file-' + tabNumber + '.py'
                    };
                },
                onAddToClosedHistory: function(tab) {
                    instance.closedTabsHistory.unshift({
                        tabs: [JSON.parse(JSON.stringify(tab))],
                        closedAt: Date.now()
                    });
                    tabsInstance.closedTabsHistory = instance.closedTabsHistory;
                },
                onFlushClosedHistory: function() {
                },
                onReopenClosedTabs: function() {
                    if (instance.closedTabsHistory.length === 0) {
                        return [];
                    }
                    var entry = instance.closedTabsHistory.shift();
                    var closedTabs = entry.tabs || [];
                    var reopened = [];
                    for (var i = 0; i < closedTabs.length; i++) {
                        var tab = closedTabs[i];
                        tab.id = ZatoTabsEvents.generateTabId();
                        tabsInstance.tabs.push(tab);
                        reopened.push(tab);
                    }
                    tabsInstance.closedTabsHistory = instance.closedTabsHistory;
                    return reopened;
                },
                onClearMessages: function(tabId, messages) {
                    instance.clearedMessagesBuffer[tabId] = {
                        messages: JSON.parse(JSON.stringify(messages)),
                        clearedAt: Date.now()
                    };
                    tabsInstance.clearedMessagesBuffer = instance.clearedMessagesBuffer;
                },
                onUndoClearMessages: function(tabId) {
                    var buffer = instance.clearedMessagesBuffer[tabId];
                    if (!buffer) {
                        return false;
                    }
                    var tab = ZatoTabsEvents.getTabById(tabsInstance.tabs, tabId);
                    if (tab) {
                        tab.messages = buffer.messages;
                        delete instance.clearedMessagesBuffer[tabId];
                        tabsInstance.clearedMessagesBuffer = instance.clearedMessagesBuffer;
                        return true;
                    }
                    return false;
                }
            };

            ZatoTabsEvents.bind(container, tabsInstance, callbacks);
        },

        /**
         * Binds event listeners to the editor textarea.
         * Handles: input, keyup, click (for status bar updates), Tab key (inserts spaces).
         *
         * @param {Object} instance - the IDE instance object
         */
        bindEvents: function(instance) {
            var self = this;

            var searchButton = instance.container.querySelector('.zato-ide-search-button');
            if (searchButton) {
                searchButton.addEventListener('click', function(e) {
                    e.stopPropagation();
                    self.toggleSearchPopup(instance, searchButton);
                });
            }

            document.addEventListener('click', function(e) {
                var popup = instance.container.querySelector('.zato-ide-search-popup');
                if (popup && popup.classList.contains('open')) {
                    if (!popup.contains(e.target) && !searchButton.contains(e.target)) {
                        popup.classList.remove('open');
                    }
                }
            });
        },

        toggleSearchPopup: function(instance, button) {
            var existingPopup = instance.container.querySelector('.zato-ide-search-popup');
            if (existingPopup) {
                existingPopup.classList.toggle('open');
                return;
            }

            var popup = document.createElement('div');
            popup.className = 'zato-ide-search-popup open';
            popup.innerHTML = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.';

            var toolbarRight = button.parentElement;
            toolbarRight.style.position = 'relative';
            toolbarRight.appendChild(popup);
        },

        /**
         * Gets the current editor content.
         *
         * @param {Object} instance - the IDE instance object
         * @returns {string} the editor content, or empty string if instance is invalid
         */
        getValue: function(instance) {
            if (instance && instance.codeEditor) {
                return ZatoIDEEditor.getValue(instance.codeEditor);
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
            if (instance && instance.codeEditor) {
                ZatoIDEEditor.setContent(instance.codeEditor, value);
                instance.content = value;
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
            if (instance.codeEditor) {
                ZatoIDEEditor.setTheme(instance.codeEditor, theme);
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
                if (instance.codeEditor) {
                    ZatoIDEEditor.destroy(instance.codeEditor);
                }
                instance.container.innerHTML = '';
                delete this.instances[containerId];
            }
        },

        /**
         * Sets the language for syntax highlighting.
         */
        setLanguage: function(instance, language) {
            if (instance && instance.codeEditor) {
                ZatoIDEEditor.setLanguage(instance.codeEditor, language);
            }
        },

        /**
         * Focuses the editor.
         */
        focus: function(instance) {
            if (instance && instance.codeEditor) {
                ZatoIDEEditor.focus(instance.codeEditor);
            }
        }
    };

    window.ZatoIDE = ZatoIDE;

})();
