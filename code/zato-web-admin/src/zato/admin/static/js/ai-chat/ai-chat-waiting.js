(function() {
    'use strict';

    var waitingTexts = ['Working ..', 'Generating ..', 'In progress ..', 'Be right with you ..'];
    var cycleDuration = 4000;
    var idleThreshold = 100;
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
            console.log('[IDLE-TRACE] startIdleWatch called, tabId:', tabId, 'contentEl:', !!contentEl);
            if (this.idleTimers[tabId]) {
                console.log('[IDLE-TRACE] timer already exists for tabId:', tabId);
                return;
            }

            this.lastActivityTime[tabId] = Date.now();
            this.cyclingElements[tabId] = tabId;
            console.log('[IDLE-TRACE] set lastActivityTime and cyclingElements for tabId:', tabId);

            var self = this;
            this.idleTimers[tabId] = setInterval(function() {
                var now = Date.now();
                var lastActivity = self.lastActivityTime[tabId] || now;
                var idleTime = now - lastActivity;

                if (idleTime >= idleThreshold) {
                    console.log('[IDLE-TRACE] idle threshold reached, idleTime:', idleTime, 'calling showCyclingText');
                    self.showCyclingText(tabId);
                }
            }, 100);
            console.log('[IDLE-TRACE] interval started for tabId:', tabId);
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
            var messagesContainer = document.querySelector('.ai-chat-messages[data-tab-id="' + tabId + '"]');
            if (!messagesContainer) {
                return;
            }

            var streamingEl = messagesContainer.querySelector('.ai-chat-message.streaming');
            if (!streamingEl) {
                return;
            }

            var contentEl = streamingEl.querySelector('.ai-chat-message-content');
            if (!contentEl) {
                return;
            }

            var waitingEl = contentEl.querySelector('.ai-chat-waiting-indicator');
            if (!waitingEl) {
                waitingEl = document.createElement('span');
                waitingEl.className = 'ai-chat-waiting-indicator';
                waitingEl.innerHTML = '<span class="ai-chat-waiting-cursor">▋</span><span class="ai-chat-waiting-text"></span>';
                contentEl.appendChild(waitingEl);
            }

            var textEl = waitingEl.querySelector('.ai-chat-waiting-text');
            if (textEl && !textEl.textContent) {
                textEl.textContent = waitingTexts[0];
                this.startCycling(tabId, waitingEl.parentElement);
            }
        },

        hideCyclingText: function(tabId) {
            var messagesContainer = document.querySelector('.ai-chat-messages[data-tab-id="' + tabId + '"]');
            if (!messagesContainer) {
                return;
            }

            var streamingEl = messagesContainer.querySelector('.ai-chat-message.streaming');
            if (!streamingEl) {
                return;
            }

            var contentEl = streamingEl.querySelector('.ai-chat-message-content');
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
