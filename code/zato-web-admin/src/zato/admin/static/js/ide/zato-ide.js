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
            html += '<select id="' + instance.id + '-method-select" class="zato-ide-method-select" style="display: none;">';
            html += '<option value="">-- methods --</option>';
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
            lines.push('    def fetch_unread(self):');
            lines.push('        conn = self.email.imap.get(\'My Automation\').conn');
            lines.push('        return list(conn.get(criteria=\'UNSEEN\'))');
            lines.push('');
            lines.push('    def mark_as_read(self, msg_id):');
            lines.push('        conn = self.email.imap.get(\'My Automation\').conn');
            lines.push('        conn.mark_seen(msg_id)');
            lines.push('');
            lines.push('    def archive_message(self, msg_id):');
            lines.push('        conn = self.email.imap.get(\'My Automation\').conn');
            lines.push('        conn.move(msg_id, \'Archive\')');
            lines.push('');
            lines.push('    def delete_message(self, msg_id):');
            lines.push('        conn = self.email.imap.get(\'My Automation\').conn');
            lines.push('        conn.delete(msg_id)');
            lines.push('');
            lines.push('    def get_attachments(self, msg_id):');
            lines.push('        conn = self.email.imap.get(\'My Automation\').conn');
            lines.push('        msg = conn.get_by_id(msg_id)');
            lines.push('        return msg.attachments');
            lines.push('');
            lines.push('    def process_with_callbacks(self, msg_id):');
            lines.push('        def on_success(result):');
            lines.push('            self.logger.info(\'Success: %s\', result)');
            lines.push('        def on_error(error):');
            lines.push('            self.logger.error(\'Error: %s\', error)');
            lines.push('        def on_complete():');
            lines.push('            self.logger.info(\'Processing complete\')');
            lines.push('        def cleanup():');
            lines.push('            self.logger.info(\'Cleaning up resources\')');
            lines.push('        try:');
            lines.push('            result = self.process_message(msg_id)');
            lines.push('            on_success(result)');
            lines.push('        except Exception as e:');
            lines.push('            on_error(e)');
            lines.push('        finally:');
            lines.push('            on_complete()');
            lines.push('            cleanup()');
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
            lines.push('    def sync_users(self):');
            lines.push('        session = self.outgoing.sql.get(\'My Database\').session()');
            lines.push('        return session.execute(\'SELECT * FROM users WHERE active = true\')');
            lines.push('');
            lines.push('    def sync_orders(self):');
            lines.push('        session = self.outgoing.sql.get(\'My Database\').session()');
            lines.push('        return session.execute(\'SELECT * FROM orders WHERE status = pending\')');
            lines.push('');
            lines.push('    def update_record(self, table, record_id, data):');
            lines.push('        session = self.outgoing.sql.get(\'My Database\').session()');
            lines.push('        session.execute(f\'UPDATE {table} SET data = ? WHERE id = ?\', [data, record_id])');
            lines.push('');
            lines.push('    def delete_record(self, table, record_id):');
            lines.push('        session = self.outgoing.sql.get(\'My Database\').session()');
            lines.push('        session.execute(f\'DELETE FROM {table} WHERE id = ?\', [record_id])');
            lines.push('');
            lines.push('    def bulk_insert(self, table, records):');
            lines.push('        session = self.outgoing.sql.get(\'My Database\').session()');
            lines.push('        for record in records:');
            lines.push('            session.execute(f\'INSERT INTO {table} VALUES (?)\', [record])');
            lines.push('');
            lines.push('    def transactional_update(self, operations):');
            lines.push('        def begin_transaction():');
            lines.push('            return self.outgoing.sql.get(\'My Database\').session()');
            lines.push('        def commit(session):');
            lines.push('            session.commit()');
            lines.push('        def rollback(session):');
            lines.push('            session.rollback()');
            lines.push('        def execute_ops(session, ops):');
            lines.push('            for op in ops:');
            lines.push('                session.execute(op)');
            lines.push('        session = begin_transaction()');
            lines.push('        try:');
            lines.push('            execute_ops(session, operations)');
            lines.push('            commit(session)');
            lines.push('        except Exception:');
            lines.push('            rollback(session)');
            lines.push('            raise');
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
            lines.push('    def get_cached(self, key):');
            lines.push('        cache = self.cache.get_cache(\'default\')');
            lines.push('        return cache.get(key)');
            lines.push('');
            lines.push('    def set_cached(self, key, value, ttl):');
            lines.push('        cache = self.cache.get_cache(\'default\')');
            lines.push('        cache.set(key, value, expiry=ttl)');
            lines.push('');
            lines.push('    def invalidate(self, key):');
            lines.push('        cache = self.cache.get_cache(\'default\')');
            lines.push('        cache.delete(key)');
            lines.push('');
            lines.push('    def clear_all(self):');
            lines.push('        cache = self.cache.get_cache(\'default\')');
            lines.push('        cache.clear()');
            lines.push('');
            lines.push('    def get_stats(self):');
            lines.push('        cache = self.cache.get_cache(\'default\')');
            lines.push('        return cache.stats()');
            lines.push('');
            lines.push('    def batch_operations(self, items):');
            lines.push('        def set_item(cache, key, value):');
            lines.push('            cache.set(key, value)');
            lines.push('        def get_item(cache, key):');
            lines.push('            return cache.get(key)');
            lines.push('        def delete_item(cache, key):');
            lines.push('            cache.delete(key)');
            lines.push('        def process_batch(cache, batch):');
            lines.push('            for item in batch:');
            lines.push('                set_item(cache, item[\'key\'], item[\'value\'])');
            lines.push('        cache = self.cache.get_cache(\'default\')');
            lines.push('        process_batch(cache, items)');
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
            lines.push('    def send_slack(self, message):');
            lines.push('        self.outgoing.plain_http.get(\'Slack Webhook\').conn.post(');
            lines.push('            self.cid,');
            lines.push('            data={\'text\': message}');
            lines.push('        )');
            lines.push('');
            lines.push('    def send_email(self, recipient, subject, body):');
            lines.push('        self.email.smtp.get(\'Default SMTP\').send(');
            lines.push('            to=recipient,');
            lines.push('            subject=subject,');
            lines.push('            body=body');
            lines.push('        )');
            lines.push('');
            lines.push('    def send_sms(self, phone, message):');
            lines.push('        self.outgoing.plain_http.get(\'SMS Gateway\').conn.post(');
            lines.push('            self.cid,');
            lines.push('            data={\'phone\': phone, \'message\': message}');
            lines.push('        )');
            lines.push('');
            lines.push('    def broadcast(self, channels, message):');
            lines.push('        for channel in channels:');
            lines.push('            self.invoke(\'notifications.send\', {\'channel\': channel, \'message\': message})');
            lines.push('');
            lines.push('    def schedule_notification(self, delay, message):');
            lines.push('        self.invoke_async(\'notifications.send\', {\'message\': message}, delay=delay)');
            lines.push('');
            lines.push('    def send_with_retry(self, channel, message, max_retries):');
            lines.push('        def attempt_send(ch, msg):');
            lines.push('            return self.outgoing.plain_http.get(ch).conn.post(self.cid, data=msg)');
            lines.push('        def should_retry(error, attempt):');
            lines.push('            return attempt < max_retries');
            lines.push('        def wait_before_retry(attempt):');
            lines.push('            import time');
            lines.push('            time.sleep(2 ** attempt)');
            lines.push('        def log_failure(error):');
            lines.push('            self.logger.error(\'Send failed: %s\', error)');
            lines.push('        for attempt in range(max_retries):');
            lines.push('            try:');
            lines.push('                return attempt_send(channel, message)');
            lines.push('            except Exception as e:');
            lines.push('                if should_retry(e, attempt):');
            lines.push('                    wait_before_retry(attempt)');
            lines.push('                else:');
            lines.push('                    log_failure(e)');
            lines.push('                    raise');
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
            lines.push('    def download_file(self, remote_path):');
            lines.push('        ftp = self.outgoing.ftp.get(\'My FTP\').conn');
            lines.push('        return ftp.getfo(remote_path)');
            lines.push('');
            lines.push('    def upload_file(self, local_content, remote_path):');
            lines.push('        ftp = self.outgoing.ftp.get(\'My FTP\').conn');
            lines.push('        ftp.putfo(local_content, remote_path)');
            lines.push('');
            lines.push('    def list_directory(self, path):');
            lines.push('        ftp = self.outgoing.ftp.get(\'My FTP\').conn');
            lines.push('        return ftp.listdir(path)');
            lines.push('');
            lines.push('    def delete_file(self, remote_path):');
            lines.push('        ftp = self.outgoing.ftp.get(\'My FTP\').conn');
            lines.push('        ftp.remove(remote_path)');
            lines.push('');
            lines.push('    def move_file(self, source, destination):');
            lines.push('        ftp = self.outgoing.ftp.get(\'My FTP\').conn');
            lines.push('        ftp.rename(source, destination)');
            lines.push('');
            lines.push('    def process_directory(self, path, handler):');
            lines.push('        def list_files(ftp, dir_path):');
            lines.push('            return ftp.listdir(dir_path)');
            lines.push('        def read_file(ftp, file_path):');
            lines.push('            return ftp.getfo(file_path)');
            lines.push('        def archive_file(ftp, file_path):');
            lines.push('            ftp.rename(file_path, file_path + \'.done\')');
            lines.push('        def log_processed(file_path):');
            lines.push('            self.logger.info(\'Processed: %s\', file_path)');
            lines.push('        ftp = self.outgoing.ftp.get(\'My FTP\').conn');
            lines.push('        for f in list_files(ftp, path):');
            lines.push('            content = read_file(ftp, f)');
            lines.push('            handler(content)');
            lines.push('            archive_file(ftp, f)');
            lines.push('            log_processed(f)');
            lines.push('');
            lines.push('');
            lines.push('class QueueConsumer(Service):');
            lines.push('');
            lines.push('    def handle(self):');
            lines.push('        msg = self.request.raw_request');
            lines.push('        self.logger.info(\'Received message: %s\', msg)');
            lines.push('        self.response.payload = {\'status\': \'processed\'}');
            lines.push('');
            lines.push('    def process_message(self, msg):');
            lines.push('        self.logger.info(\'Processing: %s\', msg)');
            lines.push('        return {\'status\': \'ok\'}');
            lines.push('');
            lines.push('    def validate_message(self, msg):');
            lines.push('        if not msg.get(\'id\'):');
            lines.push('            raise ValueError(\'Missing message id\')');
            lines.push('        return True');
            lines.push('');
            lines.push('    def acknowledge(self, msg_id):');
            lines.push('        self.pubsub.acknowledge(msg_id)');
            lines.push('');
            lines.push('    def reject(self, msg_id, reason):');
            lines.push('        self.pubsub.reject(msg_id, reason=reason)');
            lines.push('');
            lines.push('    def requeue(self, msg_id):');
            lines.push('        self.pubsub.requeue(msg_id)');
            lines.push('');
            lines.push('    def process_batch(self, messages):');
            lines.push('        def validate(msg):');
            lines.push('            return msg.get(\'id\') is not None');
            lines.push('        def transform(msg):');
            lines.push('            return {\'id\': msg[\'id\'], \'processed\': True}');
            lines.push('        def store(msg):');
            lines.push('            self.cache.get_cache(\'processed\').set(msg[\'id\'], msg)');
            lines.push('        def notify(msg):');
            lines.push('            self.pubsub.publish(\'processed\', msg)');
            lines.push('        for msg in messages:');
            lines.push('            if validate(msg):');
            lines.push('                transformed = transform(msg)');
            lines.push('                store(transformed)');
            lines.push('                notify(transformed)');
            lines.push('');
            lines.push('');
            lines.push('class ScheduledTask(Service):');
            lines.push('');
            lines.push('    def handle(self):');
            lines.push('        self.logger.info(\'Running scheduled task at %s\', self.time.utcnow())');
            lines.push('        self.invoke(\'myapp.services.cleanup\')');
            lines.push('');
            lines.push('    def run_cleanup(self):');
            lines.push('        self.invoke(\'myapp.services.cleanup\')');
            lines.push('');
            lines.push('    def run_backup(self):');
            lines.push('        self.invoke(\'myapp.services.backup\')');
            lines.push('');
            lines.push('    def run_report(self):');
            lines.push('        self.invoke(\'myapp.services.generate_report\')');
            lines.push('');
            lines.push('    def run_sync(self):');
            lines.push('        self.invoke(\'myapp.services.sync_external\')');
            lines.push('');
            lines.push('    def run_maintenance(self):');
            lines.push('        self.invoke(\'myapp.services.maintenance\')');
            lines.push('');
            lines.push('    def run_with_logging(self, task_name):');
            lines.push('        def log_start(name):');
            lines.push('            self.logger.info(\'Starting task: %s\', name)');
            lines.push('        def log_end(name):');
            lines.push('            self.logger.info(\'Finished task: %s\', name)');
            lines.push('        def log_error(name, error):');
            lines.push('            self.logger.error(\'Task %s failed: %s\', name, error)');
            lines.push('        def execute_task(name):');
            lines.push('            self.invoke(f\'myapp.services.{name}\')');
            lines.push('        log_start(task_name)');
            lines.push('        try:');
            lines.push('            execute_task(task_name)');
            lines.push('            log_end(task_name)');
            lines.push('        except Exception as e:');
            lines.push('            log_error(task_name, e)');
            lines.push('            raise');
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
            instance.codeEditor = ZatoIDEEditorAce.create(editorArea, {
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
                    self.syncDropdownsToLine(instance, line);
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
                instance.files[instance.activeFile].content = ZatoIDEEditorAce.getValue(instance.codeEditor);
            }

            instance.activeFile = filename;
            var file = instance.files[filename];

            if (instance.codeEditor) {
                ZatoIDEEditorAce.setValue(instance.codeEditor, file.content);
                ZatoIDEEditorAce.setLanguage(instance.codeEditor, file.language);
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
