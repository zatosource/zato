var AIChatTooltip = {

    tooltip: null,
    currentTarget: null,
    hideTimerId: null,

    init: function() {
        if (this.tooltip) return;

        this.tooltip = document.createElement('div');
        this.tooltip.className = 'ai-chat-hover-tooltip';
        document.body.appendChild(this.tooltip);

        this.attachEvents();
    },

    attachEvents: function() {
        var self = this;

        document.addEventListener('mouseenter', function(e) {
            var target = e.target;

            if (!target.hasAttribute || !target.hasAttribute('data-tooltip')) {
                return;
            }

            if (!target.closest('.ai-chat-widget')) {
                return;
            }

            if (self.isPopupOpen(target)) {
                return;
            }

            self.show(target);

            var timeout = target.getAttribute('data-tooltip-timeout');
            if (timeout) {
                self.hideTimerId = setTimeout(function() {
                    self.hide();
                }, parseInt(timeout, 10));
            }
        }, true);

        document.addEventListener('mouseleave', function(e) {
            var target = e.target;
            if (target.hasAttribute && target.hasAttribute('data-tooltip')) {
                self.hide();
            }
        }, true);
    },

    isPopupOpen: function(target) {
        if (target.classList.contains('zato-dropdown-trigger')) {
            var dropdown = target.closest('.zato-dropdown');
            if (dropdown && dropdown.classList.contains('open')) return true;
        }

        if (target.classList.contains('ai-chat-context-bar')) {
            var tooltip = target.querySelector('.ai-chat-context-tooltip.open');
            if (tooltip) return true;
        }

        if (target.classList.contains('ai-chat-convert-trigger')) {
            var convertTooltip = target.querySelector('.ai-chat-convert-tooltip.open');
            if (convertTooltip) return true;
        }

        return false;
    },

    show: function(target) {
        if (!this.tooltip) return;

        var text = target.getAttribute('data-tooltip');
        if (!text) return;

        this.currentTarget = target;
        this.tooltip.textContent = text;
        this.tooltip.style.opacity = '1';
        this.tooltip.style.visibility = 'visible';

        this.position(target);
    },

    position: function(target) {
        var rect = target.getBoundingClientRect();
        this.tooltip.style.visibility = 'hidden';
        this.tooltip.style.display = 'block';
        var tooltipRect = this.tooltip.getBoundingClientRect();
        this.tooltip.style.visibility = 'visible';

        var left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        var top = rect.top - tooltipRect.height - 6;

        if (left < 5) left = 5;
        if (left + tooltipRect.width > window.innerWidth - 5) {
            left = window.innerWidth - tooltipRect.width - 5;
        }

        this.tooltip.style.left = left + 'px';
        this.tooltip.style.top = top + 'px';
    },

    hide: function() {
        if (!this.tooltip) return;
        if (this.hideTimerId) {
            clearTimeout(this.hideTimerId);
            this.hideTimerId = null;
        }
        this.tooltip.style.opacity = '0';
        this.tooltip.style.visibility = 'hidden';
        this.currentTarget = null;
    }

};

document.addEventListener('DOMContentLoaded', function() {
    AIChatTooltip.init();
});
