(function() {
    'use strict';

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
            console.log('[DebuggerUI] create: opts.theme=' + opts.theme + ' opts.ide=' + (opts.ide ? 'present' : 'null'));

            var container = document.getElementById(containerId);
            console.log('[DebuggerUI] create: container=' + (container ? 'found' : 'not found'));
            if (!container) {
                console.error('[DebuggerUI] create: Container not found:', containerId);
                return null;
            }

            var savedExpanded = this.loadState('expanded') || {};
            var instance = {
                id: containerId,
                container: container,
                debugger: debuggerInstance,
                options: opts,
                elements: {},
                ide: opts.ide || null,
                isConnected: false,
                isConnecting: false,
                expanded: {
                    callStack: savedExpanded.callStack !== false,
                    variables: savedExpanded.variables !== false,
                    breakpoints: savedExpanded.breakpoints !== false,
                    watches: savedExpanded.watches !== false,
                    console: savedExpanded.console !== false
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

            this.updateToolbarState(instance);
            this.updatePanelsVisibility(instance);
            this.restoreConsoleOutput(instance);
            this.restoreWatches(instance);

            this.instances[containerId] = instance;

            console.log('[DebuggerUI] create: END returning instance');
            return instance;
        },

        getInstance: function(containerId) {
            return this.instances[containerId] || null;
        },

        storagePrefix: 'zato.debugger.',

        loadState: function(key) {
            try {
                var stored = localStorage.getItem(this.storagePrefix + key);
                return stored ? JSON.parse(stored) : null;
            } catch (err) {
                return null;
            }
        },

        saveState: function(key, value) {
            try {
                localStorage.setItem(this.storagePrefix + key, JSON.stringify(value));
            } catch (err) {}
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

        showConnecting: function(instance) {
            if (!instance) {
                return;
            }

            instance.isConnecting = true;

            var panelsContainer = instance.container.querySelector('.zato-debugger-panels');
            var consolePanel = instance.container.querySelector('.zato-debugger-console');

            if (panelsContainer) {
                panelsContainer.style.display = '';
                instance._savedPanelsHTML = panelsContainer.innerHTML;
                panelsContainer.innerHTML = '<div class="zato-debugger-connecting">' +
                    '<img src="/static/img/spinner.svg" class="ai-chat-spinner-icon ai-chat-spinner-large" alt="">' +
                    '<span>Connecting .. <span class="zato-debugger-countdown">10.00 s</span></span>' +
                    '</div>';
            }

            if (consolePanel) {
                instance._savedConsoleDisplay = consolePanel.style.display;
                consolePanel.style.display = 'none';
            }

            if (instance.elements) {
                this.setButtonEnabled(instance.elements.continueBtn, false);
                this.setButtonEnabled(instance.elements.pauseBtn, false);
                this.setButtonEnabled(instance.elements.stepOverBtn, false);
                this.setButtonEnabled(instance.elements.stepIntoBtn, false);
                this.setButtonEnabled(instance.elements.stepOutBtn, false);
                this.setButtonEnabled(instance.elements.restartBtn, false);
                this.setButtonEnabled(instance.elements.stopBtn, false);
            }

            this.startConnectingCountdown(instance);
        },

        startConnectingCountdown: function(instance) {
            var self = this;
            var remaining = 10.00;
            var countdownEl = instance.container.querySelector('.zato-debugger-countdown');

            if (instance._countdownInterval) {
                clearInterval(instance._countdownInterval);
            }

            instance._countdownInterval = setInterval(function() {
                remaining -= 0.01;
                if (remaining <= 0) {
                    clearInterval(instance._countdownInterval);
                    delete instance._countdownInterval;
                    if (instance.isConnecting) {
                        self.showError(instance, 'UI connection timeout');
                    }
                    return;
                }
                if (countdownEl) {
                    countdownEl.textContent = remaining.toFixed(2) + ' s';
                }
            }, 10);
        },

        stopConnectingCountdown: function(instance) {
            if (instance._countdownInterval) {
                clearInterval(instance._countdownInterval);
                delete instance._countdownInterval;
            }
        },

        hideConnecting: function(instance) {
            if (!instance) {
                return;
            }

            instance.isConnecting = false;
            this.stopConnectingCountdown(instance);

            var panelsContainer = instance.container.querySelector('.zato-debugger-panels');
            var consolePanel = instance.container.querySelector('.zato-debugger-console');

            if (panelsContainer && instance._savedPanelsHTML) {
                panelsContainer.innerHTML = instance._savedPanelsHTML;
                delete instance._savedPanelsHTML;
                this.cacheElements(instance);
            }

            if (consolePanel && instance._savedConsoleDisplay !== undefined) {
                consolePanel.style.display = instance._savedConsoleDisplay;
                delete instance._savedConsoleDisplay;
            }

            this.updateToolbarState(instance);
        },

        setConnected: function(instance, connected) {
            if (!instance) {
                return;
            }
            instance.isConnected = connected;
            this.updatePanelsVisibility(instance);
            this.updateToolbarState(instance);
        },

        updatePanelsVisibility: function(instance) {
            if (!instance) {
                return;
            }
            var panelsContainer = instance.container.querySelector('.zato-debugger-panels');
            var consolePanel = instance.container.querySelector('.zato-debugger-console');

            if (panelsContainer) {
                panelsContainer.style.display = instance.isConnected ? '' : 'none';
            }
            if (consolePanel) {
                consolePanel.style.display = instance.isConnected ? '' : 'none';
            }
        },

        showError: function(instance, errorMessage) {
            if (!instance) {
                return;
            }

            instance.isConnecting = false;
            this.stopConnectingCountdown(instance);

            var panelsContainer = instance.container.querySelector('.zato-debugger-panels');
            var consolePanel = instance.container.querySelector('.zato-debugger-console');

            if (panelsContainer) {
                instance._errorMessage = errorMessage;
                panelsContainer.innerHTML = '<div class="zato-debugger-error">' +
                    '<div class="zato-debugger-error-header">' +
                    '<span class="zato-debugger-error-title">Connection failed</span>' +
                    '<button class="zato-debugger-copy-btn" data-copy="error" data-tooltip="Copy to clipboard">Copy</button>' +
                    '</div>' +
                    '<div class="zato-debugger-error-message">' + this.escapeHtml(errorMessage) + '</div>' +
                    '</div>';
            }

            if (consolePanel) {
                consolePanel.style.display = 'none';
            }

            this.updateToolbarState(instance);
        },

        escapeHtml: function(text) {
            if (text === null || text === undefined) {
                return '';
            }
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    };

    window.ZatoDebuggerUI = ZatoDebuggerUI;

})();
