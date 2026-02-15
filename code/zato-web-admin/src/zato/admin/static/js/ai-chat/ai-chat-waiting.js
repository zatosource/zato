(function() {
    'use strict';

    var waitingTexts = ['Working ..', 'Generating ..', 'In progress ..', 'Be right with you ..'];
    var cycleDuration = 4000;

    var AIChatWaiting = {

        intervals: {},

        buildWaitingHtml: function() {
            var html = '<span class="ai-chat-waiting-indicator">';
            html += '<span class="ai-chat-waiting-cursor">▋</span>';
            html += '<span class="ai-chat-waiting-text">' + waitingTexts[0] + '</span>';
            html += '</span>';
            return html;
        },

        startCycling: function(tabId, element) {
            if (this.intervals[tabId]) {
                return;
            }

            var textEl = element.querySelector('.ai-chat-waiting-text');
            if (!textEl) {
                return;
            }

            var index = 0;
            var self = this;

            this.intervals[tabId] = setInterval(function() {
                index = (index + 1) % waitingTexts.length;
                var el = element.querySelector('.ai-chat-waiting-text');
                if (el) {
                    el.textContent = waitingTexts[index];
                } else {
                    self.stopCycling(tabId);
                }
            }, cycleDuration);
        },

        stopCycling: function(tabId) {
            if (this.intervals[tabId]) {
                clearInterval(this.intervals[tabId]);
                delete this.intervals[tabId];
            }
        },

        stopAll: function() {
            for (var tabId in this.intervals) {
                this.stopCycling(tabId);
            }
        }
    };

    window.AIChatWaiting = AIChatWaiting;

})();
