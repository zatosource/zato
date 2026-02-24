(function() {
    'use strict';

    var instances = {};

    var ZatoTerminal = {

        create: function(containerId, options) {
            var container = document.getElementById(containerId);
            if (!container) {
                console.error('[ZatoTerminal] Container not found:', containerId);
                return null;
            }

            var instance = {
                id: containerId,
                container: container,
                options: options || {},
                terminal: null,
                sessionId: null,
                eventSource: null,
                isConnected: false
            };

            instances[containerId] = instance;
            this.render(instance);
            this.connect(instance);

            return instance;
        },

        getInstance: function(containerId) {
            return instances[containerId] || null;
        },

        render: function(instance) {
            instance.container.innerHTML = '';
            instance.container.className = 'zato-terminal-container';

            var terminalDiv = document.createElement('div');
            terminalDiv.className = 'zato-terminal-xterm';
            instance.container.appendChild(terminalDiv);

            if (typeof Terminal === 'undefined') {
                console.error('[ZatoTerminal] xterm.js Terminal not loaded');
                return;
            }

            instance.terminal = new Terminal({
                cursorBlink: true,
                cursorStyle: 'block',
                fontSize: 13,
                fontFamily: 'Consolas, "Courier New", monospace',
                lineHeight: 1.2,
                scrollback: 10000,
                theme: {
                    background: '#1e1e1e',
                    foreground: '#d4d4d4',
                    cursor: '#d4d4d4',
                    cursorAccent: '#1e1e1e',
                    selectionBackground: 'rgba(255, 255, 255, 0.3)',
                    black: '#000000',
                    red: '#cd3131',
                    green: '#0dbc79',
                    yellow: '#e5e510',
                    blue: '#2472c8',
                    magenta: '#bc3fbc',
                    cyan: '#11a8cd',
                    white: '#e5e5e5',
                    brightBlack: '#666666',
                    brightRed: '#f14c4c',
                    brightGreen: '#23d18b',
                    brightYellow: '#f5f543',
                    brightBlue: '#3b8eea',
                    brightMagenta: '#d670d6',
                    brightCyan: '#29b8db',
                    brightWhite: '#ffffff'
                }
            });

            instance.terminal.open(terminalDiv);
            instance.terminal.focus();

            var self = this;
            instance.terminal.onData(function(data) {
                self.sendInput(instance, data);
            });

            instance.terminal.onResize(function(size) {
                self.sendResize(instance, size.rows, size.cols);
            });
        },

        connect: function(instance) {
            var self = this;

            var csrfToken = this.getCsrfToken();
            var rows = instance.terminal.rows;
            var cols = instance.terminal.cols;

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/zato/ide/terminal/create/', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('X-CSRFToken', csrfToken);

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        var response = JSON.parse(xhr.responseText);
                        if (response.success) {
                            instance.sessionId = response.session_id;
                            instance.isConnected = true;
                            self.startStream(instance);
                        }
                    }
                }
            };

            xhr.send(JSON.stringify({ rows: rows, cols: cols }));
        },

        startStream: function(instance) {
            if (instance.eventSource) {
                instance.eventSource.close();
            }

            var url = '/zato/ide/terminal/stream/?session_id=' + encodeURIComponent(instance.sessionId);
            instance.eventSource = new EventSource(url);

            instance.eventSource.onmessage = function(event) {
                try {
                    var data = JSON.parse(event.data);
                    if (data.output) {
                        instance.terminal.write(data.output);
                    }
                } catch (e) {
                    console.error('[ZatoTerminal] Parse error:', e);
                }
            };

            instance.eventSource.addEventListener('closed', function() {
                instance.isConnected = false;
                instance.terminal.write('\r\n\x1b[31m[Session closed]\x1b[0m\r\n');
            });

            instance.eventSource.onerror = function() {
                if (instance.eventSource.readyState === EventSource.CLOSED) {
                    instance.isConnected = false;
                }
            };
        },

        sendInput: function(instance, data) {
            if (!instance.sessionId || !instance.isConnected) {
                return;
            }

            var csrfToken = this.getCsrfToken();

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/zato/ide/terminal/write/', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
            xhr.send(JSON.stringify({ session_id: instance.sessionId, data: data }));
        },

        sendResize: function(instance, rows, cols) {
            if (!instance.sessionId || !instance.isConnected) {
                return;
            }

            var csrfToken = this.getCsrfToken();

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/zato/ide/terminal/resize/', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
            xhr.send(JSON.stringify({ session_id: instance.sessionId, rows: rows, cols: cols }));
        },

        getCsrfToken: function() {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.indexOf('csrftoken=') === 0) {
                    return cookie.substring('csrftoken='.length);
                }
            }
            return '';
        },

        resize: function(instance) {
            if (instance && instance.terminal) {
                instance.terminal.fit && instance.terminal.fit();
            }
        },

        destroy: function(containerId) {
            var instance = instances[containerId];
            if (!instance) {
                return;
            }

            if (instance.eventSource) {
                instance.eventSource.close();
            }

            if (instance.sessionId) {
                var csrfToken = this.getCsrfToken();
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/zato/ide/terminal/close/', true);
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
                xhr.send(JSON.stringify({ session_id: instance.sessionId }));
            }

            if (instance.terminal) {
                instance.terminal.dispose();
            }

            instance.container.innerHTML = '';
            delete instances[containerId];
        }
    };

    window.ZatoTerminal = ZatoTerminal;

})();
