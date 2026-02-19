(function() {
    'use strict';

    var ZatoTooltip = {

        instances: {},
        nextId: 1,

        create: function(containerId, options) {
            options = options || {};

            var instance = {
                id: 'zato-tooltip-' + this.nextId++,
                containerId: containerId,
                container: null,
                tooltipEl: null,
                currentTarget: null,
                hideTimerId: null,
                isLocked: false,
                theme: options.theme || 'dark',
                attribute: options.attribute || 'data-tooltip',
                timeoutAttribute: options.timeoutAttribute || 'data-tooltip-timeout',
                isPopupOpen: options.isPopupOpen || null,
                handlers: {}
            };

            this.instances[containerId] = instance;
            this.initInstance(instance);

            return instance;
        },

        getInstance: function(containerId) {
            return this.instances[containerId] || null;
        },

        initInstance: function(instance) {
            instance.container = document.getElementById(instance.containerId);
            if (!instance.container) {
                instance.container = document.querySelector('.' + instance.containerId);
            }
            if (!instance.container) {
                return;
            }

            instance.tooltipEl = document.createElement('div');
            instance.tooltipEl.className = 'zato-tooltip zato-tooltip-theme-' + instance.theme;
            document.body.appendChild(instance.tooltipEl);

            this.attachEvents(instance);
        },

        attachEvents: function(instance) {
            var self = this;

            instance.handlers.mouseenter = function(e) {
                var target = e.target;

                if (!target.hasAttribute || !target.hasAttribute(instance.attribute)) {
                    return;
                }

                if (!instance.container.contains(target)) {
                    return;
                }

                if (instance.isPopupOpen && instance.isPopupOpen(target)) {
                    return;
                }

                self.show(instance, target);

                var timeout = target.getAttribute(instance.timeoutAttribute);
                if (timeout) {
                    instance.hideTimerId = setTimeout(function() {
                        self.hide(instance);
                    }, parseInt(timeout, 10));
                }
            };

            instance.handlers.mouseleave = function(e) {
                if (instance.isLocked) {
                    return;
                }
                var target = e.target;
                if (target.hasAttribute && target.hasAttribute(instance.attribute)) {
                    self.hide(instance);
                }
            };

            instance.container.addEventListener('mouseenter', instance.handlers.mouseenter, true);
            instance.container.addEventListener('mouseleave', instance.handlers.mouseleave, true);
        },

        show: function(instance, target) {
            if (!instance.tooltipEl) {
                return;
            }

            var text = target.getAttribute(instance.attribute);
            if (!text) {
                return;
            }

            instance.currentTarget = target;
            instance.tooltipEl.textContent = text;
            instance.tooltipEl.style.opacity = '1';
            instance.tooltipEl.style.visibility = 'visible';

            this.position(instance, target);
        },

        position: function(instance, target) {
            var rect = target.getBoundingClientRect();
            instance.tooltipEl.style.visibility = 'hidden';
            instance.tooltipEl.style.display = 'block';
            var tooltipRect = instance.tooltipEl.getBoundingClientRect();
            instance.tooltipEl.style.visibility = 'visible';

            var left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
            var top = rect.top - tooltipRect.height - 6;

            if (left < 5) {
                left = 5;
            }
            if (left + tooltipRect.width > window.innerWidth - 5) {
                left = window.innerWidth - tooltipRect.width - 5;
            }

            instance.tooltipEl.style.left = left + 'px';
            instance.tooltipEl.style.top = top + 'px';
        },

        positionLeft: function(instance, target) {
            var rect = target.getBoundingClientRect();
            instance.tooltipEl.style.visibility = 'hidden';
            instance.tooltipEl.style.display = 'block';
            var tooltipRect = instance.tooltipEl.getBoundingClientRect();
            instance.tooltipEl.style.visibility = 'visible';

            var left = rect.left;
            var top = rect.top - tooltipRect.height - 6;

            if (left < 5) {
                left = 5;
            }
            if (left + tooltipRect.width > window.innerWidth - 5) {
                left = window.innerWidth - tooltipRect.width - 5;
            }

            instance.tooltipEl.style.left = left + 'px';
            instance.tooltipEl.style.top = top + 'px';
        },

        positionBottom: function(instance, target) {
            var rect = target.getBoundingClientRect();
            instance.tooltipEl.style.visibility = 'hidden';
            instance.tooltipEl.style.display = 'block';
            var tooltipRect = instance.tooltipEl.getBoundingClientRect();
            instance.tooltipEl.style.visibility = 'visible';

            var left = rect.left;
            var top = rect.bottom + 4;

            if (left < 5) {
                left = 5;
            }
            if (left + tooltipRect.width > window.innerWidth - 5) {
                left = window.innerWidth - tooltipRect.width - 5;
            }

            instance.tooltipEl.style.left = left + 'px';
            instance.tooltipEl.style.top = top + 'px';
        },

        hide: function(instance) {
            if (!instance.tooltipEl) {
                return;
            }
            if (instance.hideTimerId) {
                clearTimeout(instance.hideTimerId);
                instance.hideTimerId = null;
            }
            instance.tooltipEl.style.opacity = '0';
            instance.tooltipEl.style.visibility = 'hidden';
            instance.currentTarget = null;
        },

        showTemporary: function(instance, target, text, duration, alignment) {
            if (!instance.tooltipEl) {
                return;
            }

            instance.isLocked = true;
            instance.currentTarget = target;
            instance.tooltipEl.textContent = text;
            instance.tooltipEl.style.opacity = '1';
            instance.tooltipEl.style.visibility = 'visible';

            if (alignment === 'left') {
                this.positionLeft(instance, target);
            }
            else if (alignment === 'bottom') {
                this.positionBottom(instance, target);
            }
            else {
                this.position(instance, target);
            }

            var self = this;
            instance.hideTimerId = setTimeout(function() {
                instance.isLocked = false;
                self.hide(instance);
            }, duration);
        },

        setTheme: function(instance, theme) {
            if (!instance.tooltipEl) {
                return;
            }
            instance.tooltipEl.className = 'zato-tooltip zato-tooltip-theme-' + theme;
            instance.theme = theme;
        },

        destroy: function(containerId) {
            var instance = this.instances[containerId];
            if (!instance) {
                return;
            }

            if (instance.container) {
                instance.container.removeEventListener('mouseenter', instance.handlers.mouseenter, true);
                instance.container.removeEventListener('mouseleave', instance.handlers.mouseleave, true);
            }

            if (instance.tooltipEl && instance.tooltipEl.parentNode) {
                instance.tooltipEl.parentNode.removeChild(instance.tooltipEl);
            }

            if (instance.hideTimerId) {
                clearTimeout(instance.hideTimerId);
            }

            delete this.instances[containerId];
        }

    };

    window.ZatoTooltip = ZatoTooltip;

})();
