(function() {
    'use strict';

    /**
     * ZatoDebuggerProtocol - debug adapter protocol (DAP) communication.
     *
     * Handles communication with the Python debugger backend via SSE (Server-Sent Events)
     * for receiving events and HTTP POST for sending commands.
     * Implements DAP messages: launch, attach, setBreakpoints, continue, next,
     * stepIn, stepOut, pause, stackTrace, scopes, variables, evaluate, disconnect.
     */
    var ZatoDebuggerProtocol = {

        connections: {},

        sequenceCounter: 1,

        pendingRequests: {},

        sessionIds: {},

        getNextSeq: function() {
            return this.sequenceCounter++;
        },

        connect: function(instance, callback) {
            console.log('[DebugProtocol] connect: START instance.id=' + instance.id);
            var self = this;

            if (this.connections[instance.id]) {
                console.log('[DebugProtocol] connect: closing existing connection');
                this.disconnect(instance);
            }

            var sessionId = 'debug-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
            this.sessionIds[instance.id] = sessionId;
            console.log('[DebugProtocol] connect: sessionId=' + sessionId);

            var sseUrl = this.getSSEUrl(instance, sessionId);
            console.log('[DebugProtocol] connect: sseUrl=' + sseUrl);

            var eventSource = new EventSource(sseUrl);

            eventSource.onopen = function() {
                console.log('[DebugProtocol] SSE connected');
                self.connections[instance.id] = eventSource;
                if (callback) {
                    callback(true);
                }
            };

            eventSource.onmessage = function(event) {
                console.log('[DebugProtocol] SSE message received');
                self.handleMessage(instance, event.data);
            };

            eventSource.onerror = function(error) {
                if (eventSource.readyState === EventSource.CLOSED) {
                    console.log('[DebugProtocol] SSE connection closed');
                    delete self.connections[instance.id];
                    delete self.sessionIds[instance.id];
                    ZatoDebuggerCore.handleTerminated(instance);
                }
                if (callback) {
                    callback(false, 'Connection error');
                    callback = null;
                }
            };

            eventSource.addEventListener('debug', function(event) {
                console.log('[DebugProtocol] SSE debug event received');
                self.handleMessage(instance, event.data);
            });
        },

        disconnect: function(instance) {
            console.log('[DebugProtocol] disconnect: instance.id=' + instance.id);
            var eventSource = this.connections[instance.id];
            if (eventSource) {
                this.sendRequest(instance, 'disconnect', { restart: false });
                eventSource.close();
                delete this.connections[instance.id];
                delete this.sessionIds[instance.id];
            }
        },

        getSSEUrl: function(instance, sessionId) {
            var baseUrl = window.location.origin;
            return baseUrl + '/zato/ide/debug/sse/?session_id=' + encodeURIComponent(sessionId);
        },

        getCommandUrl: function(instance) {
            var baseUrl = window.location.origin;
            return baseUrl + '/zato/ide/debug/command/';
        },

        sendRequest: function(instance, command, args, callback) {
            console.log('[DebugProtocol] sendRequest: command=' + command);
            var sessionId = this.sessionIds[instance.id];
            if (!sessionId) {
                console.warn('[DebugProtocol] sendRequest: no session, cannot send');
                if (callback) {
                    callback(null, 'Not connected');
                }
                return;
            }

            var seq = this.getNextSeq();
            var request = {
                seq: seq,
                type: 'request',
                command: command,
                arguments: args || {},
                session_id: sessionId
            };

            if (callback) {
                this.pendingRequests[seq] = callback;
            }

            var self = this;
            var url = this.getCommandUrl(instance);
            console.log('[DebugProtocol] sendRequest: POST to ' + url);

            var csrfToken = this.getCsrfToken();
            console.log('[DebugProtocol] sendRequest: csrfToken=' + (csrfToken ? 'found' : 'not found'));

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(request)
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                console.log('[DebugProtocol] sendRequest: response received for seq=' + seq);
                if (data.request_seq === seq) {
                    self.handleResponse(instance, data);
                }
            })
            .catch(function(error) {
                console.error('[DebugProtocol] sendRequest: error:', error);
                if (callback) {
                    delete self.pendingRequests[seq];
                    callback(null, error.message);
                }
            });

            console.log('[DebugProtocol] sendRequest: sent command=' + command);
        },

        handleMessage: function(instance, data) {
            var message;
            try {
                message = JSON.parse(data);
            } catch (e) {
                console.error('[DebugProtocol] Failed to parse message:', e);
                return;
            }

            console.log('[DebugProtocol] Received:', message.type, message.command || message.event);

            if (message.type === 'response') {
                this.handleResponse(instance, message);
            } else if (message.type === 'event') {
                this.handleEvent(instance, message);
            }
        },

        handleResponse: function(instance, response) {
            var callback = this.pendingRequests[response.request_seq];
            if (callback) {
                delete this.pendingRequests[response.request_seq];
                if (response.success) {
                    callback(response.body, null);
                } else {
                    callback(null, response.message);
                }
            }
        },

        handleEvent: function(instance, event) {
            console.log('[DebugProtocol] handleEvent: event=' + event.event + ' body=' + JSON.stringify(event.body));
            switch (event.event) {
                case 'connected':
                    console.log('[DebugProtocol] handleEvent: connected, ignoring');
                    break;
                case 'initialized':
                    console.log('[DebugProtocol] handleEvent: calling handleInitialized');
                    this.handleInitialized(instance);
                    break;
                case 'stopped':
                    console.log('[DebugProtocol] handleEvent: calling handleStopped');
                    this.handleStopped(instance, event.body);
                    break;
                case 'continued':
                    this.handleContinued(instance, event.body);
                    break;
                case 'terminated':
                    this.handleTerminated(instance);
                    break;
                case 'output':
                    this.handleOutput(instance, event.body);
                    break;
                case 'breakpoint':
                    this.handleBreakpointEvent(instance, event.body);
                    break;
                case 'thread':
                    this.handleThread(instance, event.body);
                    break;
                default:
                    console.log('[DebugProtocol] handleEvent: unknown event=' + event.event);
                    break;
            }
        },

        handleInitialized: function(instance) {
            console.log('[DebugProtocol] handleInitialized: START');
            var breakpoints = ZatoDebuggerCore.getAllBreakpoints(instance);
            console.log('[DebugProtocol] handleInitialized: breakpoints.length=' + breakpoints.length);

            var currentFile = instance.currentFile || 'my_service.py';
            console.log('[DebugProtocol] handleInitialized: currentFile=' + currentFile);

            if (breakpoints.length === 0) {
                var firstBreakableLine = this.findFirstBreakableLine(instance);
                console.log('[DebugProtocol] handleInitialized: no breakpoints, auto-setting on line ' + firstBreakableLine);
                ZatoDebuggerCore.addBreakpoint(instance, currentFile, firstBreakableLine);
                breakpoints = ZatoDebuggerCore.getAllBreakpoints(instance);
            }

            var fileBreakpoints = {};
            for (var i = 0; i < breakpoints.length; i++) {
                var bp = breakpoints[i];
                var file = bp.file || currentFile;
                if (!fileBreakpoints[file]) {
                    fileBreakpoints[file] = [];
                }
                fileBreakpoints[file].push(bp);
            }

            for (var file in fileBreakpoints) {
                console.log('[DebugProtocol] handleInitialized: setting breakpoints for file=' + file);
                this.setBreakpoints(instance, file, fileBreakpoints[file]);
            }

            console.log('[DebugProtocol] handleInitialized: sending configurationDone');
            this.sendRequest(instance, 'configurationDone', {}, function(body, error) {
                console.log('[DebugProtocol] handleInitialized: configurationDone response, error=' + error);
            });
        },

        handleStopped: function(instance, body) {
            console.log('[DebugProtocol] handleStopped: body=' + JSON.stringify(body));
            var threadId = body.threadId || 1;
            var reason = body.reason;

            console.log('[DebugProtocol] handleStopped: calling ZatoDebuggerCore.handleBreakpointHit');
            ZatoDebuggerCore.handleBreakpointHit(instance, threadId, reason);
            console.log('[DebugProtocol] handleStopped: done');
        },

        handleContinued: function(instance, body) {
            ZatoDebuggerCore.setState(instance, ZatoDebuggerCore.DebugState.RUNNING);
        },

        findFirstBreakableLine: function(instance) {
            var content = '';
            if (instance.session && instance.session.fileContent) {
                content = instance.session.fileContent;
            }
            if (!content) {
                return 1;
            }

            var lines = content.split('\n');
            for (var i = 0; i < lines.length; i++) {
                var line = lines[i].trim();
                if (line.length === 0) {
                    continue;
                }
                if (line.charAt(0) === '#') {
                    continue;
                }
                if (line.substring(0, 3) === '"""' || line.substring(0, 3) === "'''") {
                    continue;
                }
                return i + 1;
            }
            return 1;
        },

        handleTerminated: function(instance) {
            ZatoDebuggerCore.handleTerminated(instance);
        },

        handleOutput: function(instance, body) {
            var category = body.category || 'console';
            var output = body.output || '';
            ZatoDebuggerCore.handleOutput(instance, category, output);
        },

        handleBreakpointEvent: function(instance, body) {
            var bp = body.breakpoint;
            if (bp && bp.id) {
                var allBps = ZatoDebuggerCore.getAllBreakpoints(instance);
                for (var i = 0; i < allBps.length; i++) {
                    if (allBps[i].id === bp.id) {
                        allBps[i].state = bp.verified ?
                            ZatoDebuggerCore.BreakpointState.VERIFIED :
                            ZatoDebuggerCore.BreakpointState.INVALID;
                        break;
                    }
                }
            }
        },

        handleThread: function(instance, body) {
            console.log('[DebugProtocol] Thread event:', body.reason, body.threadId);
        },

        initialize: function(instance, callback) {
            var args = {
                clientID: 'zato-ide',
                clientName: 'Zato IDE',
                adapterID: 'python',
                pathFormat: 'path',
                linesStartAt1: true,
                columnsStartAt1: true,
                supportsVariableType: true,
                supportsVariablePaging: false,
                supportsRunInTerminalRequest: false,
                locale: 'en-us'
            };

            this.sendRequest(instance, 'initialize', args, function(body, error) {
                if (callback) {
                    callback(body, error);
                }
            });
        },

        launch: function(instance, config, callback) {
            console.log('[DebugProtocol] launch: START');
            var self = this;

            var debuggerInstance = instance;
            var code = '';
            if (debuggerInstance.session && debuggerInstance.session.fileContent) {
                code = debuggerInstance.session.fileContent;
            } else if (config.code) {
                code = config.code;
            }
            console.log('[DebugProtocol] launch: code.length=' + code.length);

            this.connect(instance, function(connected, error) {
                console.log('[DebugProtocol] launch: connect callback connected=' + connected);
                if (!connected) {
                    console.log('[DebugProtocol] launch: connect failed error=' + error);
                    if (callback) {
                        callback(false, error);
                    }
                    return;
                }

                self.initialize(instance, function(body, initError) {
                    console.log('[DebugProtocol] launch: initialize callback body=' + JSON.stringify(body) + ' error=' + initError);
                    if (initError) {
                        console.log('[DebugProtocol] launch: initialize error=' + initError);
                        if (callback) {
                            callback(false, initError);
                        }
                        return;
                    }

                    var args = {
                        type: 'python',
                        request: 'launch',
                        name: 'Debug Current File',
                        program: config.program,
                        code: code,
                        pythonPath: config.pythonPath || 'python3',
                        stopOnEntry: config.stopOnEntry !== false,
                        console: 'integratedTerminal',
                        cwd: '${workspaceFolder}',
                        env: {},
                        justMyCode: true
                    };

                    console.log('[DebugProtocol] launch: sending launch request with code.length=' + code.length);
                    self.sendRequest(instance, 'launch', args, function(launchBody, launchError) {
                        console.log('[DebugProtocol] launch: launch response received error=' + launchError);
                        if (callback) {
                            callback(!launchError, launchError);
                        }
                    });
                });
            });
        },

        attach: function(instance, config, callback) {
            var self = this;

            this.connect(instance, function(connected, error) {
                if (!connected) {
                    if (callback) {
                        callback(false, error);
                    }
                    return;
                }

                self.initialize(instance, function(capabilities, initError) {
                    if (initError) {
                        if (callback) {
                            callback(false, initError);
                        }
                        return;
                    }

                    var args = {
                        type: 'python',
                        request: 'attach',
                        name: 'Attach to Server',
                        connect: {
                            host: config.host || 'localhost',
                            port: config.port || 5678
                        },
                        pathMappings: config.pathMappings || [],
                        justMyCode: true
                    };

                    self.sendRequest(instance, 'attach', args, function(body, attachError) {
                        if (callback) {
                            callback(!attachError, attachError);
                        }
                    });
                });
            });
        },

        setBreakpoints: function(instance, file, breakpoints, callback) {
            var bps = [];
            for (var i = 0; i < breakpoints.length; i++) {
                var bp = breakpoints[i];
                var bpData = { line: bp.line };
                if (bp.condition) {
                    bpData.condition = bp.condition;
                }
                if (bp.hitCondition) {
                    bpData.hitCondition = bp.hitCondition;
                }
                bps.push(bpData);
            }

            var args = {
                source: { path: file },
                breakpoints: bps,
                sourceModified: false
            };

            this.sendRequest(instance, 'setBreakpoints', args, function(body, error) {
                if (body && body.breakpoints) {
                    for (var j = 0; j < body.breakpoints.length; j++) {
                        var result = body.breakpoints[j];
                        if (j < breakpoints.length) {
                            breakpoints[j].state = result.verified ?
                                ZatoDebuggerCore.BreakpointState.VERIFIED :
                                ZatoDebuggerCore.BreakpointState.INVALID;
                            if (result.id) {
                                breakpoints[j].remoteId = result.id;
                            }
                        }
                    }
                }
                if (callback) {
                    callback(body, error);
                }
            });
        },

        clearAllBreakpoints: function(instance) {
            var ws = this.connections[instance.id];
            if (!ws) {
                return;
            }

            var files = {};
            var allBps = ZatoDebuggerCore.getAllBreakpoints(instance);
            for (var i = 0; i < allBps.length; i++) {
                files[allBps[i].file] = true;
            }

            for (var file in files) {
                this.setBreakpoints(instance, file, []);
            }
        },

        continue_: function(instance, threadId, callback) {
            var args = { threadId: threadId };
            this.sendRequest(instance, 'continue', args, callback);
        },

        pause: function(instance, threadId, callback) {
            var args = { threadId: threadId };
            this.sendRequest(instance, 'pause', args, callback);
        },

        next: function(instance, threadId, callback) {
            var args = { threadId: threadId, granularity: 'statement' };
            this.sendRequest(instance, 'next', args, callback);
        },

        stepIn: function(instance, threadId, callback) {
            var args = { threadId: threadId, granularity: 'statement' };
            this.sendRequest(instance, 'stepIn', args, callback);
        },

        stepOut: function(instance, threadId, callback) {
            var args = { threadId: threadId, granularity: 'statement' };
            this.sendRequest(instance, 'stepOut', args, callback);
        },

        stackTrace: function(instance, threadId, callback) {
            var self = this;
            var args = {
                threadId: threadId,
                startFrame: 0,
                levels: 20
            };

            this.sendRequest(instance, 'stackTrace', args, function(body, error) {
                if (body && body.stackFrames) {
                    ZatoDebuggerCore.setCallStack(instance, body.stackFrames);

                    if (body.stackFrames.length > 0) {
                        var topFrame = body.stackFrames[0];
                        instance.currentFrame = topFrame.id;
                        self.scopes(instance, topFrame.id);
                    }
                }
                if (callback) {
                    callback(body, error);
                }
            });
        },

        scopes: function(instance, frameId, callback) {
            var args = { frameId: frameId };

            var self = this;
            this.sendRequest(instance, 'scopes', args, function(body, error) {
                if (body && body.scopes) {
                    ZatoDebuggerCore.setScopes(instance, body.scopes);

                    for (var i = 0; i < body.scopes.length; i++) {
                        var scope = body.scopes[i];
                        self.variables(instance, scope.variablesReference);
                    }
                }
                if (callback) {
                    callback(body, error);
                }
            });
        },

        variables: function(instance, variablesReference, callback) {
            var args = { variablesReference: variablesReference };

            this.sendRequest(instance, 'variables', args, function(body, error) {
                if (body && body.variables) {
                    ZatoDebuggerCore.setVariables(instance, variablesReference, body.variables);
                }
                if (callback) {
                    callback(body, error);
                }
            });
        },

        evaluate: function(instance, expression, frameId, callback) {
            var args = {
                expression: expression,
                frameId: frameId,
                context: 'repl'
            };

            this.sendRequest(instance, 'evaluate', args, function(body, error) {
                if (callback) {
                    if (error) {
                        callback({ result: error, type: 'error' });
                    } else {
                        callback(body);
                    }
                }
            });
        },

        threads: function(instance, callback) {
            this.sendRequest(instance, 'threads', {}, callback);
        },

        isConnected: function(instance) {
            var eventSource = this.connections[instance.id];
            return eventSource && eventSource.readyState === EventSource.OPEN;
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
        }
    };

    window.ZatoDebuggerProtocol = ZatoDebuggerProtocol;

})();
