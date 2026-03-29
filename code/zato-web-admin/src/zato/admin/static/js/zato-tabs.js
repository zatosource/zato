(function() {
    'use strict';

    function ZatoTabs(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        if (!this.container) return;

        this.nav = this.container.querySelector('.zato-tabs-nav');
        this.content = this.container.querySelector('.zato-tabs-content');
        if (!this.nav || !this.content) return;

        this.tabs = this.nav.querySelectorAll('li');
        this.panels = this.content.querySelectorAll('.zato-tabs-panel');
        this.callbacks = {};

        this.init();
    }

    ZatoTabs.prototype.init = function() {
        var self = this;
        this.tabs.forEach(function(tab) {
            var link = tab.querySelector('a');
            if (link) {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    var targetId = this.getAttribute('href').replace('#', '');
                    self.activate(targetId);
                });
            }
        });
    };

    ZatoTabs.prototype.activate = function(panelId) {
        var self = this;

        this.tabs.forEach(function(tab) {
            var link = tab.querySelector('a');
            if (link && link.getAttribute('href') === '#' + panelId) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });

        this.panels.forEach(function(panel) {
            if (panel.id === panelId) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });

        if (this.callbacks[panelId]) {
            this.callbacks[panelId].call(this, panelId);
        }

        if (this.onActivate) {
            this.onActivate.call(this, panelId);
        }
    };

    ZatoTabs.prototype.on = function(panelId, callback) {
        this.callbacks[panelId] = callback;
        return this;
    };

    ZatoTabs.prototype.onTabChange = function(callback) {
        this.onActivate = callback;
        return this;
    };

    ZatoTabs.prototype.getActivePanel = function() {
        var active = this.content.querySelector('.zato-tabs-panel.active');
        return active ? active.id : null;
    };

    if (typeof jQuery !== 'undefined') {
        jQuery.fn.zatoTabs = function() {
            return this.each(function() {
                var instance = new ZatoTabs(this);
                jQuery(this).data('zatoTabs', instance);
            });
        };
    }

    window.ZatoTabs = ZatoTabs;
})();
