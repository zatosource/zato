(function() {
    'use strict';

    var ZatoIDESplit = {

        storageKey: 'zato.ide.split-position',
        defaultSplitPercent: 50,
        minPanelWidth: 200,

        instances: {},

        create: function(containerId, options) {
            var opts = options || {};
            var container = document.getElementById(containerId);
            if (!container) {
                console.error('ZatoIDESplit: container not found:', containerId);
                return null;
            }

            var savedPercent = this.loadSplitPosition();
            var splitPercent = savedPercent !== null ? savedPercent : this.defaultSplitPercent;

            var instance = {
                id: containerId,
                container: container,
                splitPercent: splitPercent,
                isDragging: false,
                idePanel: null,
                chatPanel: null,
                resizer: null,
                onResize: opts.onResize || null
            };

            this.render(instance);
            this.bindEvents(instance);
            this.instances[containerId] = instance;

            return instance;
        },

        render: function(instance) {
            var html = '';

            html += '<div class="zato-ide-split-container">';

            html += '<div class="zato-ide-split-panel zato-ide-split-panel-ide" id="' + instance.id + '-ide-panel">';
            html += '</div>';

            html += '<div class="zato-ide-split-resizer" id="' + instance.id + '-resizer"></div>';

            html += '<div class="zato-ide-split-panel zato-ide-split-panel-chat" id="' + instance.id + '-chat-panel">';
            html += '</div>';

            html += '</div>';

            instance.container.innerHTML = html;

            instance.idePanel = document.getElementById(instance.id + '-ide-panel');
            instance.chatPanel = document.getElementById(instance.id + '-chat-panel');
            instance.resizer = document.getElementById(instance.id + '-resizer');

            this.applySplitPosition(instance);
        },

        bindEvents: function(instance) {
            var self = this;

            instance.resizer.addEventListener('mousedown', function(e) {
                e.preventDefault();
                instance.isDragging = true;
                instance.resizer.classList.add('dragging');
                document.body.style.cursor = 'col-resize';
                document.body.style.userSelect = 'none';
            });

            document.addEventListener('mousemove', function(e) {
                if (!instance.isDragging) {
                    return;
                }

                var containerRect = instance.container.getBoundingClientRect();
                var containerWidth = containerRect.width;
                var resizerWidth = instance.resizer.offsetWidth;

                var newIdeWidth = e.clientX - containerRect.left;

                if (newIdeWidth < self.minPanelWidth) {
                    newIdeWidth = self.minPanelWidth;
                }

                var maxIdeWidth = containerWidth - self.minPanelWidth - resizerWidth;
                if (newIdeWidth > maxIdeWidth) {
                    newIdeWidth = maxIdeWidth;
                }

                instance.splitPercent = (newIdeWidth / containerWidth) * 100;
                self.applySplitPosition(instance);
            });

            document.addEventListener('mouseup', function() {
                if (instance.isDragging) {
                    instance.isDragging = false;
                    instance.resizer.classList.remove('dragging');
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                    self.saveSplitPosition(instance.splitPercent);

                    if (instance.onResize) {
                        instance.onResize(instance);
                    }
                }
            });
        },

        applySplitPosition: function(instance) {
            var containerWidth = instance.container.offsetWidth;
            var resizerWidth = instance.resizer ? instance.resizer.offsetWidth : 4;
            var ideWidth = (containerWidth * instance.splitPercent / 100);

            if (ideWidth < this.minPanelWidth) {
                ideWidth = this.minPanelWidth;
            }

            var maxIdeWidth = containerWidth - this.minPanelWidth - resizerWidth;
            if (ideWidth > maxIdeWidth) {
                ideWidth = maxIdeWidth;
            }

            if (instance.idePanel) {
                instance.idePanel.style.width = ideWidth + 'px';
            }
        },

        saveSplitPosition: function(percent) {
            try {
                localStorage.setItem(this.storageKey, percent.toString());
            } catch (e) {
                console.warn('ZatoIDESplit: failed to save split position:', e);
            }
        },

        loadSplitPosition: function() {
            try {
                var saved = localStorage.getItem(this.storageKey);
                if (saved !== null) {
                    var percent = parseFloat(saved);
                    if (!isNaN(percent) && percent >= 10 && percent <= 90) {
                        return percent;
                    }
                }
            } catch (e) {
                console.warn('ZatoIDESplit: failed to load split position:', e);
            }
            return null;
        },

        getIDEPanel: function(instance) {
            return instance ? instance.idePanel : null;
        },

        getChatPanel: function(instance) {
            return instance ? instance.chatPanel : null;
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
