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

            var isNewConversation = messages.length === 1;
            var body = JSON.stringify({
                model: model,
                messages: messages,
                session_id: tabId,
                is_new_conversation: isNewConversation
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
            } else if (eventType === 'tool_progress') {
                console.log('[SSE] tool_progress event received:', data);
                if (callbacks.onToolProgress) {
                    callbacks.onToolProgress(data);
                }
            }
        },

        handleObjectChanged: function(data) {
            console.log('[SSE-TRACE] handleObjectChanged called with data:', JSON.stringify(data));
            var action = data.action;
            var objectId = data.object_id;
            var objectName = data.object_name;
            console.log('[SSE-TRACE] action:', action, 'objectId:', objectId, 'objectName:', objectName);

            if (action === 'delete') {
                console.log('[SSE-TRACE] delete action, looking for tr_' + objectId);
                var row = document.getElementById('tr_' + objectId);
                console.log('[SSE-TRACE] delete row found:', !!row);
                if (row) {
                    row.classList.add('zato-row-deleting');
                    setTimeout(function() {
                        row.remove();
                    }, 500);
                }
            } else if (action === 'create' || action === 'update') {
                console.log('[SSE-TRACE] create/update action, calling refreshRow');
                this.refreshRow(objectId, objectName, action);
            } else {
                console.log('[SSE-TRACE] unknown action, not handling:', action);
            }
        },

        refreshRow: function(objectId, objectName, action) {
            console.log('[SSE-TRACE] refreshRow called: objectId=' + objectId + ', objectName=' + objectName + ', action=' + action);
            console.log('[SSE-TRACE] current page URL:', window.location.href);
            
            fetch(window.location.href)
                .then(function(response) {
                    console.log('[SSE-TRACE] fetch response status:', response.status);
                    return response.text();
                })
                .then(function(html) {
                    console.log('[SSE-TRACE] fetched HTML length:', html.length);
                    var parser = new DOMParser();
                    var doc = parser.parseFromString(html, 'text/html');
                    var newRow = null;
                    var oldRow = null;

                    console.log('[SSE-TRACE] looking for row by objectId:', objectId);
                    if (objectId) {
                        newRow = doc.getElementById('tr_' + objectId);
                        oldRow = document.getElementById('tr_' + objectId);
                        console.log('[SSE-TRACE] by objectId: newRow=' + !!newRow + ', oldRow=' + !!oldRow);
                    }
                    
                    if (!newRow && objectName) {
                        console.log('[SSE-TRACE] looking for row by objectName:', objectName);
                        var nameSpans = doc.querySelectorAll('.name-value');
                        console.log('[SSE-TRACE] found ' + nameSpans.length + ' .name-value spans in fetched doc');
                        for (var i = 0; i < nameSpans.length; i++) {
                            var spanText = nameSpans[i].textContent.trim();
                            console.log('[SSE-TRACE] span[' + i + '] text: "' + spanText + '"');
                            if (spanText === objectName) {
                                newRow = nameSpans[i].closest('tr');
                                console.log('[SSE-TRACE] found matching row by name in .name-value, tr id:', newRow ? newRow.id : 'no id');
                                break;
                            }
                        }
                        if (!newRow) {
                            console.log('[SSE-TRACE] no .name-value match, searching in #data-table tbody td');
                            var dataTableTbody = doc.querySelector('#data-table tbody');
                            if (dataTableTbody) {
                                var allTds = dataTableTbody.querySelectorAll('td');
                                console.log('[SSE-TRACE] found ' + allTds.length + ' td elements in #data-table tbody');
                                for (var j = 0; j < allTds.length; j++) {
                                    var tdText = allTds[j].textContent.trim();
                                    if (tdText === objectName) {
                                        newRow = allTds[j].closest('tr');
                                        console.log('[SSE-TRACE] found matching row by name in td, tr id:', newRow ? newRow.id : 'no id');
                                        break;
                                    }
                                }
                            }
                        }
                    }

                    console.log('[SSE-TRACE] final: newRow found=' + !!newRow + ', oldRow found=' + !!oldRow);
                    if (newRow) {
                        console.log('[SSE-TRACE] newRow id:', newRow.id, 'newRow HTML preview:', newRow.outerHTML.substring(0, 200));
                    }

                    if (newRow) {
                        if (oldRow) {
                            console.log('[SSE-TRACE] replacing oldRow with newRow');
                            oldRow.replaceWith(newRow);
                            if (typeof $ !== 'undefined' && $.fn && $.fn.zato && $.fn.zato.data_table && $.fn.zato.data_table.parse) {
                                console.log('[SSE-TRACE] re-parsing data_table after replace');
                                $.fn.zato.data_table.parse();
                            }
                        } else {
                            console.log('[SSE-TRACE] no oldRow, inserting newRow into tbody');
                            var tbody = document.querySelector('#data-table tbody');
                            console.log('[SSE-TRACE] tbody found:', !!tbody);
                            if (tbody) {
                                var noResultsRow = tbody.querySelector('tr.ignore');
                                console.log('[SSE-TRACE] noResultsRow found:', !!noResultsRow);
                                if (noResultsRow) {
                                    console.log('[SSE-TRACE] removing noResultsRow');
                                    noResultsRow.remove();
                                }
                                console.log('[SSE-TRACE] inserting newRow at beginning of tbody');
                                tbody.insertBefore(newRow, tbody.firstChild);
                                console.log('[SSE-TRACE] insertion done');
                                if (typeof $ !== 'undefined' && $.fn && $.fn.zato && $.fn.zato.data_table && $.fn.zato.data_table.parse) {
                                    console.log('[SSE-TRACE] re-parsing data_table');
                                    $.fn.zato.data_table.parse();
                                }
                            } else {
                                console.log('[SSE-TRACE] no #data-table tbody found in current document');
                            }
                        }
                        newRow.classList.add('zato-row-highlight');
                        setTimeout(function() {
                            newRow.classList.remove('zato-row-highlight');
                            newRow.classList.add('updated');
                        }, 1200);
                    } else {
                        console.log('[SSE-TRACE] no newRow found, cannot update table');
                        console.log('[SSE-TRACE] dumping all tr ids from fetched doc:');
                        var allTrs = doc.querySelectorAll('tr');
                        for (var j = 0; j < Math.min(allTrs.length, 20); j++) {
                            console.log('[SSE-TRACE] tr[' + j + '] id:', allTrs[j].id || '(no id)');
                        }
                    }
                })
                .catch(function(error) {
                    console.error('[SSE-TRACE] fetch error:', error);
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
