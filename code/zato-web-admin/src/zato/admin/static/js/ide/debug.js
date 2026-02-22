(function() {
    'use strict';

    var ZatoIDEDebug = {

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
                console.log('[ZatoIDE] handleDebugAction: action is connect-server');
                this.connectToServer(instance);
            } else {
                console.log('[ZatoIDE] handleDebugAction: unknown action=' + action);
            }

            console.log('[ZatoIDE] handleDebugAction: END');
        },

        connectToServer: function(instance) {
            console.log('[ZatoIDE] connectToServer: START');
            var self = this;

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
                return response.json();
            })
            .then(function(data) {
                console.log('[ZatoIDE] connectToServer: response=', data);
                if (data.success) {
                    console.log('[ZatoIDE] connectToServer: attached to PID ' + data.target_pid + ' on port ' + data.debugpy_port);

                    self.showDebugPanel(instance);

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
                            console.log('[ZatoIDE] connectToServer: SSE connected');
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
                                ZatoDebuggerCore.handleTerminated(debuggerInstance);
                            }
                        };
                    }
                } else {
                    console.error('[ZatoIDE] connectToServer: failed - ' + data.message);
                    alert('Failed to connect to server: ' + data.message);
                }
            })
            .catch(function(error) {
                console.error('[ZatoIDE] connectToServer: error', error);
                alert('Error connecting to server: ' + error.message);
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
