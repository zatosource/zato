(function() {
    'use strict';

    var ZatoIDEDebug = {

        handleDebugAction: function(instance, action) {
            if (action === 'connect-server') {
                this.connectToServer(instance);
            }
        },

        connectToServer: function(instance) {
            console.log('[ZatoIDE] connectToServer: START');
            var self = this;

            this.showDebugPanel(instance);

            if (instance.debuggerIDE && instance.debuggerIDE.debuggerUI) {
                ZatoDebuggerUI.showConnecting(instance.debuggerIDE.debuggerUI);
            }

            var serverBaseDir = '~/env/qs-1/server1';

            var csrfToken = this.getCsrfToken();

            fetch('/zato/ide/debug/connect-server/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    server_base_dir: serverBaseDir
                })
            })
            .then(function(response) {
                console.log('[ZatoIDE] connectToServer: response.status=' + response.status + ' response.ok=' + response.ok);
                return response.text();
            })
            .then(function(text) {
                console.log('[ZatoIDE] connectToServer: raw response text=' + text);
                var data = JSON.parse(text);
                console.log('[ZatoIDE] connectToServer: parsed response=', data);
                if (data.success) {
                    console.log('[ZatoIDE] connectToServer: attached to PID ' + data.target_pid + ' on port ' + data.debugpy_port);

                    if (!instance.debuggerIDE) {
                        console.error('[ZatoIDE] connectToServer: debuggerIDE not created');
                        return;
                    }

                    var debuggerInstance = instance.debuggerIDE.debugger;
                    if (!debuggerInstance) {
                        console.error('[ZatoIDE] connectToServer: debugger instance not found');
                        return;
                    }

                    debuggerInstance.attachSessionId = data.session_id;
                    debuggerInstance.attachMode = true;
                    debuggerInstance.state = 'running';

                    if (typeof ZatoDebuggerProtocol !== 'undefined') {
                        ZatoDebuggerProtocol.sessionIds[debuggerInstance.id] = data.session_id;
                        ZatoDebuggerProtocol.connections[debuggerInstance.id] = null;

                        var sseUrl = window.location.origin + '/zato/ide/debug/sse/?session_id=' + encodeURIComponent(data.session_id);
                        console.log('[ZatoIDE] connectToServer: opening SSE to ' + sseUrl);

                        var eventSource = new EventSource(sseUrl);
                        ZatoDebuggerProtocol.connections[debuggerInstance.id] = eventSource;

                        eventSource.onopen = function() {
                            console.log('[ZatoIDE] connectToServer: SSE onopen fired');
                            console.log('[ZatoIDE] connectToServer: instance.debuggerIDE=' + (instance.debuggerIDE ? 'ok' : 'null'));
                            console.log('[ZatoIDE] connectToServer: instance.debuggerIDE.debuggerUI=' + (instance.debuggerIDE && instance.debuggerIDE.debuggerUI ? 'ok' : 'null'));
                            if (instance.debuggerIDE && instance.debuggerIDE.debuggerUI) {
                                console.log('[ZatoIDE] connectToServer: calling hideConnecting and setConnected');
                                ZatoDebuggerUI.hideConnecting(instance.debuggerIDE.debuggerUI);
                                ZatoDebuggerUI.setConnected(instance.debuggerIDE.debuggerUI, true);
                            } else {
                                console.log('[ZatoIDE] connectToServer: debuggerUI not available, cannot update UI');
                            }
                            ZatoDebuggerCore.setState(debuggerInstance, ZatoDebuggerCore.DebugState.RUNNING);
                        };

                        eventSource.onmessage = function(event) {
                            ZatoDebuggerProtocol.handleMessage(debuggerInstance, event.data);
                        };

                        eventSource.addEventListener('debug', function(event) {
                            ZatoDebuggerProtocol.handleMessage(debuggerInstance, event.data);
                        });

                        eventSource.onerror = function() {
                            if (eventSource.readyState === EventSource.CLOSED) {
                                console.log('[ZatoIDE] connectToServer: SSE closed');
                                if (instance.debuggerIDE && instance.debuggerIDE.debuggerUI) {
                                    ZatoDebuggerUI.setConnected(instance.debuggerIDE.debuggerUI, false);
                                }
                                ZatoDebuggerCore.handleTerminated(debuggerInstance);
                            }
                        };
                    }
                } else {
                    console.error('[ZatoIDE] connectToServer: failed - ' + data.message);
                    if (instance.debuggerIDE && instance.debuggerIDE.debuggerUI) {
                        ZatoDebuggerUI.showError(instance.debuggerIDE.debuggerUI, data.message);
                    }
                }
            })
            .catch(function(error) {
                console.error('[ZatoIDE] connectToServer: error', error);
                if (instance.debuggerIDE && instance.debuggerIDE.debuggerUI) {
                    ZatoDebuggerUI.showError(instance.debuggerIDE.debuggerUI, error.message);
                }
            });
        },

        getCsrfToken: function() {
            var cookieValue = null;
            var name = 'csrftoken';
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].trim();
                    if (cookie.indexOf(name + '=') === 0) {
                        cookieValue = cookie.substring(name.length + 1);
                        break;
                    }
                }
            }
            return cookieValue;
        },

        showDebugPanel: function(instance) {
            if (instance.debuggerIDE) {
                ZatoDebuggerIDE.showDebugPanel(instance.debuggerIDE);
            } else if (typeof ZatoDebuggerIDE !== 'undefined') {
                instance.debuggerIDE = ZatoDebuggerIDE.create(instance, {
                    theme: instance.options.theme
                });
                ZatoDebuggerIDE.showDebugPanel(instance.debuggerIDE);
            }
        }
    };

    window.ZatoIDEDebug = ZatoIDEDebug;

})();
