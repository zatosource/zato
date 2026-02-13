(function() {
    'use strict';

    var STORAGE_KEY_TABS = 'zato.llm-chat.tabs';
    var STORAGE_KEY_ACTIVE_TAB = 'zato.llm-chat.active-tab';
    var STORAGE_KEY_POSITION = 'zato.llm-chat.position';
    var STORAGE_KEY_DIMENSIONS = 'zato.llm-chat.dimensions';
    var STORAGE_KEY_MINIMIZED = 'zato.llm-chat.minimized';
    var STORAGE_KEY_PRE_MINIMIZE_POSITION = 'zato.llm-chat.pre-minimize-position';
    var STORAGE_KEY_ZOOM = 'zato.llm-chat.zoom';

    var LLMChatState = {

        loadTabs: function() {
            console.debug('LLMChatState.loadTabs: loading tabs from localStorage');
            var tabsJson = localStorage.getItem(STORAGE_KEY_TABS);

            if (tabsJson) {
                try {
                    return JSON.parse(tabsJson);
                } catch (e) {
                    console.debug('LLMChatState.loadTabs: failed to parse tabs');
                }
            }
            return null;
        },

        saveTabs: function(tabs) {
            console.debug('LLMChatState.saveTabs: saving tabs');
            localStorage.setItem(STORAGE_KEY_TABS, JSON.stringify(tabs));
        },

        loadActiveTabId: function() {
            return localStorage.getItem(STORAGE_KEY_ACTIVE_TAB);
        },

        saveActiveTabId: function(tabId) {
            localStorage.setItem(STORAGE_KEY_ACTIVE_TAB, tabId);
        },

        loadPosition: function() {
            var positionJson = localStorage.getItem(STORAGE_KEY_POSITION);
            console.debug('LLMChatState.loadPosition: positionJson:', positionJson);

            if (positionJson) {
                try {
                    return JSON.parse(positionJson);
                } catch (e) {
                    console.debug('LLMChatState.loadPosition: failed to parse position');
                }
            }
            return null;
        },

        savePosition: function(position) {
            console.debug('LLMChatState.savePosition: saving position:', JSON.stringify(position));
            localStorage.setItem(STORAGE_KEY_POSITION, JSON.stringify(position));
        },

        loadDimensions: function() {
            var dimensionsJson = localStorage.getItem(STORAGE_KEY_DIMENSIONS);
            console.debug('LLMChatState.loadDimensions: dimensionsJson:', dimensionsJson);

            if (dimensionsJson) {
                try {
                    return JSON.parse(dimensionsJson);
                } catch (e) {
                    console.debug('LLMChatState.loadDimensions: failed to parse dimensions');
                }
            }
            return null;
        },

        saveDimensions: function(dimensions) {
            console.debug('LLMChatState.saveDimensions: saving dimensions:', JSON.stringify(dimensions));
            localStorage.setItem(STORAGE_KEY_DIMENSIONS, JSON.stringify(dimensions));
        },

        loadMinimized: function() {
            var minimizedStr = localStorage.getItem(STORAGE_KEY_MINIMIZED);
            return minimizedStr === 'true';
        },

        saveMinimized: function(isMinimized) {
            localStorage.setItem(STORAGE_KEY_MINIMIZED, isMinimized.toString());
        },

        loadPreMinimizePosition: function() {
            var preMinPosJson = localStorage.getItem(STORAGE_KEY_PRE_MINIMIZE_POSITION);
            console.debug('LLMChatState.loadPreMinimizePosition: preMinPosJson:', preMinPosJson);

            if (preMinPosJson) {
                try {
                    return JSON.parse(preMinPosJson);
                } catch (e) {
                    console.debug('LLMChatState.loadPreMinimizePosition: failed to parse');
                }
            }
            return null;
        },

        savePreMinimizePosition: function(position) {
            console.debug('LLMChatState.savePreMinimizePosition:', JSON.stringify(position));
            localStorage.setItem(STORAGE_KEY_PRE_MINIMIZE_POSITION, JSON.stringify(position));
        },

        loadZoom: function() {
            var zoomStr = localStorage.getItem(STORAGE_KEY_ZOOM);
            if (zoomStr) {
                var zoom = parseFloat(zoomStr);
                if (!isNaN(zoom)) {
                    return zoom;
                }
            }
            return 1.0;
        },

        saveZoom: function(zoomScale) {
            localStorage.setItem(STORAGE_KEY_ZOOM, zoomScale.toString());
        }
    };

    window.LLMChatState = LLMChatState;

})();
