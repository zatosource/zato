(function() {
    'use strict';

    var AIChatSSE = {

        connections: {},

        connect: function(tabId, model, messages, callbacks) {
            console.debug('AIChatSSE.connect: tabId:', tabId, 'model:', model);

            var self = this;

            if (this.connections[tabId]) {
                this.disconnect(tabId);
            }

            var csrfToken = this.getCsrfToken();
            if (!csrfToken) {
                console.error('AIChatSSE.connect: CSRF token not found');
                if (callbacks.onError) {
                    callbacks.onError('CSRF token not found');
                }
                return;
            }

            var body = JSON.stringify({
                model: model,
                messages: messages
            });

            fetch('/zato/ai-chat/invoke/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: body
            }).then(function(response) {
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status);
                }

                var reader = response.body.getReader();
                var decoder = new TextDecoder();
                var buffer = '';

                self.connections[tabId] = {
                    reader: reader,
                    active: true
                };

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
                        console.error('AIChatSSE.processStream: error:', error);
                        self.handleError(tabId, error, callbacks);
                    });
                }

                processStream();

            }).catch(function(error) {
                console.error('AIChatSSE.connect: fetch error:', error);
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
                    console.error('AIChatSSE.processLine: JSON parse error:', e);
                    return;
                }

                this.handleEvent(this.currentEvent, data, tabId, callbacks);
            }
        },

        handleEvent: function(eventType, data, tabId, callbacks) {
            console.debug('AIChatSSE.handleEvent: type:', eventType, 'data:', data);

            if (eventType === 'chunk') {
                if (callbacks.onChunk) {
                    callbacks.onChunk(data.text);
                }
            } else if (eventType === 'done') {
                if (callbacks.onComplete) {
                    var inputTokens = data.input_tokens || 0;
                    var outputTokens = data.output_tokens || 0;
                    console.log('AIChatSSE done: input_tokens=' + inputTokens + ' output_tokens=' + outputTokens + ' data=', data);
                    callbacks.onComplete(inputTokens, outputTokens);
                }
                this.disconnect(tabId);
            } else if (eventType === 'error') {
                if (callbacks.onError) {
                    callbacks.onError(data.message);
                }
                this.disconnect(tabId);
            }
        },

        handleDisconnect: function(tabId, callbacks) {
            console.debug('AIChatSSE.handleDisconnect: tabId:', tabId);
            delete this.connections[tabId];
            if (callbacks.onComplete) {
                callbacks.onComplete();
            }
        },

        handleError: function(tabId, error, callbacks) {
            console.error('AIChatSSE.handleError: tabId:', tabId, 'error:', error);
            this.disconnect(tabId);
            if (callbacks.onError) {
                callbacks.onError(error.message || String(error));
            }
        },

        disconnect: function(tabId) {
            console.debug('AIChatSSE.disconnect: tabId:', tabId);

            var connection = this.connections[tabId];
            if (connection) {
                connection.active = false;
                if (connection.reader) {
                    try {
                        connection.reader.cancel();
                    } catch (e) {
                        console.debug('AIChatSSE.disconnect: reader cancel error:', e);
                    }
                }
                delete this.connections[tabId];
            }
        },

        disconnectAll: function() {
            console.debug('AIChatSSE.disconnectAll');
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
