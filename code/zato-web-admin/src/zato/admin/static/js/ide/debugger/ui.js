(function() {
    'use strict';

    /**
     * ZatoDebuggerUI - debugger UI components.
     *
     * Renders:
     * - Debug toolbar (continue, pause, step over, step into, step out, restart, stop)
     * - Call stack panel
     * - Variables panel (locals, globals, watches)
     * - Breakpoints panel
     * - Debug console output
     */
    var ZatoDebuggerUI = {

        instances: {},

        defaultOptions: {
            theme: 'dark',
            showCallStack: true,
            showVariables: true,
            showBreakpoints: true,
            showConsole: true
        },

        create: function(containerId, debuggerInstance, options) {
            console.log('[DebuggerUI] create: START containerId=' + containerId);
            console.log('[DebuggerUI] create: debuggerInstance=' + (debuggerInstance ? 'ok' : 'null'));

            var opts = {};
            var key;
            for (key in this.defaultOptions) {
                opts[key] = this.defaultOptions[key];
            }
            for (key in options) {
                opts[key] = options[key];
            }
            console.log('[DebuggerUI] create: opts=' + JSON.stringify(opts));

            var container = document.getElementById(containerId);
            console.log('[DebuggerUI] create: container=' + (container ? 'found' : 'not found'));
            if (!container) {
                console.error('[DebuggerUI] create: Container not found:', containerId);
                return null;
            }

            var instance = {
                id: containerId,
                container: container,
                debugger: debuggerInstance,
                options: opts,
                elements: {},
                expanded: {
                    callStack: true,
                    variables: true,
                    breakpoints: true,
                    watches: true,
                    console: true
                }
            };
            console.log('[DebuggerUI] create: instance created');

            console.log('[DebuggerUI] create: calling render');
            this.render(instance);
            console.log('[DebuggerUI] create: render complete');

            this.initTooltip(instance);

            console.log('[DebuggerUI] create: calling bindEvents');
            this.bindEvents(instance);
            console.log('[DebuggerUI] create: bindEvents complete');

            this.instances[containerId] = instance;

            console.log('[DebuggerUI] create: END returning instance');
            return instance;
        },

        getInstance: function(containerId) {
            return this.instances[containerId] || null;
        },

        initTooltip: function(instance) {
            console.log('[DebuggerUI] initTooltip: START');
            console.log('[DebuggerUI] initTooltip: instance.id=' + instance.id);
            console.log('[DebuggerUI] initTooltip: ZatoTooltip defined=' + (typeof ZatoTooltip !== 'undefined'));
            if (typeof ZatoTooltip !== 'undefined') {
                console.log('[DebuggerUI] initTooltip: calling ZatoTooltip.create');
                instance.tooltip = ZatoTooltip.create(instance.id, {
                    theme: 'dark',
                    attribute: 'data-tooltip'
                });
                console.log('[DebuggerUI] initTooltip: tooltip created=' + (instance.tooltip ? 'yes' : 'no'));
                if (instance.tooltip) {
                    console.log('[DebuggerUI] initTooltip: tooltip.container=' + (instance.tooltip.container ? 'found' : 'null'));
                }
            }
            console.log('[DebuggerUI] initTooltip: END');
        },

        destroy: function(containerId) {
            var instance = this.instances[containerId];
            if (instance) {
                instance.container.innerHTML = '';
                delete this.instances[containerId];
            }
        },

        render: function(instance) {
            console.log('[DebuggerUI] render: START');
            console.log('[DebuggerUI] render: instance.container=' + (instance.container ? 'ok' : 'null'));
            console.log('[DebuggerUI] render: theme=' + instance.options.theme);

            var html = '';
            html += '<div class="zato-debugger-container zato-debugger-theme-' + instance.options.theme + '">';
            html += this.renderToolbar(instance);
            html += '<div class="zato-debugger-panels">';
            html += this.renderCallStackPanel(instance);
            html += this.renderVariablesPanel(instance);
            html += this.renderWatchesPanel(instance);
            html += this.renderBreakpointsPanel(instance);
            html += '</div>';
            html += this.renderConsolePanel(instance);
            html += '</div>';

            console.log('[DebuggerUI] render: html.length=' + html.length);
            instance.container.innerHTML = html;
            console.log('[DebuggerUI] render: innerHTML set');

            this.cacheElements(instance);
            console.log('[DebuggerUI] render: END');
        },

        cacheElements: function(instance) {
            var container = instance.container;
            instance.elements = {
                toolbar: container.querySelector('.zato-debugger-toolbar'),
                continueBtn: container.querySelector('[data-action="continue"]'),
                pauseBtn: container.querySelector('[data-action="pause"]'),
                stepOverBtn: container.querySelector('[data-action="step-over"]'),
                stepIntoBtn: container.querySelector('[data-action="step-into"]'),
                stepOutBtn: container.querySelector('[data-action="step-out"]'),
                restartBtn: container.querySelector('[data-action="restart"]'),
                stopBtn: container.querySelector('[data-action="stop"]'),
                callStackPanel: container.querySelector('.zato-debugger-callstack'),
                callStackList: container.querySelector('.zato-debugger-callstack-list'),
                variablesPanel: container.querySelector('.zato-debugger-variables'),
                variablesList: container.querySelector('.zato-debugger-variables-list'),
                watchesPanel: container.querySelector('.zato-debugger-watches'),
                watchesList: container.querySelector('.zato-debugger-watches-list'),
                watchInput: container.querySelector('.zato-debugger-watch-input'),
                breakpointsPanel: container.querySelector('.zato-debugger-breakpoints'),
                breakpointsList: container.querySelector('.zato-debugger-breakpoints-list'),
                consolePanel: container.querySelector('.zato-debugger-console'),
                consoleOutput: container.querySelector('.zato-debugger-console-output'),
                consoleInput: container.querySelector('.zato-debugger-console-input')
            };
        },

        renderToolbar: function(instance) {
            var html = '';
            html += '<div class="zato-debugger-toolbar">';
            html += '<div class="zato-debugger-toolbar-group">';
            html += this.renderToolbarButton('continue', 'Continue', 'F5', this.getContinueIcon());
            html += this.renderToolbarButton('pause', 'Pause', 'F6', this.getPauseIcon());
            html += '</div>';
            html += '<div class="zato-debugger-toolbar-separator"></div>';
            html += '<div class="zato-debugger-toolbar-group">';
            html += this.renderToolbarButton('step-over', 'Step over', 'F10', this.getStepOverIcon());
            html += this.renderToolbarButton('step-into', 'Step into', 'F11', this.getStepIntoIcon());
            html += this.renderToolbarButton('step-out', 'Step out', 'Shift+F11', this.getStepOutIcon());
            html += '</div>';
            html += '<div class="zato-debugger-toolbar-separator"></div>';
            html += '<div class="zato-debugger-toolbar-group">';
            html += this.renderToolbarButton('restart', 'Restart', 'Ctrl+Shift+F5', this.getRestartIcon());
            html += this.renderToolbarButton('stop', 'Stop', 'Shift+F5', this.getStopIcon());
            html += '</div>';
            html += '</div>';
            return html;
        },

        renderToolbarButton: function(action, title, shortcut, iconPath) {
            var tooltip = title + ' (' + shortcut + ')';
            var iconHtml = iconPath.startsWith('<') ? iconPath : '<img src="' + iconPath + '" alt="' + title + '" class="zato-debugger-toolbar-icon">';
            return '<button class="zato-debugger-toolbar-button" data-action="' + action + '" data-tooltip="' + tooltip + '">' +
                   iconHtml + '</button>';
        },

        renderCallStackPanel: function(instance) {
            var html = '';
            html += '<div class="zato-debugger-panel zato-debugger-callstack">';
            html += '<div class="zato-debugger-panel-header" data-panel="callStack">';
            html += '<span class="zato-debugger-panel-toggle">' + this.getChevronIcon() + '</span>';
            html += '<span class="zato-debugger-panel-title">Call stack</span>';
            html += '<button class="zato-debugger-copy-btn" data-copy="callstack" data-tooltip="Copy to clipboard">Copy</button>';
            html += '</div>';
            html += '<div class="zato-debugger-panel-content">';
            html += '<div class="zato-debugger-callstack-list"></div>';
            html += '</div>';
            html += '</div>';
            return html;
        },

        renderVariablesPanel: function(instance) {
            var html = '';
            html += '<div class="zato-debugger-panel zato-debugger-variables">';
            html += '<div class="zato-debugger-panel-header" data-panel="variables">';
            html += '<span class="zato-debugger-panel-toggle">' + this.getChevronIcon() + '</span>';
            html += '<span class="zato-debugger-panel-title">Variables</span>';
            html += '<button class="zato-debugger-copy-btn" data-copy="variables" data-tooltip="Copy to clipboard">Copy</button>';
            html += '</div>';
            html += '<div class="zato-debugger-panel-content">';
            html += '<div class="zato-debugger-variables-list"></div>';
            html += '</div>';
            html += '</div>';
            return html;
        },

        renderWatchesPanel: function(instance) {
            var html = '';
            html += '<div class="zato-debugger-panel zato-debugger-watches">';
            html += '<div class="zato-debugger-panel-header" data-panel="watches">';
            html += '<span class="zato-debugger-panel-toggle">' + this.getChevronIcon() + '</span>';
            html += '<span class="zato-debugger-panel-title">Watch</span>';
            html += '<button class="zato-debugger-panel-action" data-action="add-watch" title="Add expression">';
            html += this.getPlusIcon();
            html += '</button>';
            html += '</div>';
            html += '<div class="zato-debugger-panel-content">';
            html += '<div class="zato-debugger-watches-list"></div>';
            html += '<input type="text" class="zato-debugger-watch-input" placeholder="Add expression...">';
            html += '</div>';
            html += '</div>';
            return html;
        },

        renderBreakpointsPanel: function(instance) {
            var html = '';
            html += '<div class="zato-debugger-panel zato-debugger-breakpoints">';
            html += '<div class="zato-debugger-panel-header" data-panel="breakpoints">';
            html += '<span class="zato-debugger-panel-toggle">' + this.getChevronIcon() + '</span>';
            html += '<span class="zato-debugger-panel-title">Breakpoints</span>';
            html += '<button class="zato-debugger-panel-action" data-action="clear-breakpoints" data-tooltip="Remove all breakpoints">';
            html += this.getTrashIcon();
            html += '</button>';
            html += '</div>';
            html += '<div class="zato-debugger-panel-content">';
            html += '<div class="zato-debugger-breakpoints-list"></div>';
            html += '</div>';
            html += '</div>';
            return html;
        },

        renderConsolePanel: function(instance) {
            var html = '';
            html += '<div class="zato-debugger-panel zato-debugger-console">';
            html += '<div class="zato-debugger-panel-header" data-panel="console">';
            html += '<span class="zato-debugger-panel-toggle">' + this.getChevronIcon() + '</span>';
            html += '<span class="zato-debugger-panel-title">Debug console</span>';
            html += '<button class="zato-debugger-panel-action" data-action="clear-console" data-tooltip="Clear console">';
            html += this.getTrashIcon();
            html += '</button>';
            html += '</div>';
            html += '<div class="zato-debugger-panel-content zato-debugger-console-content">';
            html += '<div class="zato-debugger-console-output"></div>';
            html += '<div class="zato-debugger-console-input-wrapper">';
            html += '<span class="zato-debugger-console-prompt">&gt;</span>';
            html += '<input type="text" class="zato-debugger-console-input" placeholder="Evaluate expression...">';
            html += '</div>';
            html += '</div>';
            html += '</div>';
            return html;
        },

        bindEvents: function(instance) {
            var self = this;
            var container = instance.container;

            container.addEventListener('click', function(e) {
                var copyBtn = e.target.closest('.zato-debugger-copy-btn');
                if (copyBtn) {
                    e.stopPropagation();
                    var copyType = copyBtn.getAttribute('data-copy');
                    self.copyPanelContent(instance, copyType);
                    if (instance.tooltip && typeof ZatoTooltip !== 'undefined') {
                        ZatoTooltip.showTemporary(instance.tooltip, copyBtn, 'Copied to clipboard', 1100);
                    }
                    return;
                }

                var actionBtn = e.target.closest('.zato-debugger-panel-action');
                if (actionBtn) {
                    e.stopPropagation();
                    var action = actionBtn.getAttribute('data-action');
                    self.handleAction(instance, action, e);
                    if (instance.tooltip && typeof ZatoTooltip !== 'undefined') {
                        ZatoTooltip.hide(instance.tooltip);
                    }
                    return;
                }

                var button = e.target.closest('[data-action]');
                if (button) {
                    var action = button.getAttribute('data-action');
                    self.handleAction(instance, action, e);
                }

                var header = e.target.closest('.zato-debugger-panel-header[data-panel]');
                if (header) {
                    var panel = header.getAttribute('data-panel');
                    self.togglePanel(instance, panel);
                }

                var frameItem = e.target.closest('.zato-debugger-frame-item');
                if (frameItem) {
                    var frameId = parseInt(frameItem.getAttribute('data-frame-id'), 10);
                    self.selectFrame(instance, frameId);
                }

                var bpItem = e.target.closest('.zato-debugger-breakpoint-item');
                if (bpItem && !e.target.closest('.zato-debugger-breakpoint-checkbox')) {
                    var file = bpItem.getAttribute('data-file');
                    var line = parseInt(bpItem.getAttribute('data-line'), 10);
                    self.jumpToBreakpoint(instance, file, line);
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
                    self.toggleVariable(instance, varItem);
                }
            });

            var watchInput = instance.elements.watchInput;
            if (watchInput) {
                watchInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && watchInput.value.trim()) {
                        ZatoDebuggerCore.addWatch(instance.debugger, watchInput.value.trim());
                        watchInput.value = '';
                        self.updateWatches(instance);
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
                        self.evaluateInConsole(instance, expr);
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
                    self.updateToolbarState(instance);
                });

                ZatoDebuggerCore.on(instance.debugger, 'onCallStackUpdate', function(data) {
                    self.updateCallStack(instance, data.frames);
                });

                ZatoDebuggerCore.on(instance.debugger, 'onVariablesUpdate', function(data) {
                    self.updateVariables(instance, data.scopeRef, data.variables);
                });

                ZatoDebuggerCore.on(instance.debugger, 'onOutput', function(data) {
                    self.appendConsoleOutput(instance, data.category, data.output);
                });

                ZatoDebuggerCore.on(instance.debugger, 'onBreakpointHit', function(data) {
                    self.highlightCurrentLine(instance);
                });
            }

            document.addEventListener('keydown', function(e) {
                if (!instance.debugger || !ZatoDebuggerCore.isDebugging(instance.debugger)) {
                    return;
                }

                if (e.key === 'F5' && !e.shiftKey && !e.ctrlKey) {
                    e.preventDefault();
                    self.handleAction(instance, 'continue');
                } else if (e.key === 'F6') {
                    e.preventDefault();
                    self.handleAction(instance, 'pause');
                } else if (e.key === 'F10') {
                    e.preventDefault();
                    self.handleAction(instance, 'step-over');
                } else if (e.key === 'F11' && !e.shiftKey) {
                    e.preventDefault();
                    self.handleAction(instance, 'step-into');
                } else if (e.key === 'F11' && e.shiftKey) {
                    e.preventDefault();
                    self.handleAction(instance, 'step-out');
                } else if (e.key === 'F5' && e.shiftKey && !e.ctrlKey) {
                    e.preventDefault();
                    self.handleAction(instance, 'stop');
                } else if (e.key === 'F5' && e.ctrlKey && e.shiftKey) {
                    e.preventDefault();
                    self.handleAction(instance, 'restart');
                }
            });
        },

        handleAction: function(instance, action, event) {
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
                    this.updateBreakpoints(instance);
                    break;
                case 'clear-console':
                    if (instance.elements.consoleOutput) {
                        instance.elements.consoleOutput.innerHTML = '';
                    }
                    break;
                case 'add-watch':
                    if (instance.elements.watchInput) {
                        instance.elements.watchInput.focus();
                    }
                    break;
            }
        },

        togglePanel: function(instance, panelName) {
            instance.expanded[panelName] = !instance.expanded[panelName];
            var panel = instance.container.querySelector('.zato-debugger-' + panelName.toLowerCase());
            if (panel) {
                panel.classList.toggle('collapsed', !instance.expanded[panelName]);
            }
        },

        copyPanelContent: function(instance, copyType) {
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
            }

            if (text) {
                navigator.clipboard.writeText(text).catch(function(err) {
                    console.error('Failed to copy:', err);
                });
            }
        },

        updateToolbarState: function(instance) {
            var dbg = instance.debugger;
            if (!dbg) {
                return;
            }

            var state = ZatoDebuggerCore.getState(dbg);
            var isPaused = state === ZatoDebuggerCore.DebugState.PAUSED;
            var isRunning = state === ZatoDebuggerCore.DebugState.RUNNING;
            var isDebugging = ZatoDebuggerCore.isDebugging(dbg);

            this.setButtonEnabled(instance.elements.continueBtn, isPaused);
            this.setButtonEnabled(instance.elements.pauseBtn, isRunning);
            this.setButtonEnabled(instance.elements.stepOverBtn, isPaused);
            this.setButtonEnabled(instance.elements.stepIntoBtn, isPaused);
            this.setButtonEnabled(instance.elements.stepOutBtn, isPaused);
            this.setButtonEnabled(instance.elements.restartBtn, isDebugging);
            this.setButtonEnabled(instance.elements.stopBtn, isDebugging);
        },

        setButtonEnabled: function(button, enabled) {
            if (button) {
                button.disabled = !enabled;
                button.classList.toggle('disabled', !enabled);
            }
        },

        updateCallStack: function(instance, frames) {
            var list = instance.elements.callStackList;
            if (!list) {
                return;
            }

            if (!frames || frames.length === 0) {
                list.innerHTML = '<div class="zato-debugger-empty">No call stack</div>';
                return;
            }

            var html = '';
            for (var i = 0; i < frames.length; i++) {
                var frame = frames[i];
                var isActive = i === 0;
                var source = frame.source ? frame.source.name : 'unknown';
                html += '<div class="zato-debugger-frame-item' + (isActive ? ' active' : '') + '" data-frame-id="' + frame.id + '">';
                html += '<span class="zato-debugger-frame-name">' + this.escapeHtml(frame.name) + '</span>';
                html += '<span class="zato-debugger-frame-location">' + this.escapeHtml(source) + ':' + frame.line + '</span>';
                html += '</div>';
            }
            list.innerHTML = html;
        },

        updateVariables: function(instance, scopeRef, variables) {
            var list = instance.elements.variablesList;
            if (!list) {
                return;
            }

            if (!variables || variables.length === 0) {
                list.innerHTML = '<div class="zato-debugger-empty">No variables</div>';
                return;
            }

            var html = this.renderVariablesList(variables, 0);
            list.innerHTML = html;
        },

        renderVariablesList: function(variables, depth) {
            var html = '';
            for (var i = 0; i < variables.length; i++) {
                var v = variables[i];
                var hasChildren = v.variablesReference && v.variablesReference > 0;
                var indent = depth * 16;
                html += '<div class="zato-debugger-variable-item' + (hasChildren ? ' expandable' : '') + '" ';
                html += 'data-ref="' + (v.variablesReference || 0) + '" style="padding-left: ' + indent + 'px;">';
                if (hasChildren) {
                    html += '<span class="zato-debugger-variable-toggle">' + this.getChevronIcon() + '</span>';
                }
                html += '<span class="zato-debugger-variable-name">' + this.escapeHtml(v.name) + '</span>';
                html += '<span class="zato-debugger-variable-separator">:</span>';
                html += '<span class="zato-debugger-variable-value">' + this.escapeHtml(v.value) + '</span>';
                if (v.type) {
                    html += '<span class="zato-debugger-variable-type">' + this.escapeHtml(v.type) + '</span>';
                }
                html += '</div>';
            }
            return html;
        },

        toggleVariable: function(instance, varItem) {
            varItem.classList.toggle('expanded');
        },

        updateWatches: function(instance) {
            var list = instance.elements.watchesList;
            if (!list) {
                return;
            }

            var watches = instance.debugger ? instance.debugger.watches : [];
            if (!watches || watches.length === 0) {
                list.innerHTML = '<div class="zato-debugger-empty">No watch expressions</div>';
                return;
            }

            var html = '';
            for (var i = 0; i < watches.length; i++) {
                var w = watches[i];
                html += '<div class="zato-debugger-watch-item" data-watch-id="' + w.id + '">';
                html += '<span class="zato-debugger-watch-expr">' + this.escapeHtml(w.expression) + '</span>';
                html += '<span class="zato-debugger-watch-separator">:</span>';
                html += '<span class="zato-debugger-watch-value">' + this.highlightPythonValue(w.value || '<not available>') + '</span>';
                html += '<button class="zato-debugger-watch-remove" data-action="remove-watch" data-watch-id="' + w.id + '">';
                html += this.getCloseIcon();
                html += '</button>';
                html += '</div>';
            }
            list.innerHTML = html;
        },

        updateBreakpoints: function(instance) {
            var list = instance.elements.breakpointsList;
            if (!list) {
                return;
            }

            var breakpoints = instance.debugger ? ZatoDebuggerCore.getAllBreakpoints(instance.debugger) : [];
            if (!breakpoints || breakpoints.length === 0) {
                list.innerHTML = '<div class="zato-debugger-empty">No breakpoints</div>';
                return;
            }

            var html = '';
            for (var i = 0; i < breakpoints.length; i++) {
                var bp = breakpoints[i];
                var filename = bp.file.split('/').pop();
                html += '<div class="zato-debugger-breakpoint-item" data-file="' + this.escapeHtml(bp.file) + '" data-line="' + bp.line + '">';
                html += '<input type="checkbox" class="zato-debugger-breakpoint-checkbox"' + (bp.enabled ? ' checked' : '') + '>';
                html += '<span class="zato-debugger-breakpoint-icon">' + this.getBreakpointIcon() + '</span>';
                html += '<span class="zato-debugger-breakpoint-file">' + this.escapeHtml(filename) + '</span>';
                html += '<span class="zato-debugger-breakpoint-line">:' + bp.line + '</span>';
                if (bp.condition) {
                    html += '<span class="zato-debugger-breakpoint-condition">' + this.escapeHtml(bp.condition) + '</span>';
                }
                html += '</div>';
            }
            list.innerHTML = html;
        },

        selectFrame: function(instance, frameId) {
            if (instance.debugger) {
                ZatoDebuggerCore.selectFrame(instance.debugger, frameId);
            }

            var items = instance.elements.callStackList.querySelectorAll('.zato-debugger-frame-item');
            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                var id = parseInt(item.getAttribute('data-frame-id'), 10);
                item.classList.toggle('active', id === frameId);
            }
        },

        jumpToBreakpoint: function(instance, file, line) {
            if (instance.onJumpToLine) {
                instance.onJumpToLine(file, line);
            }
        },

        evaluateInConsole: function(instance, expression) {
            this.appendConsoleOutput(instance, 'input', '> ' + expression);

            if (instance.debugger && ZatoDebuggerCore.isPaused(instance.debugger)) {
                var frame = instance.debugger.currentFrame;
                if (frame && typeof ZatoDebuggerProtocol !== 'undefined') {
                    var self = this;
                    ZatoDebuggerProtocol.evaluate(instance.debugger, expression, frame.id, function(result) {
                        self.appendConsoleOutput(instance, 'output', result.result);
                    });
                }
            } else {
                this.appendConsoleOutput(instance, 'error', 'Cannot evaluate: debugger not paused');
            }
        },

        appendConsoleOutput: function(instance, category, text) {
            var output = instance.elements.consoleOutput;
            if (!output) {
                return;
            }

            var line = document.createElement('div');
            line.className = 'zato-debugger-console-line zato-debugger-console-' + category;
            if (category === 'output') {
                line.innerHTML = this.highlightPythonValue(text);
            } else {
                line.textContent = text;
            }
            output.appendChild(line);
            output.scrollTop = output.scrollHeight;
        },

        highlightPythonValue: function(text) {
            if (text === null || text === undefined) {
                return '';
            }
            var escaped = this.escapeHtml(String(text));
            escaped = escaped.replace(/\b(True|False|None)\b/g, '<span class="zato-debugger-hl-keyword">$1</span>');
            escaped = escaped.replace(/\b(\d+\.?\d*)\b/g, '<span class="zato-debugger-hl-number">$1</span>');
            escaped = escaped.replace(/('[^']*'|"[^"]*")/g, '<span class="zato-debugger-hl-string">$1</span>');
            escaped = escaped.replace(/&lt;([^&]+)&gt;/g, '<span class="zato-debugger-hl-type">&lt;$1&gt;</span>');
            return escaped;
        },

        highlightCurrentLine: function(instance) {
            if (instance.onHighlightLine && instance.debugger) {
                var dbg = instance.debugger;
                if (dbg.currentFile && dbg.currentLine) {
                    instance.onHighlightLine(dbg.currentFile, dbg.currentLine);
                }
            }
        },

        escapeHtml: function(text) {
            if (text === null || text === undefined) {
                return '';
            }
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        getContinueIcon: function() {
            return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M3 2l10 6-10 6V2z"/></svg>';
        },

        getPauseIcon: function() {
            return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><rect x="3" y="2" width="4" height="12"/><rect x="9" y="2" width="4" height="12"/></svg>';
        },

        getStepOverIcon: function() {
            return '/static/img/debugger/step-over.svg';
        },

        getStepIntoIcon: function() {
            return '/static/img/debugger/step-into.svg';
        },

        getStepOutIcon: function() {
            return '/static/img/debugger/step-out.svg';
        },

        getRestartIcon: function() {
            return '/static/img/debugger/restart.svg';
        },

        getStopIcon: function() {
            return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><rect x="3" y="3" width="10" height="10"/></svg>';
        },

        getChevronIcon: function() {
            return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="12" height="12" fill="currentColor"><path d="M6 4l4 4-4 4"/></svg>';
        },

        getPlusIcon: function() {
            return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M8 2v12M2 8h12"/></svg>';
        },

        getTrashIcon: function() {
            return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M5 2V1h6v1h4v2H1V2h4zm1 3h1v8H6V5zm3 0h1v8H9V5zM3 4v10h10V4H3z"/></svg>';
        },

        getCloseIcon: function() {
            return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="12" height="12" fill="currentColor"><path d="M12 4L4 12M4 4l8 8"/></svg>';
        },

        getBreakpointIcon: function() {
            return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="12" height="12" fill="#e51400"><circle cx="8" cy="8" r="6"/></svg>';
        }
    };

    window.ZatoDebuggerUI = ZatoDebuggerUI;

})();
