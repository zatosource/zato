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
                positionAttribute: options.positionAttribute || 'data-tooltip-position',
                position: options.position || 'top',
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
                if (instance.isLocked) {
                    return;
                }

                var target = e.target;

                while (target && target !== instance.container) {
                    if (target.hasAttribute && target.hasAttribute(instance.attribute)) {
                        break;
                    }
                    target = target.parentElement;
                }

                if (!target || target === instance.container || !target.hasAttribute || !target.hasAttribute(instance.attribute)) {
                    return;
                }

                if (!instance.container.contains(target)) {
                    return;
                }

                var closerContainer = target.parentElement;
                while (closerContainer && closerContainer !== instance.container) {
                    if (self.instances[closerContainer.id]) {
                        return;
                    }
                    closerContainer = closerContainer.parentElement;
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
                if (target === instance.currentTarget) {
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

            var targetPosition = target.getAttribute(instance.positionAttribute) || instance.position;
            this.positionTooltip(instance, target, targetPosition);
        },

        positionTooltip: function(instance, target, positionOverride) {
            var pos = positionOverride || instance.position || 'top';
            var rect = target.getBoundingClientRect();
            instance.tooltipEl.style.visibility = 'hidden';
            instance.tooltipEl.style.display = 'block';
            var tooltipRect = instance.tooltipEl.getBoundingClientRect();
            instance.tooltipEl.style.visibility = 'visible';

            var left, top;

            if (pos === 'left') {
                left = rect.left - tooltipRect.width - 8;
                top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
            } else if (pos === 'bottom') {
                left = rect.left;
                top = rect.bottom + 4;
            } else {
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
                top = rect.top - tooltipRect.height - 6;
                if (top < 5) {
                    top = rect.bottom + 6;
                }
            }

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

            if (instance.hideTimerId) {
                clearTimeout(instance.hideTimerId);
                instance.hideTimerId = null;
            }

            instance.isLocked = true;
            instance.currentTarget = target;
            instance.tooltipEl.textContent = text;
            instance.tooltipEl.style.opacity = '1';
            instance.tooltipEl.style.visibility = 'visible';

            this.positionTooltip(instance, target, alignment);

            var self = this;
            instance.hideTimerId = setTimeout(function() {
                instance.tooltipEl.style.opacity = '0';
                instance.tooltipEl.style.visibility = 'hidden';
                instance.currentTarget = null;
                setTimeout(function() {
                    instance.isLocked = false;
                }, 300);
            }, duration);
        },

        hideImmediate: function(instance) {
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
