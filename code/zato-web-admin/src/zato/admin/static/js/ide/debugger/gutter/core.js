(function() {
    'use strict';

    var ZatoDebuggerGutter = {

        instances: {},

        markerIds: {},

        create: function(aceEditor, debuggerInstance, options) {
            console.log('[Gutter] create: START');
            console.log('[Gutter] create: aceEditor=' + (aceEditor ? 'exists' : 'null'));
            console.log('[Gutter] create: aceEditor.container.id=' + (aceEditor && aceEditor.container ? aceEditor.container.id : 'N/A'));
            console.log('[Gutter] create: debuggerInstance=' + (debuggerInstance ? 'exists' : 'null'));
            console.log('[Gutter] create: options=' + JSON.stringify(options));
            console.log('[Gutter] create: existing instances=' + JSON.stringify(Object.keys(this.instances)));
            console.log('[Gutter] create: stack trace=', new Error().stack);

            var instanceId = 'gutter-' + Date.now();

            var loadedBreakpoints = this.loadBreakpointsFromStorage();
            console.log('[Gutter] create: loadedBreakpoints=' + JSON.stringify(loadedBreakpoints));

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
            console.log('[Gutter] create: calling updateBreakpointMarkers');
            this.updateBreakpointMarkers(instance);

            var self = this;
            var renderCount = 0;
            aceEditor.renderer.on('afterRender', function onRender() {
                renderCount++;
                console.log('[Gutter] afterRender #' + renderCount + ': fired');
                var gutterCells = aceEditor.renderer.$gutterLayer.element.querySelectorAll('.ace_gutter-cell');
                console.log('[Gutter] afterRender #' + renderCount + ': gutterCells.length=' + gutterCells.length);

                var gutterElement = aceEditor.renderer.$gutterLayer.element;
                var gutterRect = gutterElement.getBoundingClientRect();
                console.log('[Gutter] afterRender #' + renderCount + ': gutter left=' + gutterRect.left + ' width=' + gutterRect.width);

                for (var i = 0; i < gutterCells.length; i++) {
                    if (gutterCells[i].classList.contains('ace_breakpoint')) {
                        var style = window.getComputedStyle(gutterCells[i]);
                        var cellRect = gutterCells[i].getBoundingClientRect();
                        console.log('[Gutter] afterRender #' + renderCount + ': cell[' + i + '] has breakpoint, bg-pos=' + style.backgroundPosition + ' cellLeft=' + cellRect.left + ' cellWidth=' + cellRect.width);
                    }
                }

                if (gutterCells.length > 1 && renderCount === 1) {
                    console.log('[Gutter] afterRender: first render with cells, calling updateBreakpointMarkers');
                    self.updateBreakpointMarkers(instance);
                    self.setupMutationObserver(instance);
                }
            });

            console.log('[Gutter] create: END, instanceId=' + instanceId);
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
            console.log('[Gutter] bindEvents: START instance.id=' + instance.id);
            var self = this;
            var editor = instance.editor;
            var gutter = editor.renderer.$gutter;
            console.log('[Gutter] bindEvents: gutter element=' + (gutter ? 'exists' : 'null'));
            console.log('[Gutter] bindEvents: gutter.id=' + (gutter ? gutter.id : 'N/A'));
            console.log('[Gutter] bindEvents: gutter existing listeners=' + (gutter._zatoGutterBound ? 'YES ALREADY BOUND' : 'no'));

            if (gutter._zatoGutterBound) {
                console.log('[Gutter] bindEvents: SKIPPING - already bound');
                return;
            }
            gutter._zatoGutterBound = true;

            gutter.addEventListener('mousedown', function(e) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
            }, true);

            gutter.addEventListener('click', function(e) {
                console.log('[Gutter] click event fired, instance.id=' + instance.id);
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
