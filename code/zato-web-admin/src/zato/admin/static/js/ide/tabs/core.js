(function() {
    'use strict';

    var ZatoIDETabs = {

        storageKeys: {
            tabs: 'zato.ide.tabs'
        },

        initTabs: function(instance) {
            if (typeof ZatoTabsManager === 'undefined') {
                return;
            }

            var tabsContainerId = instance.id + '-tabs';
            instance.tabsManager = ZatoTabsManager.create(tabsContainerId, {
                theme: instance.options.theme,
                onTabChange: function(tab) {
                    if (instance.onTabChange) {
                        instance.onTabChange(tab);
                    }
                }
            });

            var savedState = this.loadTabsState();
            var files;
            var activeTabId;

            if (savedState && savedState.tabs && savedState.tabs.length > 0) {
                files = savedState.tabs;
                activeTabId = savedState.activeTabId || files[0].id;
                instance.closedTabsHistory = savedState.closedTabsHistory || [];
                this.restoreFilesFromTabs(instance, files);
            } else {
                files = [];
                activeTabId = null;
                instance.closedTabsHistory = [];
            }

            instance.tabsManager.tabs = files;
            instance.tabsManager.activeTabId = activeTabId;
            instance.tabsManager.allowCloseLastTab = true;
            instance.tabsManager.container = document.getElementById(tabsContainerId);

            this.renderTabs(instance);
            this.bindTabEvents(instance);
        }
    };

    window.ZatoIDETabs = ZatoIDETabs;

})();
