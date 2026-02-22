(function() {
    'use strict';

    var ZatoIDESplit = {

        storageKey: 'zato.ide.split-position',
        defaultSplitPercent: 50,
        fallbackRightPanelWidth: 300,
        minPanelWidth: 300,
        snapThreshold: 250,
        expandStartPercent: 20,
        instances: {},

        create: function(containerId, options) {
            var opts = options || {};
            var container = document.getElementById(containerId);
            if (!container) {
                console.error('ZatoIDESplit: container not found:', containerId);
                return null;
            }

            var storageKey = opts.storageKey || this.storageKey;
            var defaultPercent = opts.defaultSplitPercent || this.defaultSplitPercent;
            var fallbackRightPanelWidth = opts.fallbackRightPanelWidth || this.fallbackRightPanelWidth;

            var instance = {
                id: containerId,
                container: container,
                splitPercent: defaultPercent,
                savedLeftPanelPixels: null,
                isDragging: false,
                leftPanel: null,
                rightPanel: null,
                resizer: null,
                onResize: opts.onResize || null,
                storageKey: storageKey,
                defaultSplitPercent: defaultPercent,
                fallbackRightPanelWidth: fallbackRightPanelWidth,
                minPanelWidth: opts.minPanelWidth || this.minPanelWidth
            };

            this.render(instance);
            this.bindEvents(instance);
            this.restoreSplitPosition(instance);
            this.instances[containerId] = instance;

            return instance;
        },

        render: function(instance) {
            var html = '';

            html += '<div class="zato-ide-split-container">';

            html += '<div class="zato-ide-split-panel zato-ide-split-panel-left" id="' + instance.id + '-left-panel">';
            html += '</div>';

            html += '<div class="zato-ide-split-resizer" id="' + instance.id + '-resizer"></div>';

            html += '<div class="zato-ide-split-panel zato-ide-split-panel-right" id="' + instance.id + '-right-panel">';
            html += '</div>';

            html += '</div>';

            instance.container.innerHTML = html;

            instance.leftPanel = document.getElementById(instance.id + '-left-panel');
            instance.rightPanel = document.getElementById(instance.id + '-right-panel');
            instance.resizer = document.getElementById(instance.id + '-resizer');

            this.applySplitPosition(instance);
        },

        getInstance: function(containerId) {
            return this.instances[containerId] || null;
        },

        destroy: function(containerId) {
            var instance = this.instances[containerId];
            if (instance) {
                instance.container.innerHTML = '';
                delete this.instances[containerId];
            }
        }
    };

    window.ZatoIDESplit = ZatoIDESplit;

})();
