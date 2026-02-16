(function() {
    'use strict';

    var waitingTexts = ['Working ..', 'Generating ..', 'In progress ..', 'Be right with you ..'];
    var cycleDuration = 4000;
    var idleThreshold = 2000;
    var minDisplayTime = 100;

    var AIChatWaiting = {

        intervals: {},
        idleTimers: {},
        lastActivityTime: {},
        cyclingElements: {},

        buildWaitingHtml: function() {
            var html = '<span class="ai-chat-waiting-indicator">';
            html += '<span class="ai-chat-waiting-cursor">▋</span>';
            html += '<span class="ai-chat-waiting-text"></span>';
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

            textEl.textContent = waitingTexts[0];
            this.cyclingElements[tabId] = element;

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
            delete this.cyclingElements[tabId];
        },

        stopAll: function() {
            for (var tabId in this.intervals) {
                this.stopCycling(tabId);
            }
            for (var tabId in this.idleTimers) {
                this.stopIdleWatch(tabId);
            }
        },

        recordActivity: function(tabId) {
            this.lastActivityTime[tabId] = Date.now();
            this.hideCyclingText(tabId);
        },

        startIdleWatch: function(tabId, contentEl) {
            if (this.idleTimers[tabId]) {
                return;
            }

            this.lastActivityTime[tabId] = Date.now();
            this.cyclingElements[tabId] = contentEl;

            var self = this;
            this.idleTimers[tabId] = setInterval(function() {
                var now = Date.now();
                var lastActivity = self.lastActivityTime[tabId] || now;
                var idleTime = now - lastActivity;

                if (idleTime >= idleThreshold) {
                    self.showCyclingText(tabId);
                }
            }, 500);
        },

        stopIdleWatch: function(tabId) {
            if (this.idleTimers[tabId]) {
                clearInterval(this.idleTimers[tabId]);
                delete this.idleTimers[tabId];
            }
            delete this.lastActivityTime[tabId];
            this.hideCyclingText(tabId);
            this.stopCycling(tabId);
        },

        showCyclingText: function(tabId) {
            var contentEl = this.cyclingElements[tabId];
            if (!contentEl) {
                return;
            }

            var waitingEl = contentEl.querySelector('.ai-chat-waiting-indicator');
            if (!waitingEl) {
                return;
            }

            var textEl = waitingEl.querySelector('.ai-chat-waiting-text');
            if (textEl && !textEl.textContent) {
                textEl.textContent = waitingTexts[0];
                this.startCycling(tabId, waitingEl.parentElement);
            }
        },

        hideCyclingText: function(tabId) {
            var contentEl = this.cyclingElements[tabId];
            if (!contentEl) {
                return;
            }

            var waitingEl = contentEl.querySelector('.ai-chat-waiting-indicator');
            if (!waitingEl) {
                return;
            }

            var textEl = waitingEl.querySelector('.ai-chat-waiting-text');
            if (textEl) {
                setTimeout(function() {
                    if (textEl) {
                        textEl.textContent = '';
                    }
                }, minDisplayTime);
            }
            this.stopCycling(tabId);
        }
    };

    window.AIChatWaiting = AIChatWaiting;

})();
