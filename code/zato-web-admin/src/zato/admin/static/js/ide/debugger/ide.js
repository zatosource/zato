(function() {
    'use strict';

    /**
     * ZatoDebuggerIDE - connects the debugger to the IDE.
     *
     * Handles:
     * - Debugger panel visibility
     * - Editor gutter setup for breakpoints
     * - Coordinating debugger state with IDE state
     */
    var ZatoDebuggerIDE = {

        instances: {},

        create: function(ideInstance, options) {
            console.log('[DebuggerIDE] create: START ideInstance.id=' + ideInstance.id);
            var opts = options || {};
            console.log('[DebuggerIDE] create: opts=' + JSON.stringify(opts));

            var instance = {
                id: ideInstance.id + '-debugger',
                ide: ideInstance,
                debugger: null,
                debuggerUI: null,
                gutterHandler: null,
                panelVisible: false,
                panelContainer: null
            };
            console.log('[DebuggerIDE] create: instance.id=' + instance.id);

            this.instances[instance.id] = instance;
            console.log('[DebuggerIDE] create: calling initDebugger');
            this.initDebugger(instance);
            console.log('[DebuggerIDE] create: initDebugger complete');

            console.log('[DebuggerIDE] create: END returning instance');
            return instance;
        },

        getInstance: function(instanceId) {
            return this.instances[instanceId] || null;
        },

        getInstanceForIDE: function(ideInstance) {
            return this.instances[ideInstance.id + '-debugger'] || null;
        },

        destroy: function(instanceId) {
            var instance = this.instances[instanceId];
            if (instance) {
                if (instance.debugger) {
                    ZatoDebuggerCore.destroy(instance.debugger.id);
                }
                if (instance.debuggerUI) {
                    ZatoDebuggerUI.destroy(instance.debuggerUI.id);
                }
                if (instance.gutterHandler) {
                    ZatoDebuggerGutter.destroy(instance.gutterHandler.id);
                }
                delete this.instances[instanceId];
            }
        },

        initDebugger: function(instance) {
            console.log('[DebuggerIDE] initDebugger: START');
            var containerId = instance.id + '-core';
            console.log('[DebuggerIDE] initDebugger: containerId=' + containerId);
            console.log('[DebuggerIDE] initDebugger: typeof ZatoDebuggerCore=' + (typeof ZatoDebuggerCore));

            if (typeof ZatoDebuggerCore === 'undefined') {
                console.log('[DebuggerIDE] initDebugger: ZatoDebuggerCore is undefined, cannot create debugger');
                return;
            }

            instance.debugger = ZatoDebuggerCore.create(containerId, {
                theme: instance.ide.options.theme
            });
            console.log('[DebuggerIDE] initDebugger: debugger created=' + (instance.debugger ? 'ok' : 'null'));

            if (instance.gutterHandler && instance.debugger) {
                ZatoDebuggerGutter.attachDebugger(instance.gutterHandler, instance.debugger);
                console.log('[DebuggerIDE] initDebugger: attached debugger to gutter');
            }

            console.log('[DebuggerIDE] initDebugger: END');
        },

        stopDebugging: function(instance) {
            if (instance.debugger) {
                ZatoDebuggerCore.stopSession(instance.debugger);
            }
        },

        showDebugPanelInContainer: function(instance, containerId) {
            console.log('[DebuggerIDE] showDebugPanelInContainer: START containerId=' + containerId);

            var container = document.getElementById(containerId);
            if (!container) {
                console.log('[DebuggerIDE] showDebugPanelInContainer: container not found');
                return;
            }

            instance.panelContainer = container;
            instance.panelVisible = true;

            if (typeof ZatoDebuggerUI === 'undefined') {
                console.log('[DebuggerIDE] showDebugPanelInContainer: ZatoDebuggerUI is undefined');
                return;
            }

            if (instance.debuggerUI) {
                console.log('[DebuggerIDE] showDebugPanelInContainer: reusing existing debuggerUI');
                ZatoDebuggerUI.reattach(instance.debuggerUI, containerId);
            } else {
                console.log('[DebuggerIDE] showDebugPanelInContainer: creating new debuggerUI');
                instance.debuggerUI = ZatoDebuggerUI.create(containerId, instance.debugger, {
                    theme: instance.ide.options.theme,
                    ide: instance.ide
                });

                var ide = instance.ide;
                if (instance.debuggerUI) {
                    instance.debuggerUI.onJumpToLine = function(file, line) {
                        console.log('[DebuggerIDE] onJumpToLine: file=' + file + ' line=' + line);
                        if (ide.activeFile === file || file.endsWith(ide.activeFile)) {
                            ZatoIDEDropdowns.jumpToLine(ide, line);
                        }
                    };

                    instance.debuggerUI.onHighlightLine = function(file, line) {
                        console.log('[DebuggerIDE] onHighlightLine: file=' + file + ' line=' + line);
                        if (ide.activeFile === file || file.endsWith(ide.activeFile)) {
                            ZatoIDEDropdowns.jumpToLine(ide, line);
                        }
                    };
                }
            }

            this.setupGutter(instance);
            console.log('[DebuggerIDE] showDebugPanelInContainer: END');
        },

        showDebugPanel: function(instance) {
            console.log('[DebuggerIDE] showDebugPanel: START');
            console.log('[DebuggerIDE] showDebugPanel: redirecting to sidePanel1');

            var ide = instance.ide;
            if (ide && typeof ZatoIDE !== 'undefined') {
                ZatoIDEPanels.switchSidePanel1View(ide, 'debugger');
            }

            console.log('[DebuggerIDE] showDebugPanel: END');
        },

        hideDebugPanel: function(instance) {
            if (!instance.panelVisible) {
                return;
            }

            if (instance.debuggerUI) {
                ZatoDebuggerUI.destroy(instance.debuggerUI.id);
                instance.debuggerUI = null;
            }

            instance.panelContainer = null;
            instance.panelVisible = false;
        },

        toggleDebugPanel: function(instance) {
            if (instance.panelVisible) {
                this.hideDebugPanel(instance);
            } else {
                this.showDebugPanel(instance);
            }
        },

        adjustEditorLayout: function(instance) {
            var ide = instance.ide;
            if (ide.codeEditor && ide.codeEditor.aceEditor) {
                ide.codeEditor.aceEditor.resize();
            }
        },

        setupGutter: function(instance) {
            if (instance.gutterHandler) {
                return;
            }

            var ide = instance.ide;
            if (!ide.codeEditor || !ide.codeEditor.aceEditor) {
                return;
            }

            var existingGutter = ZatoDebuggerGutter.getInstanceForEditor(ide.codeEditor.aceEditor);
            if (existingGutter) {
                console.log('[DebuggerIDE] setupGutter: found existing gutter instance=' + existingGutter.id);
                instance.gutterHandler = existingGutter;
                return;
            }

            var self = this;
            instance.gutterHandler = ZatoDebuggerGutter.create(
                ide.codeEditor.aceEditor,
                instance.debugger,
                {
                    getFilename: function() {
                        return ide.activeFile;
                    },
                    getFilePath: function() {
                        var file = ide.files[ide.activeFile];
                        return file ? file.filePath : ide.activeFile;
                    }
                }
            );
        },

        updateBreakpoints: function(instance) {
            if (instance.gutterHandler) {
                ZatoDebuggerGutter.updateBreakpointMarkers(instance.gutterHandler);
            }
            if (instance.debuggerUI) {
                ZatoDebuggerUI.updateBreakpoints(instance.debuggerUI);
            }
        },

        handleFileSwitch: function(instance, filename) {
            if (instance.gutterHandler) {
                ZatoDebuggerGutter.updateBreakpointMarkers(instance.gutterHandler);
                ZatoDebuggerGutter.updateCurrentLineMarker(instance.gutterHandler);
            }
        },

        isDebugging: function(instance) {
            return instance.debugger && ZatoDebuggerCore.isDebugging(instance.debugger);
        },

        isPaused: function(instance) {
            return instance.debugger && ZatoDebuggerCore.isPaused(instance.debugger);
        }
    };

    window.ZatoDebuggerIDE = ZatoDebuggerIDE;

})();
