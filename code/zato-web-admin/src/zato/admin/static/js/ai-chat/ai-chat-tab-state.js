(function() {
    'use strict';

    var AIChatTabState = {

        tabStates: {},
        attachmentCounter: 0,

        getState: function(tabId) {
            if (!this.tabStates[tabId]) {
                this.tabStates[tabId] = this.createDefaultState(tabId);
            }
            return this.tabStates[tabId];
        },

        createDefaultState: function(tabId) {
            return {
                tabId: tabId,
                model: null,
                attachments: [],
                tokensIn: 0,
                tokensOut: 0
            };
        },

        initTab: function(tabId) {
            if (!this.tabStates[tabId]) {
                this.tabStates[tabId] = this.createDefaultState(tabId);
            }
            return this.tabStates[tabId];
        },

        removeTab: function(tabId) {
            delete this.tabStates[tabId];
        },

        getModel: function(tabId) {
            var state = this.getState(tabId);
            return state.model;
        },

        setModel: function(tabId, modelId) {
            var state = this.getState(tabId);
            state.model = modelId;
        },

        getAttachments: function(tabId) {
            var state = this.getState(tabId);
            return state.attachments;
        },

        addAttachment: function(tabId, attachment) {
            var state = this.getState(tabId);
            var existingIndex = -1;
            for (var i = 0; i < state.attachments.length; i++) {
                if (state.attachments[i].name === attachment.name) {
                    existingIndex = i;
                    break;
                }
            }
            if (existingIndex >= 0) {
                state.attachments[existingIndex] = attachment;
            } else {
                state.attachments.push(attachment);
            }
        },

        removeAttachment: function(tabId, attachmentId) {
            var state = this.getState(tabId);
            state.attachments = state.attachments.filter(function(a) {
                return a.id !== attachmentId;
            });
        },

        clearAttachments: function(tabId) {
            var state = this.getState(tabId);
            state.attachments = [];
        },

        createAttachmentFromPaste: function(tabId, pastedText) {
            this.attachmentCounter++;
            var preview = pastedText.substring(0, 30).replace(/\s+/g, ' ').trim();
            var name = preview ? preview + '...' : 'Attachment #' + this.attachmentCounter;

            var attachment = {
                id: 'paste-' + Date.now(),
                name: name,
                type: 'text/plain',
                size: pastedText.length,
                content: pastedText
            };

            this.addAttachment(tabId, attachment);
            return attachment;
        },

        createAttachmentFromFile: function(tabId, file, content) {
            this.attachmentCounter++;

            var attachment = {
                id: 'file-' + Date.now(),
                name: file.name,
                type: file.type || 'application/octet-stream',
                size: file.size,
                content: content
            };

            this.addAttachment(tabId, attachment);
            return attachment;
        },

        loadFromTabs: function(tabs) {
            for (var i = 0; i < tabs.length; i++) {
                var tab = tabs[i];
                if (!this.tabStates[tab.id]) {
                    this.tabStates[tab.id] = this.createDefaultState(tab.id);
                }
                if (tab.model) {
                    this.tabStates[tab.id].model = tab.model;
                }
                if (tab.attachments) {
                    this.tabStates[tab.id].attachments = tab.attachments;
                }
                if (tab.tokensIn) {
                    this.tabStates[tab.id].tokensIn = tab.tokensIn;
                }
                if (tab.tokensOut) {
                    this.tabStates[tab.id].tokensOut = tab.tokensOut;
                }
            }
        },

        saveToTab: function(tab) {
            var state = this.getState(tab.id);
            tab.model = state.model;
            tab.attachments = state.attachments;
            tab.tokensIn = state.tokensIn;
            tab.tokensOut = state.tokensOut;
        },

        getTokensIn: function(tabId) {
            var state = this.getState(tabId);
            return state.tokensIn || 0;
        },

        getTokensOut: function(tabId) {
            var state = this.getState(tabId);
            return state.tokensOut || 0;
        },

        addTokensIn: function(tabId, count) {
            var state = this.getState(tabId);
            state.tokensIn = (state.tokensIn || 0) + count;
        },

        addTokensOut: function(tabId, count) {
            var state = this.getState(tabId);
            state.tokensOut = (state.tokensOut || 0) + count;
        },

        humanizeNumber: function(num) {
            if (num >= 1000000) {
                return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
            }
            if (num >= 1000) {
                return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
            }
            return num.toString();
        }
    };

    window.AIChatTabState = AIChatTabState;

})();
