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
            html += '<select id="' + instance.id + '-method-select" class="zato-ide-method-select" style="display: none;">';
            html += '<option value="">-- methods --</option>';
            html += '</select>';
            html += '</div>';
            html += '<div class="zato-ide-toolbar-center">';
            html += '<div class="zato-ide-debug-container" id="' + instance.id + '-debug-container">';
            html += '<select class="zato-ide-debug-select zato-ide-symbol-select" id="' + instance.id + '-debug-select">';
            html += '<option value="">Debug</option>';
            html += '<option value="debug-file">Debug current file</option>';
            html += '<option value="connect-server">Connect to server</option>';
            html += '</select>';
            html += '</div>';
            html += '<span class="zato-ide-toolbar-separator"></span>';
            html += '<span class="zato-ide-search-button" title="Search"></span>';
            html += '</div>';
            html += '</div>';

            html += '<div class="zato-ide-tabs-area">';
            html += '<div id="' + instance.id + '-tabs">';
            html += '</div>';
            html += '</div>';

            html += '<div class="zato-ide-main-area" id="' + instance.id + '-main-split">';
            html += '</div>';

            html += '<div class="zato-ide-statusbar" id="' + instance.id + '-statusbar">';
            html += '</div>';

            html += '</div>';

            instance.container.innerHTML = html;

            console.log('[ZatoIDE] render: container set, initializing main split');
            this.initMainSplit(instance);
            console.log('[ZatoIDE] render: main split initialized, initializing files');
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
                            instance.selectedClassLine = line;
                            self.updateMethods(instance, line);
                        }
                    }
                });

            }

            var methodSelect = document.getElementById(instance.id + '-method-select');
            if (methodSelect && typeof ZatoDropdown !== 'undefined') {
                instance.methodDropdown = ZatoDropdown.init(methodSelect, {
                    theme: instance.options.theme,
                    id: instance.id + '-method-dropdown',
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
                        console.log('[TRACE-METHOD] dropdown.onChange: value="' + value + '" text="' + text + '"');
                        if (value) {
                            var line = parseInt(value, 10);
                            self.jumpToLine(instance, line);
                        }
                    }
                });
            }

            var debugSelect = document.getElementById(instance.id + '-debug-select');
            if (debugSelect && typeof ZatoDropdown !== 'undefined') {
                instance.debugDropdown = ZatoDropdown.init(debugSelect, {
                    theme: instance.options.theme,
                    id: instance.id + '-debug-dropdown',
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
                            self.handleDebugAction(instance, value);
                            if (instance.debugDropdown) {
                                ZatoDropdown.setValue(instance.debugDropdown, '');
                            }
                        }
                    }
                });
            }

            console.log('[ZatoIDE] render: initializing tabs');
            this.initTabs(instance);

            this.loadSearchIcon(instance);
            this.loadSidePanel1Icons(instance);
            this.initSidePanel1Content(instance);

            this.bindEvents(instance);

            console.log('[ZatoIDE] render: switching to initial file my_service.py');
            this.switchToFile(instance, 'my_service.py');
            console.log('[ZatoIDE] render: complete');
        },

        /**
         * Initializes sample files with content.
         */
        initFiles: function(instance) {
            var pythonContent = this.getPythonContent();
            var sqlContent = this.getSQLContent();
            var yamlContent = this.getYAMLContent();
            var jsonContent = this.getJSONContent();
            var iniContent = this.getINIContent();

            instance.files = {
                'my_service.py': {
                    content: pythonContent,
                    originalContent: pythonContent,
                    language: 'python',
                    modified: false
                },
                'queries.sql': {
                    content: sqlContent,
                    originalContent: sqlContent,
                    language: 'sql',
                    modified: false
                },
                'config.yaml': {
                    content: yamlContent,
                    originalContent: yamlContent,
                    language: 'yaml',
                    modified: false
                },
                'data.json': {
                    content: jsonContent,
                    originalContent: jsonContent,
                    language: 'json',
                    modified: false
                },
                'settings.ini': {
                    content: iniContent,
                    originalContent: iniContent,
                    language: 'ini',
                    modified: false
                }
            };
            instance.activeFile = 'my_service.py';
        },

        getPythonContent: function() {
            var lines = [];
            lines.push('# -*- coding: utf-8 -*-');
            lines.push('');
            lines.push('import requests');
            lines.push('');
            lines.push('class DuckDuckGoSearch:');
            lines.push('');
            lines.push('    base_url = \'https://api.duckduckgo.com/\'');
            lines.push('');
            lines.push('    def __init__(self, timeout=10):');
            lines.push('        self.timeout = timeout');
            lines.push('        self.session = requests.Session()');
            lines.push('');
            lines.push('    def instant_answer(self, query):');
            lines.push('        params = {\'q\': query, \'format\': \'json\', \'no_html\': 1}');
            lines.push('        response = self.session.get(self.base_url, params=params, timeout=self.timeout)');
            lines.push('        return response.json()');
            lines.push('');
            lines.push('    def get_abstract(self, query):');
            lines.push('        data = self.instant_answer(query)');
            lines.push('        return data.get(\'Abstract\', \'\')');
            lines.push('');
            lines.push('    def get_related_topics(self, query):');
            lines.push('        data = self.instant_answer(query)');
            lines.push('        return [topic.get(\'Text\') for topic in data.get(\'RelatedTopics\', [])]');
            lines.push('');
            lines.push('    def get_definition(self, query):');
            lines.push('        data = self.instant_answer(query)');
            lines.push('        return data.get(\'Definition\', \'\')');
            lines.push('');
            lines.push('');
            lines.push('if __name__ == \'__main__\':');
            lines.push('    ddg = DuckDuckGoSearch()');
            lines.push('    print(ddg.get_abstract(\'Python programming\'))');
            lines.push('');
            return lines.join('\n');
        },

        getSQLContent: function() {
            var lines = [];
            lines.push('-- ## User Management');
            lines.push('');
            lines.push('CREATE TABLE users (');
            lines.push('    id SERIAL PRIMARY KEY,');
            lines.push('    username VARCHAR(100) NOT NULL,');
            lines.push('    email VARCHAR(255) UNIQUE,');
            lines.push('    created_at TIMESTAMP DEFAULT NOW()');
            lines.push(');');
            lines.push('');
            lines.push('CREATE INDEX idx_users_email ON users(email);');
            lines.push('');
            lines.push('');
            lines.push('-- ## Session Tracking');
            lines.push('');
            lines.push('CREATE TABLE sessions (');
            lines.push('    id UUID PRIMARY KEY,');
            lines.push('    user_id INTEGER REFERENCES users(id),');
            lines.push('    token VARCHAR(512) NOT NULL,');
            lines.push('    expires_at TIMESTAMP NOT NULL');
            lines.push(');');
            lines.push('');
            lines.push('');
            lines.push('-- ## DUPLICATE_SECTION');
            lines.push('');
            lines.push('SELECT * FROM users WHERE id = 1;');
            lines.push('');
            lines.push('');
            lines.push('-- ## DUPLICATE_SECTION');
            lines.push('');
            lines.push('SELECT * FROM sessions WHERE user_id = 1;');
            lines.push('');
            lines.push('');
            lines.push('-- ## Audit Logging');
            lines.push('');
            lines.push('CREATE TABLE audit_log (');
            lines.push('    id SERIAL PRIMARY KEY,');
            lines.push('    action VARCHAR(50) NOT NULL,');
            lines.push('    entity_type VARCHAR(100),');
            lines.push('    entity_id INTEGER,');
            lines.push('    user_id INTEGER REFERENCES users(id),');
            lines.push('    details JSONB,');
            lines.push('    created_at TIMESTAMP DEFAULT NOW()');
            lines.push(');');
            lines.push('');
            lines.push('');
            lines.push('-- ## Permissions');
            lines.push('');
            lines.push('CREATE TABLE roles (');
            lines.push('    id SERIAL PRIMARY KEY,');
            lines.push('    name VARCHAR(50) UNIQUE NOT NULL');
            lines.push(');');
            lines.push('');
            lines.push('CREATE TABLE user_roles (');
            lines.push('    user_id INTEGER REFERENCES users(id),');
            lines.push('    role_id INTEGER REFERENCES roles(id),');
            lines.push('    PRIMARY KEY (user_id, role_id)');
            lines.push(');');
            lines.push('');
            lines.push('');
            lines.push('-- ## Notifications');
            lines.push('');
            lines.push('CREATE TABLE notifications (');
            lines.push('    id SERIAL PRIMARY KEY,');
            lines.push('    user_id INTEGER REFERENCES users(id),');
            lines.push('    message TEXT NOT NULL,');
            lines.push('    read BOOLEAN DEFAULT FALSE,');
            lines.push('    created_at TIMESTAMP DEFAULT NOW()');
            lines.push(');');
            lines.push('');
            return lines.join('\n');
        },

        getYAMLContent: function() {
            var lines = [];
            lines.push('# Configuration file');
            lines.push('');
            lines.push('server:');
            lines.push('  host: localhost');
            lines.push('  port: 8080');
            lines.push('  debug: true');
            lines.push('  workers: 4');
            lines.push('  timeout: 30');
            lines.push('');
            lines.push('database:');
            lines.push('  engine: postgresql');
            lines.push('  name: myapp');
            lines.push('  host: db.example.com');
            lines.push('  port: 5432');
            lines.push('  pool_size: 10');
            lines.push('  max_overflow: 20');
            lines.push('');
            lines.push('cache:');
            lines.push('  backend: redis');
            lines.push('  host: redis.example.com');
            lines.push('  port: 6379');
            lines.push('  db: 0');
            lines.push('  ttl: 3600');
            lines.push('');
            lines.push('DUPLICATE_KEY:');
            lines.push('  first: true');
            lines.push('  value: 100');
            lines.push('');
            lines.push('DUPLICATE_KEY:');
            lines.push('  second: true');
            lines.push('  value: 200');
            lines.push('');
            lines.push('logging:');
            lines.push('  level: INFO');
            lines.push('  format: json');
            lines.push('  handlers:');
            lines.push('    - console');
            lines.push('    - file');
            lines.push('  file_path: /var/log/app.log');
            lines.push('');
            lines.push('security:');
            lines.push('  jwt_secret: change-me-in-production');
            lines.push('  token_expiry: 86400');
            lines.push('  allowed_origins:');
            lines.push('    - https://example.com');
            lines.push('    - https://api.example.com');
            lines.push('');
            lines.push('features:');
            lines.push('  enable_signup: true');
            lines.push('  enable_oauth: false');
            lines.push('  maintenance_mode: false');
            lines.push('');
            lines.push('notifications:');
            lines.push('  email:');
            lines.push('    enabled: true');
            lines.push('    smtp_host: smtp.example.com');
            lines.push('  slack:');
            lines.push('    enabled: false');
            lines.push('    webhook_url: null');
            lines.push('');
            return lines.join('\n');
        },

        getJSONContent: function() {
            var lines = [];
            lines.push('{');
            lines.push('  "name": "My Application",');
            lines.push('  "version": "1.0.0",');
            lines.push('  "description": "A sample application configuration",');
            lines.push('  "author": "Development Team",');
            lines.push('  "settings": {');
            lines.push('    "enabled": true,');
            lines.push('    "maxItems": 100,');
            lines.push('    "tags": ["production", "api"]');
            lines.push('  },');
            lines.push('  "endpoints": {');
            lines.push('    "api": "https://api.example.com",');
            lines.push('    "auth": "https://auth.example.com",');
            lines.push('    "cdn": "https://cdn.example.com"');
            lines.push('  },');
            lines.push('  "DUPLICATE_KEY": {');
            lines.push('    "first": true,');
            lines.push('    "value": 100');
            lines.push('  },');
            lines.push('  "DUPLICATE_KEY": {');
            lines.push('    "second": true,');
            lines.push('    "value": 200');
            lines.push('  },');
            lines.push('  "database": {');
            lines.push('    "host": "localhost",');
            lines.push('    "port": 5432,');
            lines.push('    "name": "myapp",');
            lines.push('    "ssl": true');
            lines.push('  },');
            lines.push('  "cache": {');
            lines.push('    "enabled": true,');
            lines.push('    "ttl": 3600,');
            lines.push('    "maxSize": 1000');
            lines.push('  },');
            lines.push('  "logging": {');
            lines.push('    "level": "info",');
            lines.push('    "format": "json",');
            lines.push('    "outputs": ["console", "file"]');
            lines.push('  },');
            lines.push('  "features": {');
            lines.push('    "darkMode": true,');
            lines.push('    "notifications": true,');
            lines.push('    "analytics": false');
            lines.push('  },');
            lines.push('  "limits": {');
            lines.push('    "requestsPerMinute": 100,');
            lines.push('    "maxUploadSize": 10485760,');
            lines.push('    "sessionTimeout": 1800');
            lines.push('  }');
            lines.push('}');
            return lines.join('\n');
        },

        getINIContent: function() {
            var lines = [];
            lines.push('; Application settings');
            lines.push('');
            lines.push('[general]');
            lines.push('name = MyApp');
            lines.push('version = 1.0');
            lines.push('environment = production');
            lines.push('debug = false');
            lines.push('');
            lines.push('[server]');
            lines.push('host = 0.0.0.0');
            lines.push('port = 8080');
            lines.push('workers = 4');
            lines.push('timeout = 30');
            lines.push('');
            lines.push('[database]');
            lines.push('engine = postgresql');
            lines.push('host = db.example.com');
            lines.push('port = 5432');
            lines.push('name = myapp');
            lines.push('user = appuser');
            lines.push('pool_size = 10');
            lines.push('');
            lines.push('[DUPLICATE_SECTION]');
            lines.push('first = true');
            lines.push('value = 100');
            lines.push('');
            lines.push('[DUPLICATE_SECTION]');
            lines.push('second = true');
            lines.push('value = 200');
            lines.push('');
            lines.push('[cache]');
            lines.push('backend = redis');
            lines.push('host = redis.example.com');
            lines.push('port = 6379');
            lines.push('ttl = 3600');
            lines.push('');
            lines.push('[logging]');
            lines.push('level = INFO');
            lines.push('format = %(asctime)s - %(message)s');
            lines.push('file = /var/log/app.log');
            lines.push('');
            lines.push('[security]');
            lines.push('secret_key = change-me');
            lines.push('token_expiry = 86400');
            lines.push('ssl_enabled = true');
            lines.push('');
            lines.push('[features]');
            lines.push('enable_cache = true');
            lines.push('enable_signup = true');
            lines.push('maintenance_mode = false');
            lines.push('max_connections = 50');
            lines.push('');
            lines.push('[notifications]');
            lines.push('email_enabled = true');
            lines.push('smtp_host = smtp.example.com');
            lines.push('slack_enabled = false');
            lines.push('');
            return lines.join('\n');
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

            if (typeof ZatoIDEEditorAce === 'undefined') {
                console.log('[ZatoIDE] initCodeEditor: ZatoIDEEditorAce is undefined, editor JS not loaded');
                return;
            }
            console.log('[ZatoIDE] initCodeEditor: ZatoIDEEditorAce is available');

            var file = instance.files[instance.activeFile];
            console.log('[ZatoIDE] initCodeEditor: creating editor, activeFile=' + instance.activeFile + ', language=' + (file ? file.language : 'none'));
            var editorOptions = {
                theme: instance.options.theme,
                language: file ? file.language : 'python',
                tabSize: instance.options.tabSize,
                content: file ? file.content : '',
                ideContainerId: instance.id,
                onContentChange: function(content) {
                    if (instance.activeFile && instance.files[instance.activeFile]) {
                        var file = instance.files[instance.activeFile];
                        file.content = content;
                        var wasModified = file.modified;
                        file.modified = content !== file.originalContent;
                        if (wasModified !== file.modified) {
                            self.updateTabModifiedState(instance, instance.activeFile, file.modified);
                        }
                    }
                    instance.content = content;
                },
                onCursorChange: function(line, col) {
                    self.syncDropdownsToLine(instance, line);
                }
            };
            if (instance.options.fontSize) {
                editorOptions.fontSize = instance.options.fontSize;
            }
            instance.codeEditor = ZatoIDEEditorAce.create(editorArea, editorOptions);
            console.log('[ZatoIDE] initCodeEditor: editor created, codeEditor=' + (instance.codeEditor ? 'ok' : 'null'));

            if (typeof ZatoDebuggerGutter !== 'undefined' && instance.codeEditor && instance.codeEditor.aceEditor) {
                instance.gutterInstance = ZatoDebuggerGutter.create(instance.codeEditor.aceEditor, null, {
                    getFilename: function() {
                        return instance.activeFile || 'untitled.py';
                    }
                });
                console.log('[ZatoIDE] initCodeEditor: gutter created for breakpoints');
            }
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
                instance.files[instance.activeFile].content = ZatoIDEEditorAce.getValue(instance.codeEditor);
            }

            instance.activeFile = filename;
            var file = instance.files[filename];
            console.log('[ZatoIDE] switchToFile: file.language=' + file.language);

            if (instance.codeEditor) {
                console.log('[ZatoIDE] switchToFile: calling setLanguage with language=' + file.language);
                ZatoIDEEditorAce.setLanguage(instance.codeEditor, file.language);
                console.log('[ZatoIDE] switchToFile: calling setValue');
                ZatoIDEEditorAce.setValue(instance.codeEditor, file.content);
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

        updateTabModifiedState: function(instance, filename, modified) {
            if (!instance.tabsManager) {
                return;
            }
            var tabs = instance.tabsManager.tabs;
            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i].title === filename) {
                    tabs[i].modified = modified;
                    this.renderTabs(instance);
                    break;
                }
            }
        },

        showSaveDialog: function(instance, filename, callbacks) {
            var self = this;
            var overlay = document.createElement('div');
            overlay.className = 'zato-tabs-save-dialog-overlay';

            var dialog = document.createElement('div');
            dialog.className = 'zato-tabs-save-dialog';

            var header = document.createElement('div');
            header.className = 'zato-tabs-save-dialog-header';

            var title = document.createElement('div');
            title.className = 'zato-tabs-save-dialog-title';
            title.textContent = 'Save changes';

            var closeBtn = document.createElement('button');
            closeBtn.className = 'zato-tabs-save-dialog-close';
            closeBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';

            header.appendChild(title);
            header.appendChild(closeBtn);

            var content = document.createElement('div');
            content.className = 'zato-tabs-save-dialog-content';

            var message = document.createElement('div');
            message.className = 'zato-tabs-save-dialog-message';
            message.innerHTML = 'Do you want to save the changes you made to <strong>' + filename + '</strong>?<br>Your changes will be lost if you don\'t save them.';

            var buttons = document.createElement('div');
            buttons.className = 'zato-tabs-save-dialog-buttons';

            var dontSaveBtn = document.createElement('button');
            dontSaveBtn.className = 'zato-tabs-save-dialog-btn zato-tabs-save-dialog-btn-secondary';
            dontSaveBtn.textContent = 'Don\'t Save';

            var cancelBtn = document.createElement('button');
            cancelBtn.className = 'zato-tabs-save-dialog-btn zato-tabs-save-dialog-btn-secondary';
            cancelBtn.textContent = 'Cancel';

            var saveBtn = document.createElement('button');
            saveBtn.className = 'zato-tabs-save-dialog-btn zato-tabs-save-dialog-btn-default';
            saveBtn.textContent = 'Save';

            buttons.appendChild(dontSaveBtn);
            buttons.appendChild(cancelBtn);
            buttons.appendChild(saveBtn);

            content.appendChild(message);
            content.appendChild(buttons);

            dialog.appendChild(header);
            dialog.appendChild(content);
            overlay.appendChild(dialog);
            document.body.appendChild(overlay);

            dialog.style.left = '50%';
            dialog.style.top = '50%';
            dialog.style.transform = 'translate(-50%, -50%)';

            this.makeDialogDraggable(dialog, header, closeBtn);

            var closeDialog = function() {
                document.body.removeChild(overlay);
            };

            closeBtn.addEventListener('click', function() {
                closeDialog();
                if (callbacks.onCancel) {
                    callbacks.onCancel();
                }
            });

            dontSaveBtn.addEventListener('click', function() {
                closeDialog();
                if (callbacks.onDontSave) {
                    callbacks.onDontSave();
                }
            });

            cancelBtn.addEventListener('click', function() {
                closeDialog();
                if (callbacks.onCancel) {
                    callbacks.onCancel();
                }
            });

            saveBtn.addEventListener('click', function() {
                closeDialog();
                if (callbacks.onSave) {
                    callbacks.onSave();
                }
            });

            saveBtn.focus();
        },

        makeDialogDraggable: function(dialog, handle, excludeElement) {
            var isDragging = false;
            var startX, startY, startLeft, startTop;

            handle.addEventListener('mousedown', function(e) {
                if (excludeElement && e.target.closest('.zato-tabs-save-dialog-close')) {
                    return;
                }
                isDragging = true;

                var rect = dialog.getBoundingClientRect();
                startLeft = rect.left;
                startTop = rect.top;
                dialog.style.transform = 'none';
                dialog.style.left = startLeft + 'px';
                dialog.style.top = startTop + 'px';

                startX = e.clientX;
                startY = e.clientY;
                e.preventDefault();
            });

            document.addEventListener('mousemove', function(e) {
                if (!isDragging) return;
                var dx = e.clientX - startX;
                var dy = e.clientY - startY;
                dialog.style.left = (startLeft + dx) + 'px';
                dialog.style.top = (startTop + dy) + 'px';
            });

            document.addEventListener('mouseup', function() {
                isDragging = false;
            });
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
            instance.cachedSymbols = symbols;
            var container = instance.symbolDropdown;
            var menu = container.querySelector('.zato-dropdown-menu');
            var textSpan = container.querySelector('.zato-dropdown-text');

            if (!menu) {
                return;
            }

            menu.innerHTML = '';

            var lineCount = file.content ? file.content.split('\n').length : 1;

            if (symbols.length > 0) {
                var topItem = document.createElement('div');
                topItem.className = 'zato-dropdown-item';
                topItem.setAttribute('data-value', '1');
                topItem.textContent = '(top)';
                menu.appendChild(topItem);

                var bottomItem = document.createElement('div');
                bottomItem.className = 'zato-dropdown-item';
                bottomItem.setAttribute('data-value', lineCount);
                bottomItem.textContent = '(bottom)';
                menu.appendChild(bottomItem);

                var separator = document.createElement('div');
                separator.className = 'zato-dropdown-separator';
                menu.appendChild(separator);
            }

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

            instance.selectedClassLine = symbols[0].line;
            this.updateMethods(instance, symbols[0].line);
        },

        syncDropdownsToLine: function(instance, line) {
            if (!instance.symbolDropdown) {
                return;
            }

            var cachedSymbols = instance.cachedSymbols || [];
            var cachedMethods = instance.cachedMethods || [];
            var symbolContainer = instance.symbolDropdown;
            var symbolTextSpan = symbolContainer.querySelector('.zato-dropdown-text');

            if (cachedSymbols.length === 0) {
                return;
            }

            var file = instance.files[instance.activeFile];
            var lineCount = file && file.content ? file.content.split('\n').length : 1;
            var firstSymbolLine = cachedSymbols[0].line;
            var lastSymbolLine = cachedSymbols[cachedSymbols.length - 1].line;

            if (line < firstSymbolLine) {
                if (symbolTextSpan) {
                    symbolTextSpan.textContent = '(top)';
                }
                symbolContainer.setAttribute('data-value', '1');
                instance.selectedClassLine = null;
                if (instance.methodDropdown) {
                    instance.methodDropdown.style.display = 'none';
                }
                return;
            }

            var symbol = null;
            var symbolIndex = -1;
            var nextSymbolLine = null;
            for (var i = 0; i < cachedSymbols.length; i++) {
                if (cachedSymbols[i].line <= line) {
                    symbol = cachedSymbols[i];
                    symbolIndex = i;
                    nextSymbolLine = (i + 1 < cachedSymbols.length) ? cachedSymbols[i + 1].line : null;
                } else {
                    break;
                }
            }

            var symbolEnd = symbol ? this.estimateSymbolEnd(file.content, symbol.line) : null;

            var isOutsideSymbol = false;
            if (symbol && symbolEnd !== null && line >= symbolEnd) {
                isOutsideSymbol = true;
            }

            if (symbol && nextSymbolLine === null && line > lastSymbolLine) {
                var lastSymbolMethods = ZatoIDESymbols.extractMethods(file.content, file.language, lastSymbolLine);
                var lastMethodLine = lastSymbolMethods.length > 0 ? lastSymbolMethods[lastSymbolMethods.length - 1].line : lastSymbolLine;
                var estimatedEnd = this.estimateSymbolEnd(file.content, lastMethodLine);
                if (line > estimatedEnd) {
                    if (symbolTextSpan) {
                        symbolTextSpan.textContent = '(bottom)';
                    }
                    symbolContainer.setAttribute('data-value', lineCount);
                    instance.selectedClassLine = null;
                    if (instance.methodDropdown) {
                        instance.methodDropdown.style.display = 'none';
                    }
                    return;
                }
            }

            if (isOutsideSymbol) {
                if (instance.methodDropdown) {
                    instance.methodDropdown.style.display = 'none';
                }
                return;
            }

            if (instance.selectedClassLine !== symbol.line) {
                instance.selectedClassLine = symbol.line;
                this.updateMethods(instance, symbol.line);
                cachedMethods = instance.cachedMethods || [];
            }

            if (symbolTextSpan) {
                symbolTextSpan.textContent = symbol.name;
            }
            symbolContainer.setAttribute('data-value', symbol.line);

            var method = null;
            var methodIndex = -1;
            var nextMethodLine = null;
            for (var j = 0; j < cachedMethods.length; j++) {
                if (cachedMethods[j].line <= line) {
                    method = cachedMethods[j];
                    methodIndex = j;
                    nextMethodLine = (j + 1 < cachedMethods.length) ? cachedMethods[j + 1].line : null;
                } else {
                    break;
                }
            }

            var isOutsideMethod = false;
            if (method) {
                var methodEnd = this.estimateSymbolEnd(file.content, method.line);
                if (line >= methodEnd) {
                    isOutsideMethod = true;
                }
            } else {
                if (cachedMethods.length > 0 && line < cachedMethods[0].line) {
                    isOutsideMethod = true;
                }
            }

            if (instance.methodDropdown) {
                var methodContainer = instance.methodDropdown;
                var methodTextSpan = methodContainer.querySelector('.zato-dropdown-text');

                if (!method) {
                } else if (isOutsideMethod) {
                } else {
                    if (methodTextSpan) {
                        methodTextSpan.textContent = method.name;
                    }
                    methodContainer.setAttribute('data-value', method.line);
                }
            }
        },

        estimateSymbolEnd: function(content, startLine) {
            var lines = content.split('\n');
            var startIndex = startLine - 1;
            if (startIndex < 0 || startIndex >= lines.length) {
                return startLine;
            }

            var baseIndent = this.getIndent(lines[startIndex]);

            for (var i = startIndex + 1; i < lines.length; i++) {
                var line = lines[i];
                var trimmed = line.trim();
                if (trimmed === '') {
                    continue;
                }
                var currentIndent = this.getIndent(line);
                if (currentIndent <= baseIndent) {
                    return i;
                }
            }
            return lines.length;
        },

        getIndent: function(line) {
            var match = line.match(/^(\s*)/);
            return match ? match[1].length : 0;
        },

        updateMethods: function(instance, classLine) {
            if (!instance.methodDropdown || !window.ZatoIDESymbols) {
                return;
            }

            var file = instance.files[instance.activeFile];
            if (!file) {
                return;
            }

            var methods = ZatoIDESymbols.extractMethods(file.content, file.language, classLine);
            instance.cachedMethods = methods;

            var container = instance.methodDropdown;
            var menu = container.querySelector('.zato-dropdown-menu');
            var textSpan = container.querySelector('.zato-dropdown-text');

            if (!menu) {
                return;
            }

            menu.innerHTML = '';

            if (methods.length === 0) {
                container.style.display = 'none';
                return;
            }

            container.style.display = '';

            for (var i = 0; i < methods.length; i++) {
                var method = methods[i];
                var item = document.createElement('div');
                item.className = 'zato-dropdown-item';
                item.setAttribute('data-value', method.line);
                item.textContent = method.name;
                menu.appendChild(item);
            }

            if (textSpan) {
                textSpan.textContent = methods[0].name;
            }
            container.setAttribute('data-value', methods[0].line);
        },

        /**
         * Jumps to a specific line in the editor.
         */
        jumpToLine: function(instance, line) {
            if (!instance.codeEditor) {
                return;
            }

            var targetLine = Math.max(1, line - 2);
            ZatoIDEEditorAce.scrollToLine(instance.codeEditor, targetLine);
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

        loadSidePanel1Icons: function(instance) {
            var self = this;
            var iconsContainer = document.getElementById(instance.id + '-side-panel-1-icons');
            if (!iconsContainer) {
                return;
            }

            var icons = [
                { id: 'explorer', file: 'explorer.svg', tooltip: 'Explorer' },
                { id: 'debugger', file: 'debugger.svg', tooltip: 'Debugger' },
                { id: 'notes', file: 'notes.svg', tooltip: 'Notes' }
            ];

            instance.sidePanel1ActiveView = 'explorer';

            icons.forEach(function(iconDef) {
                var iconDiv = document.createElement('div');
                iconDiv.className = 'zato-ide-side-panel-1-icon';
                iconDiv.setAttribute('data-view', iconDef.id);
                iconDiv.setAttribute('data-tooltip', iconDef.tooltip);
                iconDiv.setAttribute('data-tooltip-position', 'left');
                if (iconDef.id === instance.sidePanel1ActiveView) {
                    iconDiv.classList.add('active');
                }

                iconsContainer.appendChild(iconDiv);

                var xhr = new XMLHttpRequest();
                xhr.open('GET', '/static/img/side-panel/' + iconDef.file, true);
                xhr.onreadystatechange = function() {
                    if (xhr.readyState === 4 && xhr.status === 200) {
                        iconDiv.innerHTML = xhr.responseText;
                    }
                };
                xhr.send();

                iconDiv.addEventListener('click', function() {
                    var contentContainer = document.getElementById(instance.id + '-side-panel-1-content');
                    var isCollapsed = contentContainer && contentContainer.classList.contains('collapsed');
                    
                    if (isCollapsed) {
                        if (typeof ZatoIDEKeyboard !== 'undefined' && ZatoIDEKeyboard.toggleSidePanelContent) {
                            ZatoIDEKeyboard.toggleSidePanelContent();
                        }
                    }
                    
                    self.switchSidePanel1View(instance, iconDef.id);
                });
            });
        },

        switchSidePanel1View: function(instance, viewId) {
            var self = this;
            var iconsContainer = document.getElementById(instance.id + '-side-panel-1-icons');
            if (!iconsContainer) {
                return;
            }

            var icons = iconsContainer.querySelectorAll('.zato-ide-side-panel-1-icon');
            icons.forEach(function(icon) {
                if (icon.getAttribute('data-view') === viewId) {
                    icon.classList.add('active');
                } else {
                    icon.classList.remove('active');
                }
            });

            instance.sidePanel1ActiveView = viewId;

            var contentContainer = document.getElementById(instance.id + '-side-panel-1-content');
            if (contentContainer) {
                contentContainer.innerHTML = '';

                if (viewId === 'explorer') {
                    self.initExplorer(instance, contentContainer);
                }
            }
        },

        initMainSplit: function(instance) {
            console.log('[ZatoIDE] initMainSplit: START');
            if (typeof ZatoIDESplit === 'undefined') {
                console.log('[ZatoIDE] initMainSplit: ZatoIDESplit undefined, returning');
                return;
            }

            var splitContainerId = instance.id + '-main-split';
            console.log('[ZatoIDE] initMainSplit: splitContainerId=' + splitContainerId);
            var container = document.getElementById(splitContainerId);
            console.log('[ZatoIDE] initMainSplit: container found=' + !!container);
            if (container) {
                console.log('[ZatoIDE] initMainSplit: container.innerHTML length=' + container.innerHTML.length);
                console.log('[ZatoIDE] initMainSplit: container.children.length=' + container.children.length);
            }
            instance.mainSplit = ZatoIDESplit.create(splitContainerId, {
                storageKey: 'zato.ide.main-split-position',
                defaultSplitPercent: 75,
                minPanelWidth: 200,
                onResize: function() {
                    if (instance.aceEditor) {
                        instance.aceEditor.resize();
                    }
                }
            });

            console.log('[ZatoIDE] initMainSplit: mainSplit created=' + !!instance.mainSplit);
            if (!instance.mainSplit) {
                console.log('[ZatoIDE] initMainSplit: mainSplit is null, returning');
                return;
            }

            var leftPanel = ZatoIDESplit.getLeftPanel(instance.mainSplit);
            var rightPanel = ZatoIDESplit.getRightPanel(instance.mainSplit);
            console.log('[ZatoIDE] initMainSplit: leftPanel=' + !!leftPanel + ', rightPanel=' + !!rightPanel);

            if (leftPanel) {
                console.log('[ZatoIDE] initMainSplit: setting leftPanel id to ' + instance.id + '-editor-area');
                leftPanel.id = instance.id + '-editor-area';
                leftPanel.className += ' zato-ide-editor-area';
            }

            if (rightPanel) {
                console.log('[ZatoIDE] initMainSplit: setting rightPanel id to ' + instance.id + '-side-panel-1');
                console.log('[ZatoIDE] initMainSplit: rightPanel current innerHTML length=' + rightPanel.innerHTML.length);
                rightPanel.id = instance.id + '-side-panel-1';
                rightPanel.className += ' zato-ide-side-panel-1';

                var iconsDiv = document.createElement('div');
                iconsDiv.id = instance.id + '-side-panel-1-icons';
                iconsDiv.className = 'zato-ide-side-panel-1-icons';
                rightPanel.appendChild(iconsDiv);

                var contentDiv = document.createElement('div');
                contentDiv.id = instance.id + '-side-panel-1-content';
                contentDiv.className = 'zato-ide-side-panel-1-content';
                rightPanel.appendChild(contentDiv);
                console.log('[ZatoIDE] initMainSplit: side panel elements created');
            }
            console.log('[ZatoIDE] initMainSplit: END');
        },

        initSidePanel1Content: function(instance) {
            var contentContainer = document.getElementById(instance.id + '-side-panel-1-content');
            if (!contentContainer) {
                return;
            }

            if (instance.sidePanel1ActiveView === 'explorer') {
                this.initExplorer(instance, contentContainer);
            }
        },

        initExplorer: function(instance, container) {
            var self = this;
            if (typeof ZatoIDEExplorer === 'undefined') {
                return;
            }

            var explorerDiv = document.createElement('div');
            var explorerId = instance.id + '-explorer';
            explorerDiv.id = explorerId;
            container.appendChild(explorerDiv);

            instance.explorer = ZatoIDEExplorer.create(explorerId, {
                rootPath: '~',
                onFileSelect: function(item) {
                    console.log('[ZatoIDE] File selected:', item.path);
                },
                onFileDoubleClick: function(item) {
                    if (typeof ZatoIDEEditorAce !== 'undefined' && ZatoIDEEditorAce.isEditableFile(item.name)) {
                        self.openFileFromPath(instance, item.path, item.name);
                    } else {
                        self.downloadFile(item.path, item.name);
                    }
                }
            });
        },

        downloadFile: function(filePath, fileName) {
            var link = document.createElement('a');
            link.href = '/zato/ide/explorer/download/?path=' + encodeURIComponent(filePath);
            link.download = fileName;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        },

        openFileFromPath: function(instance, filePath, fileName) {
            var self = this;

            var existingTab = this.findTabByPath(instance, filePath);
            if (existingTab) {
                this.switchToTab(instance, existingTab.id);
                return;
            }

            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/zato/ide/explorer/read/?path=' + encodeURIComponent(filePath), true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        var response = JSON.parse(xhr.responseText);
                        if (response.success) {
                            self.openFileInNewTab(instance, filePath, fileName, response.content);
                        }
                    }
                }
            };
            xhr.send();
        },

        findTabByPath: function(instance, filePath) {
            if (!instance.tabsManager || !instance.tabsManager.tabs) {
                return null;
            }
            for (var i = 0; i < instance.tabsManager.tabs.length; i++) {
                var tab = instance.tabsManager.tabs[i];
                if (tab.filePath === filePath) {
                    return tab;
                }
            }
            return null;
        },

        openFileInNewTab: function(instance, filePath, fileName, content) {
            var tabId = 'file-' + Date.now();
            var language = 'text';
            if (typeof ZatoIDEEditorAce !== 'undefined') {
                language = ZatoIDEEditorAce.getLanguageFromExtension(fileName);
            }

            var newTab = {
                id: tabId,
                title: fileName,
                filePath: filePath,
                content: content,
                language: language
            };

            if (!instance.tabsManager.tabs) {
                instance.tabsManager.tabs = [];
            }
            instance.tabsManager.tabs.push(newTab);

            if (!instance.files) {
                instance.files = {};
            }
            instance.files[fileName] = {
                content: content,
                originalContent: content,
                language: language,
                filePath: filePath,
                modified: false
            };

            this.renderTabs(instance);
            this.bindTabEvents(instance);
            this.switchToTab(instance, tabId);
        },

        switchToTab: function(instance, tabId) {
            if (!instance.tabsManager) {
                return;
            }

            instance.tabsManager.activeTabId = tabId;
            this.renderTabs(instance);
            this.bindTabEvents(instance);

            var tab = null;
            for (var i = 0; i < instance.tabsManager.tabs.length; i++) {
                if (instance.tabsManager.tabs[i].id === tabId) {
                    tab = instance.tabsManager.tabs[i];
                    break;
                }
            }

            if (tab && tab.title) {
                this.switchToFile(instance, tab.title);
            }
        },

        closeTab: function(instance, tab) {
            if (!instance.tabsManager || !instance.tabsManager.tabs) {
                return;
            }

            if (instance.tabsManager.tabs.length <= 1) {
                return;
            }

            var tabId = tab.id;
            var filename = tab.title;
            var file = instance.files ? instance.files[filename] : null;
            var self = this;

            var doClose = function() {
                var tabs = instance.tabsManager.tabs;
                var tabIndex = -1;
                for (var i = 0; i < tabs.length; i++) {
                    if (tabs[i].id === tabId) {
                        tabIndex = i;
                        break;
                    }
                }

                if (tabIndex === -1) {
                    return;
                }

                tabs.splice(tabIndex, 1);

                if (instance.tabsManager.activeTabId === tabId) {
                    var newIndex = tabIndex > 0 ? tabIndex - 1 : 0;
                    if (tabs.length > 0) {
                        instance.tabsManager.activeTabId = tabs[newIndex].id;
                        self.switchToFile(instance, tabs[newIndex].title);
                    }
                }

                self.renderTabs(instance);
                self.bindTabEvents(instance);
            };

            if (file && file.modified) {
                this.showSaveDialog(instance, filename, {
                    onDontSave: function() {
                        file.modified = false;
                        doClose();
                    },
                    onCancel: function() {
                    },
                    onSave: function() {
                        file.originalContent = file.content;
                        file.modified = false;
                        doClose();
                    }
                });
            } else {
                doClose();
            }
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
                onBeforeClose: function(tab, doClose) {
                    var filename = tab.title;
                    var file = instance.files[filename];
                    if (file && file.modified) {
                        self.showSaveDialog(instance, filename, {
                            onDontSave: function() {
                                file.modified = false;
                                doClose();
                            },
                            onCancel: function() {
                            },
                            onSave: function() {
                                file.originalContent = file.content;
                                file.modified = false;
                                doClose();
                            }
                        });
                    } else {
                        doClose();
                    }
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

        handleDebugAction: function(instance, action) {
            console.log('[ZatoIDE] handleDebugAction: START action=' + action + ' file=' + instance.activeFile);

            console.log('[ZatoIDE] handleDebugAction: checking ZatoDebuggerIDE availability');
            console.log('[ZatoIDE] handleDebugAction: typeof ZatoDebuggerIDE=' + (typeof ZatoDebuggerIDE));
            console.log('[ZatoIDE] handleDebugAction: typeof ZatoDebuggerCore=' + (typeof ZatoDebuggerCore));
            console.log('[ZatoIDE] handleDebugAction: typeof ZatoDebuggerUI=' + (typeof ZatoDebuggerUI));
            console.log('[ZatoIDE] handleDebugAction: typeof ZatoDebuggerProtocol=' + (typeof ZatoDebuggerProtocol));
            console.log('[ZatoIDE] handleDebugAction: typeof ZatoDebuggerGutter=' + (typeof ZatoDebuggerGutter));

            if (!instance.debuggerIDE && typeof ZatoDebuggerIDE !== 'undefined') {
                console.log('[ZatoIDE] handleDebugAction: creating ZatoDebuggerIDE instance');
                instance.debuggerIDE = ZatoDebuggerIDE.create(instance, {
                    theme: instance.options.theme
                });
                console.log('[ZatoIDE] handleDebugAction: ZatoDebuggerIDE instance created=' + (instance.debuggerIDE ? 'ok' : 'null'));
            } else if (!instance.debuggerIDE) {
                console.log('[ZatoIDE] handleDebugAction: ZatoDebuggerIDE is not defined, cannot create debugger');
            } else {
                console.log('[ZatoIDE] handleDebugAction: using existing debuggerIDE instance');
            }

            if (action === 'debug-file') {
                console.log('[ZatoIDE] handleDebugAction: action is debug-file');
                if (instance.debuggerIDE) {
                    console.log('[ZatoIDE] handleDebugAction: calling ZatoDebuggerIDE.debugCurrentFile');
                    var result = ZatoDebuggerIDE.debugCurrentFile(instance.debuggerIDE);
                    console.log('[ZatoIDE] handleDebugAction: debugCurrentFile returned=' + result);
                } else {
                    console.log('[ZatoIDE] handleDebugAction: no debuggerIDE instance, cannot debug');
                }
            } else if (action === 'connect-server') {
                console.log('[ZatoIDE] handleDebugAction: action is connect-server - not yet implemented');
            } else {
                console.log('[ZatoIDE] handleDebugAction: unknown action=' + action);
            }

            console.log('[ZatoIDE] handleDebugAction: END');
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

            var rect = button.getBoundingClientRect();
            popup.style.position = 'fixed';
            popup.style.top = (rect.bottom + 4) + 'px';
            popup.style.left = rect.left + 'px';

            instance.container.appendChild(popup);
        },

        /**
         * Gets the current editor content.
         *
         * @param {Object} instance - the IDE instance object
         * @returns {string} the editor content, or empty string if instance is invalid
         */
        getValue: function(instance) {
            if (instance && instance.codeEditor) {
                return ZatoIDEEditorAce.getValue(instance.codeEditor);
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
                ZatoIDEEditorAce.setValue(instance.codeEditor, value);
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
                instance.codeEditor.aceEditor.setTheme(theme === 'dark' ? 'ace/theme/zato-dark' : 'ace/theme/zato');
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
                    ZatoIDEEditorAce.destroy(instance.codeEditor);
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
                ZatoIDEEditorAce.setLanguage(instance.codeEditor, language);
            }
        },

        /**
         * Focuses the editor.
         */
        focus: function(instance) {
            if (instance && instance.codeEditor) {
                ZatoIDEEditorAce.focus(instance.codeEditor);
            }
        }
    };

    window.ZatoIDE = ZatoIDE;

})();
