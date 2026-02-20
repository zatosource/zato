(function() {
    'use strict';

    /**
     * ZatoDebuggerIDE - connects the debugger to the IDE.
     *
     * Handles:
     * - Debug current file action from toolbar
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
                if (instance.panelContainer) {
                    instance.panelContainer.remove();
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

        debugCurrentFile: function(instance) {
            console.log('[DebuggerIDE] debugCurrentFile: START');
            console.log('[DebuggerIDE] debugCurrentFile: instance.id=' + instance.id);
            console.log('[DebuggerIDE] debugCurrentFile: instance.ide=' + (instance.ide ? 'ok' : 'null'));
            console.log('[DebuggerIDE] debugCurrentFile: instance.debugger=' + (instance.debugger ? 'ok' : 'null'));

            var ide = instance.ide;
            console.log('[DebuggerIDE] debugCurrentFile: ide.activeFile=' + ide.activeFile);
            console.log('[DebuggerIDE] debugCurrentFile: ide.files keys=' + Object.keys(ide.files || {}).join(', '));

            if (!ide.activeFile || !ide.files[ide.activeFile]) {
                console.warn('[DebuggerIDE] debugCurrentFile: No active file to debug');
                return false;
            }

            var file = ide.files[ide.activeFile];
            var filename = ide.activeFile;
            var content = file.content;
            console.log('[DebuggerIDE] debugCurrentFile: filename=' + filename);
            console.log('[DebuggerIDE] debugCurrentFile: file.language=' + file.language);
            console.log('[DebuggerIDE] debugCurrentFile: content.length=' + (content ? content.length : 0));

            if (file.language !== 'python') {
                console.warn('[DebuggerIDE] debugCurrentFile: Only Python files can be debugged, got language=' + file.language);
                return false;
            }

            console.log('[DebuggerIDE] debugCurrentFile: calling showDebugPanel');
            this.showDebugPanel(instance);
            console.log('[DebuggerIDE] debugCurrentFile: showDebugPanel complete');

            console.log('[DebuggerIDE] debugCurrentFile: calling setupGutter');
            this.setupGutter(instance);
            console.log('[DebuggerIDE] debugCurrentFile: setupGutter complete');

            console.log('[DebuggerIDE] debugCurrentFile: calling ZatoDebuggerCore.startSession');
            ZatoDebuggerCore.startSession(instance.debugger, content, filename);
            console.log('[DebuggerIDE] debugCurrentFile: startSession complete');

            console.log('[DebuggerIDE] debugCurrentFile: END returning true');
            return true;
        },

        stopDebugging: function(instance) {
            if (instance.debugger) {
                ZatoDebuggerCore.stopSession(instance.debugger);
            }
        },

        showDebugPanel: function(instance) {
            console.log('[DebuggerIDE] showDebugPanel: START');
            console.log('[DebuggerIDE] showDebugPanel: instance.panelVisible=' + instance.panelVisible);

            if (instance.panelVisible) {
                console.log('[DebuggerIDE] showDebugPanel: panel already visible, returning');
                return;
            }

            var ide = instance.ide;
            console.log('[DebuggerIDE] showDebugPanel: ide.id=' + ide.id);

            var editorAreaId = ide.id + '-editor-area';
            console.log('[DebuggerIDE] showDebugPanel: looking for editorArea id=' + editorAreaId);
            var editorArea = document.getElementById(editorAreaId);
            console.log('[DebuggerIDE] showDebugPanel: editorArea=' + (editorArea ? 'found' : 'not found'));

            if (!editorArea) {
                console.log('[DebuggerIDE] showDebugPanel: editorArea not found, returning');
                return;
            }

            var wrapper = editorArea.parentElement;
            console.log('[DebuggerIDE] showDebugPanel: wrapper=' + (wrapper ? wrapper.className : 'null'));

            var panelContainer = document.createElement('div');
            panelContainer.id = instance.id + '-panel';
            panelContainer.className = 'zato-debugger-panel-container';
            console.log('[DebuggerIDE] showDebugPanel: created panelContainer id=' + panelContainer.id);

            wrapper.appendChild(panelContainer);
            console.log('[DebuggerIDE] showDebugPanel: appended panelContainer to wrapper');

            instance.panelContainer = panelContainer;
            instance.panelVisible = true;

            console.log('[DebuggerIDE] showDebugPanel: typeof ZatoDebuggerUI=' + (typeof ZatoDebuggerUI));
            if (typeof ZatoDebuggerUI === 'undefined') {
                console.log('[DebuggerIDE] showDebugPanel: ZatoDebuggerUI is undefined, cannot create UI');
                return;
            }

            console.log('[DebuggerIDE] showDebugPanel: calling ZatoDebuggerUI.create');
            instance.debuggerUI = ZatoDebuggerUI.create(panelContainer.id, instance.debugger, {
                theme: ide.options.theme
            });
            console.log('[DebuggerIDE] showDebugPanel: debuggerUI created=' + (instance.debuggerUI ? 'ok' : 'null'));

            instance.debuggerUI.onJumpToLine = function(file, line) {
                console.log('[DebuggerIDE] onJumpToLine: file=' + file + ' line=' + line);
                if (ide.activeFile === file || file.endsWith(ide.activeFile)) {
                    ZatoIDE.jumpToLine(ide, line);
                }
            };

            instance.debuggerUI.onHighlightLine = function(file, line) {
                console.log('[DebuggerIDE] onHighlightLine: file=' + file + ' line=' + line);
                if (ide.activeFile === file || file.endsWith(ide.activeFile)) {
                    ZatoIDE.jumpToLine(ide, line);
                }
            };

            console.log('[DebuggerIDE] showDebugPanel: calling adjustEditorLayout');
            this.adjustEditorLayout(instance);
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

            if (instance.panelContainer) {
                instance.panelContainer.remove();
                instance.panelContainer = null;
            }

            instance.panelVisible = false;
            this.adjustEditorLayout(instance);
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

            var self = this;
            instance.gutterHandler = ZatoDebuggerGutter.create(
                ide.codeEditor.aceEditor,
                instance.debugger,
                {
                    getFilename: function() {
                        return ide.activeFile;
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
