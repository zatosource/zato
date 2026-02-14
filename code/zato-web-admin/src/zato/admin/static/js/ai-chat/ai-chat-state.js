(function() {
    'use strict';

    var STORAGE_KEY_TABS = 'zato.ai-chat.tabs';
    var STORAGE_KEY_ACTIVE_TAB = 'zato.ai-chat.active-tab';
    var STORAGE_KEY_POSITION = 'zato.ai-chat.position';
    var STORAGE_KEY_DIMENSIONS = 'zato.ai-chat.dimensions';
    var STORAGE_KEY_MINIMIZED = 'zato.ai-chat.minimized';
    var STORAGE_KEY_MAXIMIZED = 'zato.ai-chat.maximized';
    var STORAGE_KEY_PRE_MINIMIZE_POSITION = 'zato.ai-chat.pre-minimize-position';
    var STORAGE_KEY_PRE_MAXIMIZE_STATE = 'zato.ai-chat.pre-maximize-state';
    var STORAGE_KEY_ZOOM = 'zato.ai-chat.zoom';
    var STORAGE_KEY_CONFIG_MODE = 'zato.ai-chat.config-mode';

    var AIChatState = {

        loadTabs: function() {
            var tabsJson = localStorage.getItem(STORAGE_KEY_TABS);

            if (tabsJson) {
                try {
                    return JSON.parse(tabsJson);
                } catch (e) {
                }
            }
            return null;
        },

        saveTabs: function(tabs) {
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

            if (positionJson) {
                try {
                    return JSON.parse(positionJson);
                } catch (e) {
                }
            }
            return null;
        },

        savePosition: function(position) {
            localStorage.setItem(STORAGE_KEY_POSITION, JSON.stringify(position));
        },

        loadDimensions: function() {
            var dimensionsJson = localStorage.getItem(STORAGE_KEY_DIMENSIONS);

            if (dimensionsJson) {
                try {
                    return JSON.parse(dimensionsJson);
                } catch (e) {
                }
            }
            return null;
        },

        saveDimensions: function(dimensions) {
            localStorage.setItem(STORAGE_KEY_DIMENSIONS, JSON.stringify(dimensions));
        },

        loadMinimized: function() {
            var minimizedStr = localStorage.getItem(STORAGE_KEY_MINIMIZED);
            return minimizedStr === 'true';
        },

        saveMinimized: function(isMinimized) {
            localStorage.setItem(STORAGE_KEY_MINIMIZED, isMinimized.toString());
        },

        loadMaximized: function() {
            var maximizedStr = localStorage.getItem(STORAGE_KEY_MAXIMIZED);
            return maximizedStr === 'true';
        },

        saveMaximized: function(isMaximized) {
            localStorage.setItem(STORAGE_KEY_MAXIMIZED, isMaximized.toString());
        },

        loadPreMaximizeState: function() {
            var stateJson = localStorage.getItem(STORAGE_KEY_PRE_MAXIMIZE_STATE);
            if (stateJson) {
                try {
                    return JSON.parse(stateJson);
                } catch (e) {
                    return null;
                }
            }
            return null;
        },

        savePreMaximizeState: function(state) {
            localStorage.setItem(STORAGE_KEY_PRE_MAXIMIZE_STATE, JSON.stringify(state));
        },

        loadPreMinimizePosition: function() {
            var preMinPosJson = localStorage.getItem(STORAGE_KEY_PRE_MINIMIZE_POSITION);

            if (preMinPosJson) {
                try {
                    return JSON.parse(preMinPosJson);
                } catch (e) {
                }
            }
            return null;
        },

        savePreMinimizePosition: function(position) {
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
        },

        loadConfigMode: function() {
            return localStorage.getItem(STORAGE_KEY_CONFIG_MODE) || null;
        },

        saveConfigMode: function(configMode) {
            if (configMode) {
                localStorage.setItem(STORAGE_KEY_CONFIG_MODE, configMode);
            } else {
                localStorage.removeItem(STORAGE_KEY_CONFIG_MODE);
            }
        }
    };

    window.AIChatState = AIChatState;

})();
