(function() {
    'use strict';

    var AIChatMCP = {

        servers: [],
        selectedServer: null,
        selectedServerTools: [],
        loadingTools: false,

        init: function() {
            this.loadServers();
        },

        getServerById: function(serverId) {
            for (var i = 0; i < this.servers.length; i++) {
                if (this.servers[i].id === serverId) {
                    return this.servers[i];
                }
            }
            return null;
        },

        loadToolsForServer: function(serverId, callback) {
            var self = this;
            var csrfToken = this.getCsrfToken();

            self.loadingTools = true;
            self.selectedServerTools = [];

            var headers = {
                'Content-Type': 'application/json'
            };
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }

            fetch('/zato/ai-chat/mcp/tools/?server_id=' + encodeURIComponent(serverId), {
                method: 'GET',
                credentials: 'same-origin',
                headers: headers
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                self.loadingTools = false;
                self.selectedServerTools = (data.tools || []).filter(function(t) {
                    return t._mcp_server_id === serverId;
                });
                if (callback) {
                    callback(self.selectedServerTools);
                }
            })
            .catch(function(error) {
                console.warn('AIChatMCP.loadToolsForServer: error', error);
                self.loadingTools = false;
                self.selectedServerTools = [];
                if (callback) {
                    callback([]);
                }
            });
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
                return response.json();
            })
            .then(function(data) {
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
            var html = '';
            html += '<div class="ai-chat-config-container">';
            html += '<div class="ai-chat-config-content-wrapper">';
            html += AIChatConfig.buildBackButtonHtml('ai-chat-mcp-back');

            if (this.servers.length === 0) {
                html += '<div class="ai-chat-config-title">No MCP servers configured</div>';
                html += '<button class="ai-chat-config-save-button" id="ai-chat-mcp-add">Add server</button>';
            } else {
                html += '<div class="ai-chat-mcp-header-row">';
                html += '<div class="ai-chat-config-title">MCP servers</div>';
                html += '<button class="ai-chat-mcp-add-btn" id="ai-chat-mcp-add">Add server</button>';
                html += '</div>';
                html += '<div class="ai-chat-config-keys-list">';
                for (var i = 0; i < this.servers.length; i++) {
                    var server = this.servers[i];
                    html += '<div class="ai-chat-mcp-server-row" data-server-id="' + server.id + '">';
                    html += '<div class="ai-chat-mcp-server-info">';
                    html += '<div class="ai-chat-mcp-server-name-link" data-server-id="' + server.id + '">' + server.name + '</div>';
                    html += '<div class="ai-chat-mcp-server-endpoint">' + server.endpoint + '</div>';
                    html += '</div>';
                    html += '<div class="ai-chat-mcp-server-actions">';
                    html += '<label class="ai-chat-mcp-switch">';
                    html += '<input type="checkbox" class="ai-chat-mcp-enabled" ' + (server.enabled ? 'checked' : '') + '>';
                    html += '<span class="ai-chat-mcp-slider"></span>';
                    html += '</label>';
                    html += ZatoConfirmButton.buildEditHtml(server.id, 'ai-chat-mcp-edit-btn');
                    html += ZatoConfirmButton.buildRemoveHtml(server.id, 'ai-chat-mcp-remove-btn');
                    html += '</div>';
                    html += '</div>';
                }
                html += '</div>';
            }

            html += '</div>';
            html += '</div>';

            return html;
        },

        buildServerDetailHtml: function(server, tools, loading) {
            var html = '';
            html += '<div class="ai-chat-config-container">';
            html += '<div class="ai-chat-config-content-wrapper">';
            html += AIChatConfig.buildBackButtonHtml('ai-chat-mcp-detail-back');
            html += '<div class="ai-chat-config-title">' + server.name + '</div>';
            html += '<div class="ai-chat-mcp-server-url">' + server.endpoint + '</div>';

            if (loading) {
                html += '<div class="ai-chat-mcp-loading">';
                html += '<img src="/static/img/spinner.svg" class="ai-chat-spinner-icon ai-chat-spinner-large" alt="">';
                html += '<span>Loading tools...</span>';
                html += '</div>';
            } else if (tools && tools.length > 0) {
                html += '<div class="ai-chat-mcp-tools-list">';
                for (var i = 0; i < tools.length; i++) {
                    var tool = tools[i];
                    html += '<div class="ai-chat-mcp-tool">';
                    html += '<div class="ai-chat-mcp-tool-name">' + tool.name + '</div>';
                    html += '<div class="ai-chat-mcp-tool-desc">' + (tool.description || 'No description') + '</div>';
                    html += '</div>';
                }
                html += '</div>';
            } else {
                html += '<div class="ai-chat-mcp-empty">No tools available</div>';
            }

            html += '</div>';
            html += '</div>';
            return html;
        },

        buildEditServerHtml: function(server) {
            var html = '';
            html += '<div class="ai-chat-config-container">';
            html += '<div class="ai-chat-config-content-wrapper">';
            html += AIChatConfig.buildBackButtonHtml('ai-chat-mcp-edit-back');
            html += '<div class="ai-chat-config-title">Edit ' + server.name + '</div>';

            html += '<div class="ai-chat-config-input-wrapper">';
            html += '<input type="text" class="ai-chat-config-api-key-input" id="ai-chat-mcp-edit-endpoint" value="' + server.endpoint + '" placeholder="Endpoint URL" autofocus>';
            html += '</div>';

            html += '<button class="ai-chat-config-save-button" id="ai-chat-mcp-edit-save" data-server-id="' + server.id + '">Save changes</button>';

            html += '</div>';
            html += '</div>';
            return html;
        },

        buildAddServerHtml: function() {
            var html = '';
            html += '<div class="ai-chat-config-container">';
            html += '<div class="ai-chat-config-content-wrapper">';
            html += AIChatConfig.buildBackButtonHtml('ai-chat-mcp-add-back');
            html += '<div class="ai-chat-config-title">Add an MCP server</div>';

            html += '<div class="ai-chat-config-input-wrapper">';
            html += '<input type="text" class="ai-chat-config-api-key-input" id="ai-chat-mcp-endpoint" placeholder="Endpoint URL, e.g. https://zato.io/mcp" autofocus>';
            html += '</div>';

            html += '<button class="ai-chat-config-save-button" id="ai-chat-mcp-save">Save server</button>';

            html += '</div>';
            html += '</div>';

            return html;
        }
    };

    window.AIChatMCP = AIChatMCP;

})();
