(function() {
    'use strict';

    var ZatoDebuggerGutter = {

        instances: {},

        markerIds: {},

        create: function(aceEditor, debuggerInstance, options) {
            var instanceId = 'gutter-' + Date.now();
            var loadedBreakpoints = this.loadBreakpointsFromStorage();

            var instance = {
                id: instanceId,
                editor: aceEditor,
                debugger: debuggerInstance,
                options: options || {},
                currentLineMarkerId: null,
                breakpointDecorations: {},
                localBreakpoints: loadedBreakpoints
            };

            this.instances[instanceId] = instance;
            this.bindEvents(instance);
            this.updateBreakpointMarkers(instance);

            var self = this;
            var renderCount = 0;
            aceEditor.renderer.on('afterRender', function onRender() {
                renderCount++;
                var gutterCells = aceEditor.renderer.$gutterLayer.element.querySelectorAll('.ace_gutter-cell');

                if (gutterCells.length > 1 && renderCount === 1) {
                    self.updateBreakpointMarkers(instance);
                    self.setupMutationObserver(instance);
                }
            });
            return instance;
        },

        getInstance: function(instanceId) {
            return this.instances[instanceId] || null;
        },

        getInstanceForEditor: function(aceEditor) {
            for (var id in this.instances) {
                if (this.instances[id].editor === aceEditor) {
                    return this.instances[id];
                }
            }
            return null;
        },

        destroy: function(instanceId) {
            var instance = this.instances[instanceId];
            if (instance) {
                this.clearAllMarkers(instance);
                delete this.instances[instanceId];
            }
        },

        bindEvents: function(instance) {
            var self = this;
            var editor = instance.editor;
            var gutter = editor.renderer.$gutter;

            if (gutter._zatoGutterBound) {
                return;
            }
            gutter._zatoGutterBound = true;

            gutter.addEventListener('mousedown', function(e) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
            }, true);

            gutter.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                self.handleGutterClick(instance, e);
            }, true);

            gutter.addEventListener('contextmenu', function(e) {
                self.handleGutterContextMenu(instance, e);
            });

            if (instance.debugger) {
                this.bindDebuggerEvents(instance);
            }
        },

        attachDebugger: function(instance, debuggerInstance) {
            instance.debugger = debuggerInstance;
            var localBreakpoints = instance.localBreakpoints || this.loadBreakpointsFromStorage();
            for (var file in localBreakpoints) {
                for (var line in localBreakpoints[file]) {
                    var bp = localBreakpoints[file][line];
                    ZatoDebuggerCore.addBreakpoint(debuggerInstance, file, bp.line, bp.condition || null);
                    if (!bp.enabled) {
                        ZatoDebuggerCore.enableBreakpoint(debuggerInstance, file, bp.line, false);
                    }
                }
            }
            this.bindDebuggerEvents(instance);
        },

        bindDebuggerEvents: function(instance) {
            if (!instance.debugger || instance._debuggerEventsBound) {
                return;
            }
            instance._debuggerEventsBound = true;

            var self = this;
            ZatoDebuggerCore.on(instance.debugger, 'onStateChange', function(data) {
                self.updateCurrentLineMarker(instance);
            });

            ZatoDebuggerCore.on(instance.debugger, 'onCallStackUpdate', function(data) {
                self.updateCurrentLineMarker(instance);
            });
        }
    };

    window.ZatoDebuggerGutter = ZatoDebuggerGutter;

})();
