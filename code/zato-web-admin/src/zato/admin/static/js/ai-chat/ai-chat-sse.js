(function() {
    'use strict';

    var AIChatSSE = {

        connections: {},

        connect: function(tabId, model, messages, callbacks) {
            var self = this;

            if (this.connections[tabId]) {
                this.disconnect(tabId);
            }

            var csrfToken = this.getCsrfToken();
            if (!csrfToken) {
                if (callbacks.onError) {
                    callbacks.onError('CSRF token not found');
                }
                return;
            }

            var body = JSON.stringify({
                model: model,
                messages: messages
            });

            var abortController = new AbortController();

            self.connections[tabId] = {
                abortController: abortController,
                active: true
            };

            fetch('/zato/ai-chat/invoke/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: body,
                signal: abortController.signal
            }).then(function(response) {
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status);
                }

                var reader = response.body.getReader();
                var decoder = new TextDecoder();
                var buffer = '';

                if (self.connections[tabId]) {
                    self.connections[tabId].reader = reader;
                }

                function processStream() {
                    if (!self.connections[tabId] || !self.connections[tabId].active) {
                        return;
                    }

                    reader.read().then(function(result) {
                        if (result.done) {
                            self.handleDisconnect(tabId, callbacks);
                            return;
                        }

                        buffer += decoder.decode(result.value, {stream: true});

                        var lines = buffer.split('\n');
                        buffer = lines.pop();

                        for (var i = 0; i < lines.length; i++) {
                            var line = lines[i].trim();
                            self.processLine(line, tabId, callbacks);
                        }

                        processStream();

                    }).catch(function(error) {
                        if (error.name === 'AbortError') {
                            return;
                        }
                        self.handleError(tabId, error, callbacks);
                    });
                }

                processStream();

            }).catch(function(error) {
                if (error.name === 'AbortError') {
                    return;
                }
                self.handleError(tabId, error, callbacks);
            });
        },

        processLine: function(line, tabId, callbacks) {
            if (!line) {
                return;
            }

            if (line.startsWith('event: ')) {
                this.currentEvent = line.substring(7);
                return;
            }

            if (line.startsWith('data: ')) {
                var dataStr = line.substring(6);
                var data = null;

                try {
                    data = JSON.parse(dataStr);
                } catch (e) {
                    return;
                }

                this.handleEvent(this.currentEvent, data, tabId, callbacks);
            }
        },

        handleEvent: function(eventType, data, tabId, callbacks) {
            console.log('[SSE] handleEvent:', eventType, data);
            if (eventType === 'chunk') {
                if (callbacks.onChunk) {
                    callbacks.onChunk(data.text);
                }
            } else if (eventType === 'done') {
                if (callbacks.onComplete) {
                    var inputTokens = data.input_tokens || 0;
                    var outputTokens = data.output_tokens || 0;
                    callbacks.onComplete(inputTokens, outputTokens);
                }
                this.disconnect(tabId);
            } else if (eventType === 'error') {
                if (callbacks.onError) {
                    callbacks.onError(data.message);
                }
                this.disconnect(tabId);
            } else if (eventType === 'object_changed') {
                console.log('[SSE] object_changed event received:', data);
                this.handleObjectChanged(data);
            }
        },

        handleObjectChanged: function(data) {
            console.log('[SSE] handleObjectChanged:', data);
            var action = data.action;
            var objectId = data.object_id;
            var objectName = data.object_name;

            if (action === 'delete') {
                var row = document.getElementById('tr_' + objectId);
                if (row) {
                    row.classList.add('zato-row-deleting');
                    setTimeout(function() {
                        row.remove();
                    }, 500);
                }
            } else if (action === 'create' || action === 'update') {
                this.refreshRow(objectId, objectName, action);
            }
        },

        refreshRow: function(objectId, objectName, action) {
            console.log('[SSE] refreshRow:', objectId, objectName, action);
            fetch(window.location.href)
                .then(function(response) {
                    return response.text();
                })
                .then(function(html) {
                    var parser = new DOMParser();
                    var doc = parser.parseFromString(html, 'text/html');
                    var newRow = null;
                    var oldRow = null;

                    if (objectId) {
                        newRow = doc.getElementById('tr_' + objectId);
                        oldRow = document.getElementById('tr_' + objectId);
                    } else if (objectName) {
                        var nameSpans = doc.querySelectorAll('.name-value');
                        for (var i = 0; i < nameSpans.length; i++) {
                            if (nameSpans[i].textContent.trim() === objectName) {
                                newRow = nameSpans[i].closest('tr');
                                break;
                            }
                        }
                    }

                    console.log('[SSE] newRow found:', !!newRow, 'oldRow found:', !!oldRow);

                    if (newRow) {
                        if (oldRow) {
                            oldRow.replaceWith(newRow);
                        } else {
                            var tbody = document.querySelector('#data-table tbody');
                            if (tbody) {
                                tbody.insertBefore(newRow, tbody.firstChild);
                            }
                        }
                        newRow.classList.add('zato-row-highlight');
                        setTimeout(function() {
                            newRow.classList.remove('zato-row-highlight');
                            newRow.classList.add('updated');
                        }, 1200);
                    }
                })
                .catch(function(error) {
                    console.error('Failed to refresh row:', error);
                });
        },

        handleDisconnect: function(tabId, callbacks) {
            delete this.connections[tabId];
            if (callbacks.onComplete) {
                callbacks.onComplete();
            }
        },

        handleError: function(tabId, error, callbacks) {
            this.disconnect(tabId);
            if (callbacks.onError) {
                callbacks.onError(error.message || String(error));
            }
        },

        disconnect: function(tabId) {
            var connection = this.connections[tabId];
            if (connection) {
                connection.active = false;
                delete this.connections[tabId];
            }
        },

        disconnectAll: function() {
            var tabIds = Object.keys(this.connections);
            for (var i = 0; i < tabIds.length; i++) {
                this.disconnect(tabIds[i]);
            }
        },

        isConnected: function(tabId) {
            return !!this.connections[tabId];
        },

        getCsrfToken: function() {
            var cookieValue = null;
            var name = 'csrftoken';
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },

        currentEvent: ''
    };

    window.AIChatSSE = AIChatSSE;

})();
