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
            this.updateBreakpoints(instance);
            this.preloadSpinner();

            this.instances[containerId] = instance;

            console.log('[DebuggerUI] create: END returning instance');
            return instance;
        },

        getInstance: function(containerId) {
            return this.instances[containerId] || null;
        },

        reattach: function(instance, containerId) {
            console.log('[DebuggerUI] reattach: START containerId=' + containerId);
            console.log('[DebuggerUI] reattach: isConnected=' + instance.isConnected + ' isConnecting=' + instance.isConnecting);

            var container = document.getElementById(containerId);
            if (!container) {
                console.log('[DebuggerUI] reattach: container not found');
                return;
            }

            instance.container = container;
            instance.id = containerId;

            this.render(instance);
            this.initTooltip(instance);
            this.bindEvents(instance);
            this.cacheElements(instance);
            this.updateToolbarState(instance);

            if (instance.isConnecting) {
                console.log('[DebuggerUI] reattach: restoring connecting state');
                this.restoreConnectingState(instance);
            } else if (instance._errorMessage) {
                console.log('[DebuggerUI] reattach: restoring error state');
                this.showError(instance, instance._errorMessage);
            } else {
                this.updatePanelsVisibility(instance);
            }

            this.restoreConsoleOutput(instance);
            this.restoreWatches(instance);

            this.instances[containerId] = instance;
            console.log('[DebuggerUI] reattach: END');
        },

        restoreConnectingState: function(instance) {
            console.log('[DebuggerUI] restoreConnectingState: START');
            var panelsContainer = instance.container.querySelector('.zato-debugger-panels');
            var consolePanel = instance.container.querySelector('.zato-debugger-console');

            if (panelsContainer) {
                var remaining = instance._countdownRemaining || 10.00;
                panelsContainer.style.display = '';
                panelsContainer.innerHTML = '<div class="zato-debugger-connecting">' +
                    '<span class="zato-debugger-message-box">' +
                    '<img src="/static/img/spinner.svg" class="ai-chat-spinner-icon ai-chat-spinner-large" alt="">' +
                    ' Connecting .. <span class="zato-debugger-countdown">' + remaining.toFixed(2) + ' s</span></span>' +
                    '</div>';
            }

            if (consolePanel) {
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
            console.log('[DebuggerUI] restoreConnectingState: END');
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

        preloadSpinner: function() {
            if (!this._spinnerPreloaded) {
                var img = new Image();
                img.src = '/static/img/spinner.svg';
                this._spinnerPreloaded = true;
            }
        },

        showConnecting: function(instance) {
            console.log('[DebuggerUI] showConnecting: START instance=' + (instance ? 'ok' : 'null'));
            if (!instance) {
                console.log('[DebuggerUI] showConnecting: no instance, returning');
                return;
            }

            instance.isConnecting = true;
            console.log('[DebuggerUI] showConnecting: set isConnecting=true');

            this.startConnectingCountdown(instance);

            var self = this;
            var panelsContainer = instance.container.querySelector('.zato-debugger-panels');
            var consolePanel = instance.container.querySelector('.zato-debugger-console');
            var startButton = panelsContainer ? panelsContainer.querySelector('.zato-debugger-start-button') : null;

            function showSpinner() {
                if (!instance.isConnecting) {
                    console.log('[DebuggerUI] showSpinner: isConnecting=false, skipping');
                    return;
                }
                if (panelsContainer) {
                    panelsContainer.style.display = '';
                    instance._savedPanelsHTML = panelsContainer.innerHTML;
                    panelsContainer.innerHTML = '<div class="zato-debugger-connecting">' +
                        '<span class="zato-debugger-message-box">' +
                        '<img src="/static/img/spinner.svg" class="ai-chat-spinner-icon ai-chat-spinner-large" alt="">' +
                        ' Connecting .. <span class="zato-debugger-countdown">' + (instance._countdownRemaining || 10).toFixed(2) + ' s</span></span>' +
                        '</div>';
                }

                if (consolePanel) {
                    instance._savedConsoleDisplay = consolePanel.style.display;
                    consolePanel.style.display = 'none';
                }

                if (instance.elements) {
                    self.setButtonEnabled(instance.elements.continueBtn, false);
                    self.setButtonEnabled(instance.elements.pauseBtn, false);
                    self.setButtonEnabled(instance.elements.stepOverBtn, false);
                    self.setButtonEnabled(instance.elements.stepIntoBtn, false);
                    self.setButtonEnabled(instance.elements.stepOutBtn, false);
                    self.setButtonEnabled(instance.elements.restartBtn, false);
                    self.setButtonEnabled(instance.elements.stopBtn, false);
                }
            }

            if (startButton) {
                var transitionFired = false;
                function onFadeComplete() {
                    if (transitionFired) {
                        return;
                    }
                    transitionFired = true;
                    showSpinner();
                }
                startButton.style.transition = 'opacity 70ms ease-out';
                startButton.addEventListener('transitionend', onFadeComplete);
                window.requestAnimationFrame(function() {
                    startButton.style.opacity = '0';
                });
                instance._fadeOutTimer = window.setTimeout(onFadeComplete, 80);
            } else {
                showSpinner();
            }
        },

        startConnectingCountdown: function(instance) {
            var self = this;
            var remaining = 10.00;
            instance._countdownRemaining = remaining;

            if (instance._countdownInterval) {
                clearInterval(instance._countdownInterval);
            }

            console.log('[DebuggerUI] startConnectingCountdown: starting interval');
            instance._countdownInterval = setInterval(function() {
                remaining -= 0.01;
                instance._countdownRemaining = remaining;
                if (remaining <= 0) {
                    console.log('[DebuggerUI] startConnectingCountdown: countdown reached 0, isConnecting=' + instance.isConnecting);
                    clearInterval(instance._countdownInterval);
                    delete instance._countdownInterval;
                    delete instance._countdownRemaining;
                    if (instance.isConnecting) {
                        console.log('[DebuggerUI] startConnectingCountdown: still connecting, showing timeout error');
                        self.showError(instance, 'UI connection timeout');
                    }
                    return;
                }
                var countdownEl = instance.container.querySelector('.zato-debugger-countdown');
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
            console.log('[DebuggerUI] hideConnecting: START instance=' + (instance ? 'ok' : 'null'));
            if (!instance) {
                console.log('[DebuggerUI] hideConnecting: no instance, returning');
                return;
            }

            console.log('[DebuggerUI] hideConnecting: setting isConnecting=false');
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
            console.log('[DebuggerUI] setConnected: connected=' + connected);
            if (!instance) {
                return;
            }
            instance.isConnected = connected;
            this.updatePanelsVisibility(instance);
            this.updateToolbarState(instance);
        },

        updatePanelsVisibility: function(instance) {
            console.log('[DebuggerUI] updatePanelsVisibility: isConnected=' + instance.isConnected + ' isConnecting=' + instance.isConnecting);
            if (!instance) {
                return;
            }
            var panelsContainer = instance.container.querySelector('.zato-debugger-panels');
            var consolePanel = instance.container.querySelector('.zato-debugger-console');

            if (instance.isConnected) {
                console.log('[DebuggerUI] updatePanelsVisibility: showing connected panels');
                if (panelsContainer) {
                    panelsContainer.style.display = '';
                    var hasRealPanels = panelsContainer.querySelector('.zato-debugger-callstack');
                    if (!hasRealPanels) {
                        console.log('[DebuggerUI] updatePanelsVisibility: restoring panels HTML');
                        panelsContainer.innerHTML = this.renderCallStackPanel(instance) +
                            this.renderVariablesPanel(instance) +
                            this.renderWatchesPanel(instance) +
                            this.renderBreakpointsPanel(instance);
                        this.cacheElements(instance);
                        this.restoreWatches(instance);
                        this.updateBreakpoints(instance);
                    }
                }
                if (consolePanel) {
                    consolePanel.style.display = '';
                }
            } else {
                console.log('[DebuggerUI] updatePanelsVisibility: showing disconnected panels');
                if (panelsContainer) {
                    panelsContainer.style.display = '';
                    var hasRealPanels = panelsContainer.querySelector('.zato-debugger-callstack');
                    if (!hasRealPanels) {
                        console.log('[DebuggerUI] updatePanelsVisibility: restoring panels HTML for disconnected state');
                        panelsContainer.innerHTML = '<div class="zato-debugger-start-container" style="display:none;">' +
                            '<button class="zato-debugger-start-button" data-action="start-debugging">Start debugging</button>' +
                            '</div>' +
                            this.renderCallStackPanel(instance) +
                            this.renderVariablesPanel(instance) +
                            this.renderWatchesPanel(instance) +
                            this.renderBreakpointsPanel(instance);
                        this.cacheElements(instance);
                        this.restoreWatches(instance);
                        this.updateBreakpoints(instance);
                    }
                }
                if (consolePanel) {
                    consolePanel.style.display = '';
                }
            }
        },

        showError: function(instance, errorMessage) {
            console.log('[DebuggerUI] showError: errorMessage=' + errorMessage);
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
