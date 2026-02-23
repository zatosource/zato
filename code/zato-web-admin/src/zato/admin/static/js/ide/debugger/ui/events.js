(function() {
    'use strict';

    var UI = window.ZatoDebuggerUI;

    UI.bindEvents = function(instance) {
        var container = instance.container;

        container.addEventListener('click', function(e) {
            var copyBtn = e.target.closest('.zato-debugger-copy-btn');
            if (copyBtn) {
                e.stopPropagation();
                e.preventDefault();
                var copyType = copyBtn.getAttribute('data-copy');
                UI.copyPanelContent(instance, copyType);
                if (instance.tooltip && typeof ZatoTooltip !== 'undefined') {
                    ZatoTooltip.hideImmediate(instance.tooltip);
                    ZatoTooltip.showTemporary(instance.tooltip, copyBtn, 'Copied to clipboard', 350);
                }
                return;
            }

            var actionBtn = e.target.closest('.zato-debugger-panel-action');
            if (actionBtn) {
                e.stopPropagation();
                e.preventDefault();
                var action = actionBtn.getAttribute('data-action');
                UI.handleAction(instance, action, e);
                if (instance.tooltip && typeof ZatoTooltip !== 'undefined') {
                    ZatoTooltip.hideImmediate(instance.tooltip);
                }
                return;
            }

            var button = e.target.closest('[data-action]');
            if (button && !button.classList.contains('zato-debugger-panel-action')) {
                var action = button.getAttribute('data-action');
                UI.handleAction(instance, action, e);
                return;
            }

            var header = e.target.closest('.zato-debugger-panel-header[data-panel]');
            if (header) {
                if (e.target.closest('.zato-debugger-panel-action') || e.target.closest('.zato-debugger-copy-btn')) {
                    return;
                }
                var panel = header.getAttribute('data-panel');
                UI.togglePanel(instance, panel);
            }

            var frameItem = e.target.closest('.zato-debugger-frame-item');
            if (frameItem) {
                var frameId = parseInt(frameItem.getAttribute('data-frame-id'), 10);
                UI.selectFrame(instance, frameId);
            }

            var bpItem = e.target.closest('.zato-debugger-breakpoint-item');
            if (bpItem && !e.target.closest('.zato-debugger-breakpoint-checkbox')) {
                var file = bpItem.getAttribute('data-file');
                var line = parseInt(bpItem.getAttribute('data-line'), 10);
                UI.jumpToBreakpoint(instance, file, line);
            }

            var bpCheckbox = e.target.closest('.zato-debugger-breakpoint-checkbox');
            if (bpCheckbox) {
                var bpFile = bpCheckbox.closest('.zato-debugger-breakpoint-item').getAttribute('data-file');
                var bpLine = parseInt(bpCheckbox.closest('.zato-debugger-breakpoint-item').getAttribute('data-line'), 10);
                var enabled = bpCheckbox.checked;
                ZatoDebuggerCore.enableBreakpoint(instance.debugger, bpFile, bpLine, enabled);
            }

            var varItem = e.target.closest('.zato-debugger-variable-item');
            if (varItem && varItem.classList.contains('expandable')) {
                UI.toggleVariable(instance, varItem);
            }
        });

        var watchInput = instance.elements.watchInput;
        if (watchInput) {
            watchInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && watchInput.value.trim()) {
                    ZatoDebuggerCore.addWatch(instance.debugger, watchInput.value.trim());
                    watchInput.value = '';
                    UI.updateWatches(instance);
                    UI.saveWatches(instance);
                }
            });
        }

        var consoleInput = instance.elements.consoleInput;
        if (consoleInput) {
            var historyKey = 'zato.debugger.console-history';
            var history = [];
            var historyIndex = -1;
            try {
                var stored = localStorage.getItem(historyKey);
                if (stored) {
                    history = JSON.parse(stored);
                }
            } catch (err) {
                history = [];
            }

            consoleInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && consoleInput.value.trim()) {
                    var expr = consoleInput.value.trim();
                    UI.evaluateInConsole(instance, expr);
                    history.push(expr);
                    if (history.length > 100) {
                        history = history.slice(-100);
                    }
                    try {
                        localStorage.setItem(historyKey, JSON.stringify(history));
                    } catch (err) {}
                    historyIndex = history.length;
                    consoleInput.value = '';
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    if (history.length > 0 && historyIndex > 0) {
                        historyIndex--;
                        consoleInput.value = history[historyIndex];
                    }
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    if (historyIndex < history.length - 1) {
                        historyIndex++;
                        consoleInput.value = history[historyIndex];
                    } else {
                        historyIndex = history.length;
                        consoleInput.value = '';
                    }
                }
            });
        }

        if (instance.debugger) {
            ZatoDebuggerCore.on(instance.debugger, 'onStateChange', function(data) {
                UI.updateToolbarState(instance);
            });

            ZatoDebuggerCore.on(instance.debugger, 'onCallStackUpdate', function(data) {
                UI.updateCallStack(instance, data.frames);
            });

            ZatoDebuggerCore.on(instance.debugger, 'onVariablesUpdate', function(data) {
                UI.updateVariables(instance, data.scopeRef, data.variables);
            });

            ZatoDebuggerCore.on(instance.debugger, 'onOutput', function(data) {
                UI.appendConsoleOutput(instance, data.category, data.output);
            });

            ZatoDebuggerCore.on(instance.debugger, 'onBreakpointHit', function(data) {
                UI.highlightCurrentLine(instance);
            });
        }

        document.addEventListener('keydown', function(e) {
            if (!instance.debugger || !ZatoDebuggerCore.isDebugging(instance.debugger)) {
                return;
            }

            if (e.key === 'F5' && !e.shiftKey && !e.ctrlKey) {
                e.preventDefault();
                UI.handleAction(instance, 'continue');
            } else if (e.key === 'F6') {
                e.preventDefault();
                UI.handleAction(instance, 'pause');
            } else if (e.key === 'F10') {
                e.preventDefault();
                UI.handleAction(instance, 'step-over');
            } else if (e.key === 'F11' && !e.shiftKey) {
                e.preventDefault();
                UI.handleAction(instance, 'step-into');
            } else if (e.key === 'F11' && e.shiftKey) {
                e.preventDefault();
                UI.handleAction(instance, 'step-out');
            } else if (e.key === 'F5' && e.shiftKey && !e.ctrlKey) {
                e.preventDefault();
                UI.handleAction(instance, 'stop');
            } else if (e.key === 'F5' && e.ctrlKey && e.shiftKey) {
                e.preventDefault();
                UI.handleAction(instance, 'restart');
            }
        });
    };

    UI.handleAction = function(instance, action, event) {
        var dbg = instance.debugger;
        if (!dbg) {
            return;
        }

        switch (action) {
            case 'continue':
                ZatoDebuggerCore.resume(dbg);
                break;
            case 'pause':
                ZatoDebuggerCore.pause(dbg);
                break;
            case 'step-over':
                ZatoDebuggerCore.stepOver(dbg);
                break;
            case 'step-into':
                ZatoDebuggerCore.stepInto(dbg);
                break;
            case 'step-out':
                ZatoDebuggerCore.stepOut(dbg);
                break;
            case 'restart':
                ZatoDebuggerCore.restart(dbg);
                break;
            case 'stop':
                ZatoDebuggerCore.stopSession(dbg);
                break;
            case 'clear-breakpoints':
                ZatoDebuggerCore.clearAllBreakpoints(dbg);
                if (instance.elements.breakpointsList) {
                    instance.elements.breakpointsList.innerHTML = '';
                }
                break;
            case 'clear-console':
                if (instance.elements.consoleOutput) {
                    instance.elements.consoleOutput.innerHTML = '';
                }
                UI.saveState('console-output', []);
                break;
            case 'add-watch':
                if (instance.elements.watchInput) {
                    instance.elements.watchInput.focus();
                }
                break;
            case 'remove-watch':
                var watchId = event.target.closest('[data-watch-id]');
                if (watchId) {
                    var id = parseInt(watchId.getAttribute('data-watch-id'), 10);
                    ZatoDebuggerCore.removeWatch(dbg, id);
                    UI.updateWatches(instance);
                    UI.saveWatches(instance);
                }
                break;
        }
    };

    UI.togglePanel = function(instance, panelName) {
        instance.expanded[panelName] = !instance.expanded[panelName];
        var panel = instance.container.querySelector('.zato-debugger-' + panelName.toLowerCase());
        if (panel) {
            panel.classList.toggle('collapsed', !instance.expanded[panelName]);
        }
        UI.saveState('expanded', instance.expanded);
    };

    UI.copyPanelContent = function(instance, copyType) {
        var text = '';
        var dbg = instance.debugger;

        if (copyType === 'callstack' && dbg) {
            var frames = dbg.callStack || [];
            for (var i = 0; i < frames.length; i++) {
                var frame = frames[i];
                var name = frame.name || '<unknown>';
                var source = frame.source ? frame.source.path || frame.source.name || '' : '';
                var line = frame.line || 0;
                text += name + ' at ' + source + ':' + line + '\n';
            }
        } else if (copyType === 'variables' && dbg) {
            var vars = dbg.variables || {};
            for (var ref in vars) {
                var varList = vars[ref];
                if (Array.isArray(varList)) {
                    for (var j = 0; j < varList.length; j++) {
                        var v = varList[j];
                        text += v.name + ' = ' + v.value + '\n';
                    }
                }
            }
        } else if (copyType === 'error') {
            text = instance._errorMessage || '';
        }

        if (text) {
            navigator.clipboard.writeText(text).catch(function(err) {
                console.error('Failed to copy:', err);
            });
        }
    };

})();
