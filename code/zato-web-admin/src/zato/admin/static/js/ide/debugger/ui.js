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
            console.log('[DebuggerUI] create: opts=' + JSON.stringify(opts));

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
        }
    };

    window.ZatoDebuggerUI = ZatoDebuggerUI;

})();
