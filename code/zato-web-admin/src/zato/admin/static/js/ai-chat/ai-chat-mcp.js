(function() {
    'use strict';

    var AIChatMCP = {

        servers: [],

        init: function() {
            this.loadServers();
        },

        loadServers: function(callback) {
            var self = this;

            fetch('/zato/ai-chat/mcp/servers/', {
                method: 'GET',
                credentials: 'same-origin'
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                self.servers = data.servers || [];
                console.debug('AIChatMCP.loadServers: loaded', self.servers.length, 'servers');
                if (callback) {
                    callback(self.servers);
                }
            })
            .catch(function(error) {
                console.warn('AIChatMCP.loadServers: error', error);
                self.servers = [];
                if (callback) {
                    callback([]);
                }
            });
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
        },

        addServer: function(serverConfig, callback) {
            var self = this;
            var csrfToken = this.getCsrfToken();

            console.log('AIChatMCP.addServer: adding server', serverConfig, 'csrfToken=', csrfToken ? 'present' : 'missing');

            var headers = {
                'Content-Type': 'application/json'
            };
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }

            fetch('/zato/ai-chat/mcp/servers/add/', {
                method: 'POST',
                credentials: 'same-origin',
                headers: headers,
                body: JSON.stringify(serverConfig)
            })
            .then(function(response) {
                console.log('AIChatMCP.addServer: response status', response.status);
                return response.json();
            })
            .then(function(data) {
                console.log('AIChatMCP.addServer: response data', data);
                if (data.success) {
                    self.loadServers(callback);
                } else {
                    console.warn('AIChatMCP.addServer: error', data.error);
                    if (callback) {
                        callback(null, data.error);
                    }
                }
            })
            .catch(function(error) {
                console.warn('AIChatMCP.addServer: fetch error', error);
                if (callback) {
                    callback(null, error);
                }
            });
        },

        removeServer: function(serverId, callback) {
            var self = this;
            var csrfToken = this.getCsrfToken();

            var headers = {
                'Content-Type': 'application/json'
            };
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }

            fetch('/zato/ai-chat/mcp/servers/remove/', {
                method: 'POST',
                credentials: 'same-origin',
                headers: headers,
                body: JSON.stringify({ id: serverId })
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                if (data.success) {
                    self.loadServers(callback);
                } else {
                    console.warn('AIChatMCP.removeServer: error', data.error);
                    if (callback) {
                        callback(null, data.error);
                    }
                }
            })
            .catch(function(error) {
                console.warn('AIChatMCP.removeServer: error', error);
                if (callback) {
                    callback(null, error);
                }
            });
        },

        updateServer: function(serverId, updates, callback) {
            var self = this;
            var csrfToken = this.getCsrfToken();

            var headers = {
                'Content-Type': 'application/json'
            };
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }

            fetch('/zato/ai-chat/mcp/servers/update/', {
                method: 'POST',
                credentials: 'same-origin',
                headers: headers,
                body: JSON.stringify({ id: serverId, updates: updates })
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                if (data.success) {
                    self.loadServers(callback);
                } else {
                    console.warn('AIChatMCP.updateServer: error', data.error);
                    if (callback) {
                        callback(null, data.error);
                    }
                }
            })
            .catch(function(error) {
                console.warn('AIChatMCP.updateServer: error', error);
                if (callback) {
                    callback(null, error);
                }
            });
        },

        getTools: function(callback) {
            fetch('/zato/ai-chat/mcp/tools/', {
                method: 'GET',
                credentials: 'same-origin'
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                var tools = data.tools || [];
                console.debug('AIChatMCP.getTools: loaded', tools.length, 'tools');
                if (callback) {
                    callback(tools);
                }
            })
            .catch(function(error) {
                console.warn('AIChatMCP.getTools: error', error);
                if (callback) {
                    callback([]);
                }
            });
        },

        buildManageServersHtml: function() {
            console.log('AIChatMCP.buildManageServersHtml: called, servers=', this.servers);
            var html = '';
            html += '<div class="ai-chat-config-back" id="ai-chat-mcp-back">';
            html += '<svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>';
            html += '<span>Back</span>';
            html += '</div>';
            html += '<div class="ai-chat-config-container">';
            html += '<div class="ai-chat-config-title">MCP servers</div>';
            html += '<div class="ai-chat-config-keys-list">';

            if (this.servers.length === 0) {
                html += '<div class="ai-chat-mcp-empty">No MCP servers configured</div>';
            } else {
                for (var i = 0; i < this.servers.length; i++) {
                    var server = this.servers[i];
                    html += '<div class="ai-chat-config-key-row" data-server-id="' + server.id + '">';
                    html += '<div class="ai-chat-config-key-info">';
                    html += '<div class="ai-chat-mcp-server-name">' + server.name + '</div>';
                    html += '</div>';
                    html += '<div class="ai-chat-mcp-server-actions">';
                    html += '<label class="ai-chat-mcp-toggle">';
                    html += '<input type="checkbox" class="ai-chat-mcp-enabled" ' + (server.enabled ? 'checked' : '') + '>';
                    html += '</label>';
                    html += '<button class="ai-chat-config-key-action ai-chat-config-key-remove ai-chat-mcp-remove" data-server-id="' + server.id + '">Remove</button>';
                    html += '</div>';
                    html += '</div>';
                }
            }

            html += '</div>';
            html += '<div class="ai-chat-mcp-add-section">';
            html += '<button class="ai-chat-config-save-button" id="ai-chat-mcp-add">Add an MCP server</button>';
            html += '</div>';
            html += '</div>';

            return html;
        },

        buildAddServerHtml: function() {
            console.log('AIChatMCP.buildAddServerHtml: called');
            var html = '';
            html += '<div class="ai-chat-config-back" id="ai-chat-mcp-add-back">';
            html += '<svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>';
            html += '<span>Back</span>';
            html += '</div>';
            html += '<div class="ai-chat-config-container">';
            html += '<div class="ai-chat-config-title">Add an MCP server</div>';

            html += '<div class="ai-chat-config-input-wrapper">';
            html += '<input type="text" class="ai-chat-config-api-key-input" id="ai-chat-mcp-endpoint" placeholder="Endpoint URL, e.g. https://zato.io/mcp">';
            html += '</div>';

            html += '<button class="ai-chat-config-save-button" id="ai-chat-mcp-save">Add server</button>';

            html += '</div>';

            return html;
        },

        extractNameFromUrl: function(url) {
            try {
                var parsed = new URL(url);
                var host = parsed.hostname;
                var parts = host.split('.');
                if (parts.length >= 2) {
                    return parts[parts.length - 2];
                }
                return host;
            } catch (e) {
                return 'mcp-server';
            }
        },

        generateServerId: function(name) {
            return name.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
        }
    };

    window.AIChatMCP = AIChatMCP;

})();
