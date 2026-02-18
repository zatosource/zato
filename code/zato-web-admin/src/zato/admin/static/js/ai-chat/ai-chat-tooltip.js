var AIChatTooltip = {

    tooltip: null,
    hideTimeout: null,
    currentTarget: null,

    init: function() {
        if (this.tooltip) return;

        this.tooltip = document.createElement('div');
        this.tooltip.className = 'ai-chat-hover-tooltip';
        document.body.appendChild(this.tooltip);

        this.attachEvents();
    },

    attachEvents: function() {
        var self = this;

        document.addEventListener('mouseover', function(e) {
            var target = e.target.closest('[data-tooltip]');
            if (target && target.closest('.ai-chat-widget')) {
                self.show(target);
            }
        });

        document.addEventListener('mouseout', function(e) {
            var target = e.target.closest('[data-tooltip]');
            if (target) {
                self.hide();
            }
        });
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
        var tooltipRect = this.tooltip.getBoundingClientRect();

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
        this.tooltip.style.opacity = '0';
        this.tooltip.style.visibility = 'hidden';
        this.currentTarget = null;
    },

    hideIfTarget: function(target) {
        if (this.currentTarget && (this.currentTarget === target || this.currentTarget.contains(target) || target.contains(this.currentTarget))) {
            this.hide();
        }
    }

};

document.addEventListener('DOMContentLoaded', function() {
    AIChatTooltip.init();
});
