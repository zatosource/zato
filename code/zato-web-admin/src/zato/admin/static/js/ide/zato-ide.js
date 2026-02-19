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
                        console.log('[TRACE-SYMBOL] dropdown.onChange: value="' + value + '" text="' + text + '"');
                        if (value) {
                            var line = parseInt(value, 10);
                            console.log('[TRACE-SYMBOL] dropdown.onChange: parsed line=' + line + ' from value="' + value + '"');
                            console.log('[TRACE-SYMBOL] dropdown.onChange: calling jumpToLine with line=' + line);
                            self.jumpToLine(instance, line);
                        } else {
                            console.log('[TRACE-SYMBOL] dropdown.onChange: value is empty, not jumping');
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
                    content: this.getPythonContent(),
                    language: 'python'
                },
                'queries.sql': {
                    content: this.getSQLContent(),
                    language: 'sql'
                },
                'config.yaml': {
                    content: this.getYAMLContent(),
                    language: 'yaml'
                },
                'data.json': {
                    content: this.getJSONContent(),
                    language: 'json'
                },
                'settings.ini': {
                    content: this.getINIContent(),
                    language: 'ini'
                }
            };
            instance.activeFile = 'my_service.py';
        },

        getPythonContent: function() {
            var lines = [];
            lines.push('# -*- coding: utf-8 -*-');
            lines.push('');
            lines.push('# Zato');
            lines.push('from zato.server.service import Service');
            lines.push('');
            lines.push('');
            lines.push('class EmailHandler(Service):');
            lines.push('');
            lines.push('    def handle(self):');
            lines.push('');
            lines.push('        # Connect to a Microsoft 365 IMAP connection by its name ..');
            lines.push('        conn = self.email.imap.get(\'My Automation\').conn');
            lines.push('');
            lines.push('        # .. get all messages matching filter criteria ("unread" by default)..');
            lines.push('        for msg_id, msg in conn.get():');
            lines.push('');
            lines.push('            # .. and access each of them.');
            lines.push('            self.logger.info(msg.data)');
            lines.push('');
            lines.push('');
            lines.push('class DatabaseSync(Service):');
            lines.push('');
            lines.push('    def handle(self):');
            lines.push('        connection = self.outgoing.sql.get(\'My Database\').session()');
            lines.push('        try:');
            lines.push('            result = connection.execute(\'SELECT * FROM users\')');
            lines.push('            for row in result:');
            lines.push('                self.logger.info(row)');
            lines.push('        finally:');
            lines.push('            connection.close()');
            lines.push('');
            lines.push('');
            lines.push('class CacheManager(Service):');
            lines.push('');
            lines.push('    def handle(self):');
            lines.push('        cache = self.cache.get_cache(\'default\')');
            lines.push('        cache.set(\'my_key\', \'my_value\', expiry=3600)');
            lines.push('        value = cache.get(\'my_key\')');
            lines.push('        self.response.payload = value');
            lines.push('');
            lines.push('');
            lines.push('class DUPLICATE_CLASS(Service):');
            lines.push('');
            lines.push('    def handle(self):');
            lines.push('        self.logger.info(\'First duplicate\')');
            lines.push('');
            lines.push('');
            lines.push('class DUPLICATE_CLASS(Service):');
            lines.push('');
            lines.push('    def handle(self):');
            lines.push('        self.logger.info(\'Second duplicate\')');
            lines.push('');
            lines.push('');
            lines.push('class NotificationSender(Service):');
            lines.push('');
            lines.push('    def handle(self):');
            lines.push('        self.outgoing.plain_http.get(\'Slack Webhook\').conn.post(');
            lines.push('            self.cid,');
            lines.push('            data={\'text\': \'Hello from Zato\'}');
            lines.push('        )');
            lines.push('');
            lines.push('');
            lines.push('class FileProcessor(Service):');
            lines.push('');
            lines.push('    def handle(self):');
            lines.push('        ftp = self.outgoing.ftp.get(\'My FTP\').conn');
            lines.push('        files = ftp.listdir(\'/incoming\')');
            lines.push('        for filename in files:');
            lines.push('            content = ftp.getfo(filename)');
            lines.push('            self.logger.info(\'Processing: %s\', filename)');
            lines.push('');
            lines.push('');
            lines.push('class QueueConsumer(Service):');
            lines.push('');
            lines.push('    def handle(self):');
            lines.push('        msg = self.request.raw_request');
            lines.push('        self.logger.info(\'Received message: %s\', msg)');
            lines.push('        self.response.payload = {\'status\': \'processed\'}');
            lines.push('');
            lines.push('');
            lines.push('class ScheduledTask(Service):');
            lines.push('');
            lines.push('    def handle(self):');
            lines.push('        self.logger.info(\'Running scheduled task at %s\', self.time.utcnow())');
            lines.push('        self.invoke(\'myapp.services.cleanup\')');
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
            console.log('[TRACE-SYMBOL] updateSymbols: starting');
            if (!instance.symbolDropdown || !window.ZatoIDESymbols) {
                console.log('[TRACE-SYMBOL] updateSymbols: missing symbolDropdown or ZatoIDESymbols');
                return;
            }

            var file = instance.files[instance.activeFile];
            if (!file) {
                console.log('[TRACE-SYMBOL] updateSymbols: no active file');
                return;
            }

            console.log('[TRACE-SYMBOL] updateSymbols: activeFile=' + instance.activeFile + ' language=' + file.language + ' content.length=' + (file.content ? file.content.length : 0));
            var symbols = ZatoIDESymbols.extract(file.content, file.language);
            console.log('[TRACE-SYMBOL] updateSymbols: extracted ' + symbols.length + ' symbols');
            var container = instance.symbolDropdown;
            var menu = container.querySelector('.zato-dropdown-menu');
            var textSpan = container.querySelector('.zato-dropdown-text');

            if (!menu) {
                console.log('[TRACE-SYMBOL] updateSymbols: no menu element found');
                return;
            }

            menu.innerHTML = '';

            if (symbols.length === 0) {
                console.log('[TRACE-SYMBOL] updateSymbols: no symbols, showing empty state');
                var emptyItem = document.createElement('div');
                emptyItem.className = 'zato-dropdown-item disabled';
                emptyItem.textContent = '(no symbols)';
                menu.appendChild(emptyItem);
                if (textSpan) {
                    textSpan.textContent = '-- symbols --';
                }
                return;
            }

            console.log('[TRACE-SYMBOL] updateSymbols: populating menu with ' + symbols.length + ' items');
            for (var i = 0; i < symbols.length; i++) {
                var symbol = symbols[i];
                console.log('[TRACE-SYMBOL] updateSymbols: adding item[' + i + '] name="' + symbol.name + '" data-value=' + symbol.line);
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
            console.log('[TRACE-SYMBOL] updateSymbols: done, default value=' + symbols[0].line);
        },

        /**
         * Jumps to a specific line in the editor.
         */
        jumpToLine: function(instance, line) {
            console.log('[TRACE-SYMBOL] jumpToLine: called with line=' + line);
            if (!instance.codeEditor) {
                console.log('[TRACE-SYMBOL] jumpToLine: no codeEditor, aborting');
                return;
            }

            var targetLine = Math.max(1, line - 2);
            console.log('[TRACE-SYMBOL] jumpToLine: computed targetLine=' + targetLine + ' (line=' + line + ' - 4)');
            console.log('[TRACE-SYMBOL] jumpToLine: calling ZatoIDEEditor.scrollToLine with targetLine=' + targetLine);
            ZatoIDEEditor.scrollToLine(instance.codeEditor, targetLine);
            console.log('[TRACE-SYMBOL] jumpToLine: scrollToLine called');
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
