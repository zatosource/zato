(function() {
    'use strict';

    /**
     * ZatoDebuggerCore - core debugger state and session management.
     *
     * Manages:
     * - Debug session lifecycle (start, stop, pause, resume)
     * - Breakpoint storage and management
     * - Call stack state
     * - Variable scopes
     * - Debug adapter protocol communication coordination
     */
    var ZatoDebuggerCore = {

        instances: {},

        defaultOptions: {
            theme: 'dark',
            pythonPath: 'python3',
            debuggerPort: 5678,
            stopOnEntry: true
        },

        DebugState: {
            IDLE: 'idle',
            STARTING: 'starting',
            RUNNING: 'running',
            PAUSED: 'paused',
            STOPPED: 'stopped'
        },

        BreakpointState: {
            PENDING: 'pending',
            VERIFIED: 'verified',
            INVALID: 'invalid'
        },

        create: function(containerId, options) {
            var opts = {};
            var key;
            for (key in this.defaultOptions) {
                opts[key] = this.defaultOptions[key];
            }
            for (key in options) {
                opts[key] = options[key];
            }

            var instance = {
                id: containerId,
                options: opts,
                state: this.DebugState.IDLE,
                session: null,
                breakpoints: this.loadBreakpointsFromStorage(),
                callStack: [],
                scopes: [],
                variables: {},
                watches: [],
                currentFrame: null,
                currentLine: null,
                currentFile: null,
                listeners: {
                    onStateChange: [],
                    onBreakpointHit: [],
                    onCallStackUpdate: [],
                    onVariablesUpdate: [],
                    onOutput: [],
                    onError: []
                }
            };

            this.instances[containerId] = instance;
            return instance;
        },

        getInstance: function(containerId) {
            return this.instances[containerId] || null;
        },

        destroy: function(containerId) {
            var instance = this.instances[containerId];
            if (instance) {
                if (instance.session) {
                    this.stopSession(instance);
                }
                delete this.instances[containerId];
            }
        },

        loadBreakpointsFromStorage: function() {
            try {
                var stored = localStorage.getItem('zato-ide-breakpoints');
                if (stored) {
                    var data = JSON.parse(stored);
                    var breakpoints = {};
                    for (var file in data) {
                        for (var line in data[file]) {
                            var bp = data[file][line];
                            bp.file = file;
                            var key = file + ':' + bp.line;
                            breakpoints[key] = bp;
                        }
                    }
                    return breakpoints;
                }
            } catch (e) {
                console.error('[DebuggerCore] Failed to load breakpoints from storage:', e);
            }
            return {};
        },

        saveBreakpointsToStorage: function(instance) {
            try {
                var data = {};
                for (var key in instance.breakpoints) {
                    var bp = instance.breakpoints[key];
                    var file = bp.file || 'untitled.py';
                    if (!data[file]) {
                        data[file] = {};
                    }
                    data[file][bp.line] = bp;
                }
                localStorage.setItem('zato-ide-breakpoints', JSON.stringify(data));
            } catch (e) {
                console.error('[DebuggerCore] Failed to save breakpoints to storage:', e);
            }
        },

        on: function(instance, event, callback) {
            if (instance.listeners[event]) {
                instance.listeners[event].push(callback);
            }
        },

        off: function(instance, event, callback) {
            if (instance.listeners[event]) {
                var idx = instance.listeners[event].indexOf(callback);
                if (idx !== -1) {
                    instance.listeners[event].splice(idx, 1);
                }
            }
        },

        emit: function(instance, event, data) {
            if (instance.listeners[event]) {
                for (var i = 0; i < instance.listeners[event].length; i++) {
                    instance.listeners[event][i](data);
                }
            }
        },

        setState: function(instance, newState) {
            var oldState = instance.state;
            instance.state = newState;
            this.emit(instance, 'onStateChange', {
                oldState: oldState,
                newState: newState
            });
        },

        startSession: function(instance, fileContent, filename) {
            var self = this;

            if (instance.state !== this.DebugState.IDLE && instance.state !== this.DebugState.STOPPED) {
                console.warn('[Debugger] Cannot start session in state:', instance.state);
                return false;
            }

            this.setState(instance, this.DebugState.STARTING);

            instance.session = {
                id: 'debug-' + Date.now(),
                filename: filename,
                fileContent: fileContent,
                startTime: Date.now(),
                threadId: 1
            };

            instance.callStack = [];
            instance.scopes = [];
            instance.variables = {};
            instance.currentFrame = null;
            instance.currentLine = null;
            instance.currentFile = filename;

            if (typeof ZatoDebuggerProtocol !== 'undefined') {
                ZatoDebuggerProtocol.launch(instance, {
                    program: filename,
                    stopOnEntry: instance.options.stopOnEntry,
                    pythonPath: instance.options.pythonPath
                }, function(success, error) {
                    if (success) {
                        self.setState(instance, self.DebugState.RUNNING);
                    } else {
                        self.emit(instance, 'onError', { message: error });
                        self.setState(instance, self.DebugState.STOPPED);
                    }
                });
            } else {
                this.setState(instance, this.DebugState.RUNNING);
            }

            return true;
        },

        stopSession: function(instance) {
            if (instance.state === this.DebugState.IDLE) {
                return;
            }

            if (typeof ZatoDebuggerProtocol !== 'undefined') {
                ZatoDebuggerProtocol.disconnect(instance);
            }

            instance.session = null;
            instance.callStack = [];
            instance.scopes = [];
            instance.variables = {};
            instance.currentFrame = null;
            instance.currentLine = null;

            this.setState(instance, this.DebugState.STOPPED);
        },

        pause: function(instance) {
            if (instance.state !== this.DebugState.RUNNING) {
                return false;
            }

            var threadId = instance.session ? instance.session.threadId : 1;
            if (typeof ZatoDebuggerProtocol !== 'undefined') {
                ZatoDebuggerProtocol.pause(instance, threadId);
            }

            this.setState(instance, this.DebugState.PAUSED);
            return true;
        },

        resume: function(instance) {
            if (instance.state !== this.DebugState.PAUSED) {
                return false;
            }

            var threadId = instance.session ? instance.session.threadId : 1;
            if (typeof ZatoDebuggerProtocol !== 'undefined') {
                ZatoDebuggerProtocol.continue_(instance, threadId);
            }

            this.setState(instance, this.DebugState.RUNNING);
            return true;
        },

        stepOver: function(instance) {
            if (instance.state !== this.DebugState.PAUSED) {
                return false;
            }

            var threadId = instance.session ? instance.session.threadId : 1;
            if (typeof ZatoDebuggerProtocol !== 'undefined') {
                ZatoDebuggerProtocol.next(instance, threadId);
            }

            return true;
        },

        stepInto: function(instance) {
            if (instance.state !== this.DebugState.PAUSED) {
                return false;
            }

            var threadId = instance.session ? instance.session.threadId : 1;
            if (typeof ZatoDebuggerProtocol !== 'undefined') {
                ZatoDebuggerProtocol.stepIn(instance, threadId);
            }

            return true;
        },

        stepOut: function(instance) {
            if (instance.state !== this.DebugState.PAUSED) {
                return false;
            }

            var threadId = instance.session ? instance.session.threadId : 1;
            if (typeof ZatoDebuggerProtocol !== 'undefined') {
                ZatoDebuggerProtocol.stepOut(instance, threadId);
            }

            return true;
        },

        restart: function(instance) {
            var filename = instance.session ? instance.session.filename : null;
            var content = instance.session ? instance.session.fileContent : null;

            this.stopSession(instance);

            if (filename && content) {
                this.startSession(instance, content, filename);
            }
        },

        addBreakpoint: function(instance, file, line, condition) {
            var key = file + ':' + line;

            if (instance.breakpoints[key]) {
                return instance.breakpoints[key];
            }

            var breakpoint = {
                id: 'bp-' + Date.now() + '-' + Math.random().toString(36).substr(2, 6),
                file: file,
                line: line,
                condition: condition || null,
                hitCount: 0,
                enabled: true,
                state: this.BreakpointState.PENDING
            };

            instance.breakpoints[key] = breakpoint;
            this.saveBreakpointsToStorage(instance);

            if (instance.state !== this.DebugState.IDLE && typeof ZatoDebuggerProtocol !== 'undefined') {
                ZatoDebuggerProtocol.setBreakpoints(instance, file, this.getBreakpointsForFile(instance, file));
            }

            return breakpoint;
        },

        removeBreakpoint: function(instance, file, line) {
            var key = file + ':' + line;
            var breakpoint = instance.breakpoints[key];

            if (!breakpoint) {
                return false;
            }

            delete instance.breakpoints[key];
            this.saveBreakpointsToStorage(instance);

            if (instance.state !== this.DebugState.IDLE && typeof ZatoDebuggerProtocol !== 'undefined') {
                ZatoDebuggerProtocol.setBreakpoints(instance, file, this.getBreakpointsForFile(instance, file));
            }

            return true;
        },

        toggleBreakpoint: function(instance, file, line) {
            var key = file + ':' + line;
            var breakpoint = instance.breakpoints[key];

            if (breakpoint) {
                this.removeBreakpoint(instance, file, line);
                return null;
            } else {
                return this.addBreakpoint(instance, file, line);
            }
        },

        enableBreakpoint: function(instance, file, line, enabled) {
            var key = file + ':' + line;
            var breakpoint = instance.breakpoints[key];

            if (!breakpoint) {
                return false;
            }

            breakpoint.enabled = enabled;
            this.saveBreakpointsToStorage(instance);

            if (instance.state !== this.DebugState.IDLE && typeof ZatoDebuggerProtocol !== 'undefined') {
                ZatoDebuggerProtocol.setBreakpoints(instance, file, this.getBreakpointsForFile(instance, file));
            }

            return true;
        },

        getBreakpoint: function(instance, file, line) {
            var key = file + ':' + line;
            return instance.breakpoints[key] || null;
        },

        getBreakpointsForFile: function(instance, file) {
            var breakpoints = [];
            for (var key in instance.breakpoints) {
                var bp = instance.breakpoints[key];
                if (bp.file === file && bp.enabled) {
                    breakpoints.push(bp);
                }
            }
            return breakpoints;
        },

        getAllBreakpoints: function(instance) {
            var breakpoints = [];
            for (var key in instance.breakpoints) {
                breakpoints.push(instance.breakpoints[key]);
            }
            return breakpoints;
        },

        clearAllBreakpoints: function(instance) {
            instance.breakpoints = {};

            if (instance.state !== this.DebugState.IDLE && typeof ZatoDebuggerProtocol !== 'undefined') {
                ZatoDebuggerProtocol.clearAllBreakpoints(instance);
            }
        },

        setCallStack: function(instance, frames) {
            instance.callStack = frames;
            if (frames.length > 0) {
                instance.currentFrame = frames[0];
                instance.currentLine = frames[0].line;
                instance.currentFile = frames[0].source ? frames[0].source.path : null;
            }
            this.emit(instance, 'onCallStackUpdate', { frames: frames });
        },

        selectFrame: function(instance, frameId) {
            for (var i = 0; i < instance.callStack.length; i++) {
                if (instance.callStack[i].id === frameId) {
                    instance.currentFrame = instance.callStack[i];
                    instance.currentLine = instance.callStack[i].line;
                    instance.currentFile = instance.callStack[i].source ? instance.callStack[i].source.path : null;

                    if (typeof ZatoDebuggerProtocol !== 'undefined') {
                        ZatoDebuggerProtocol.scopes(instance, frameId);
                    }

                    return true;
                }
            }
            return false;
        },

        setScopes: function(instance, scopes) {
            instance.scopes = scopes;
        },

        setVariables: function(instance, scopeRef, variables) {
            instance.variables[scopeRef] = variables;
            this.emit(instance, 'onVariablesUpdate', {
                scopeRef: scopeRef,
                variables: variables
            });
        },

        addWatch: function(instance, expression) {
            var watch = {
                id: 'watch-' + Date.now(),
                expression: expression,
                value: null,
                type: null
            };
            instance.watches.push(watch);
            this.evaluateWatch(instance, watch);
            return watch;
        },

        removeWatch: function(instance, watchId) {
            for (var i = 0; i < instance.watches.length; i++) {
                if (instance.watches[i].id === watchId) {
                    instance.watches.splice(i, 1);
                    return true;
                }
            }
            return false;
        },

        evaluateWatch: function(instance, watch) {
            if (instance.state !== this.DebugState.PAUSED || !instance.currentFrame) {
                watch.value = '<not available>';
                watch.type = null;
                return;
            }

            if (typeof ZatoDebuggerProtocol !== 'undefined') {
                ZatoDebuggerProtocol.evaluate(instance, watch.expression, instance.currentFrame.id, function(result) {
                    watch.value = result.result;
                    watch.type = result.type;
                });
            }
        },

        evaluateAllWatches: function(instance) {
            for (var i = 0; i < instance.watches.length; i++) {
                this.evaluateWatch(instance, instance.watches[i]);
            }
        },

        handleBreakpointHit: function(instance, threadId, reason) {
            this.setState(instance, this.DebugState.PAUSED);

            if (typeof ZatoDebuggerProtocol !== 'undefined') {
                ZatoDebuggerProtocol.stackTrace(instance, threadId);
            }

            this.emit(instance, 'onBreakpointHit', {
                threadId: threadId,
                reason: reason
            });
        },

        handleOutput: function(instance, category, output) {
            this.emit(instance, 'onOutput', {
                category: category,
                output: output,
                timestamp: Date.now()
            });
        },

        handleTerminated: function(instance) {
            if (instance.state === this.DebugState.IDLE) {
                return;
            }
            this.setState(instance, this.DebugState.STOPPED);
        },

        getState: function(instance) {
            return instance.state;
        },

        isDebugging: function(instance) {
            return instance.state !== this.DebugState.IDLE && instance.state !== this.DebugState.STOPPED;
        },

        isPaused: function(instance) {
            return instance.state === this.DebugState.PAUSED;
        }
    };

    window.ZatoDebuggerCore = ZatoDebuggerCore;

})();
