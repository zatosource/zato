(function() {
    'use strict';

    var waitingTexts = ['Working ..', 'Generating ..', 'In progress ..', 'Be right with you ..'];
    var codeTexts = ['Architecting ..', 'Designing ..', 'Composing ..', 'Generating code ..'];
    var codeTextFinal = 'Still generating code ..';
    var cycleDuration = 4000;
    var codeCycleDuration = 5000;
    var idleThreshold = 2000;
    var minDisplayTime = 100;

    var AIChatWaiting = {

        intervals: {},
        idleTimers: {},
        lastActivityTime: {},
        cyclingElements: {},
        codeMode: {},
        codeIndex: {},

        cyclingIndicatorHtml: '<span class="ai-chat-waiting-text"></span> <span class="ai-chat-waiting-cursor">▋</span>',

        buildWaitingHtml: function() {
            return '<span class="ai-chat-waiting-indicator"><span class="ai-chat-waiting-text">Waiting ..</span> <span class="ai-chat-waiting-cursor">▋</span></span>';
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
            delete this.codeMode[tabId];
            delete this.codeIndex[tabId];
        },

        startCodeCycling: function(tabId) {
            var self = this;
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

            this.stopCycling(tabId);
            this.codeMode[tabId] = true;
            this.codeIndex[tabId] = 0;

            var waitingEl = contentEl.querySelector('.ai-chat-waiting-indicator');
            if (!waitingEl) {
                waitingEl = document.createElement('span');
                waitingEl.className = 'ai-chat-waiting-indicator';
                waitingEl.innerHTML = this.cyclingIndicatorHtml;
                contentEl.appendChild(waitingEl);
            }

            var textEl = waitingEl.querySelector('.ai-chat-waiting-text');
            if (textEl) {
                textEl.textContent = codeTexts[0];
            }

            this.intervals[tabId] = setInterval(function() {
                var el = contentEl.querySelector('.ai-chat-waiting-indicator .ai-chat-waiting-text');
                if (!el) {
                    self.stopCycling(tabId);
                    return;
                }

                self.codeIndex[tabId]++;
                if (self.codeIndex[tabId] < codeTexts.length) {
                    el.textContent = codeTexts[self.codeIndex[tabId]];
                } else {
                    el.textContent = codeTextFinal;
                }
            }, codeCycleDuration);
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
            console.log('[SHOW-TRACE] showCyclingText called, tabId:', tabId);
            console.log('[SHOW-TRACE] intervals[tabId]:', !!this.intervals[tabId]);
            if (this.intervals[tabId]) {
                console.log('[SHOW-TRACE] early return - already has interval');
                return;
            }

            var messagesContainer = document.querySelector('.ai-chat-messages[data-tab-id="' + tabId + '"]');
            if (!messagesContainer) {
                console.log('[SHOW-TRACE] no messagesContainer');
                return;
            }

            var streamingEl = messagesContainer.querySelector('.ai-chat-message.streaming');
            if (!streamingEl) {
                console.log('[SHOW-TRACE] no streamingEl');
                return;
            }

            var contentEl = streamingEl.querySelector('.ai-chat-message-content');
            if (!contentEl) {
                console.log('[SHOW-TRACE] no contentEl');
                return;
            }

            var allWaiting = contentEl.querySelectorAll('.ai-chat-waiting-indicator');
            console.log('[SHOW-TRACE] allWaiting.length:', allWaiting.length);
            for (var i = 1; i < allWaiting.length; i++) {
                console.log('[SHOW-TRACE] removing duplicate waiting indicator at index:', i);
                allWaiting[i].remove();
            }

            var waitingEl = contentEl.querySelector('.ai-chat-waiting-indicator');
            console.log('[SHOW-TRACE] waitingEl exists:', !!waitingEl);
            if (!waitingEl) {
                waitingEl = document.createElement('span');
                waitingEl.className = 'ai-chat-waiting-indicator';
                waitingEl.innerHTML = this.cyclingIndicatorHtml;
                contentEl.appendChild(waitingEl);
                console.log('[SHOW-TRACE] created new waitingEl');
            }

            streamingEl.classList.add('hide-cursor');

            var textEl = waitingEl.querySelector('.ai-chat-waiting-text');
            console.log('[SHOW-TRACE] textEl exists:', !!textEl, 'textContent:', textEl ? textEl.textContent : 'N/A');
            if (textEl && !textEl.textContent) {
                textEl.textContent = waitingTexts[0];
                console.log('[SHOW-TRACE] set textContent to:', waitingTexts[0], 'calling startCycling');
                this.startCycling(tabId, waitingEl.parentElement);
            }
        },

        hideCyclingText: function(tabId) {
            console.log('[HIDE-TRACE] hideCyclingText called, tabId:', tabId);
            var messagesContainer = document.querySelector('.ai-chat-messages[data-tab-id="' + tabId + '"]');
            if (!messagesContainer) {
                console.log('[HIDE-TRACE] no messagesContainer');
                return;
            }

            var streamingEl = messagesContainer.querySelector('.ai-chat-message.streaming');
            if (!streamingEl) {
                console.log('[HIDE-TRACE] no streamingEl');
                return;
            }

            var contentEl = streamingEl.querySelector('.ai-chat-message-content');
            if (!contentEl) {
                console.log('[HIDE-TRACE] no contentEl');
                return;
            }

            var allWaiting = contentEl.querySelectorAll('.ai-chat-waiting-indicator');
            console.log('[HIDE-TRACE] allWaiting.length:', allWaiting.length);
            for (var i = 0; i < allWaiting.length; i++) {
                console.log('[HIDE-TRACE] removing waiting indicator at index:', i);
                allWaiting[i].remove();
            }

            streamingEl.classList.remove('hide-cursor');

            this.stopCycling(tabId);
        }
    };

    window.AIChatWaiting = AIChatWaiting;

})();
