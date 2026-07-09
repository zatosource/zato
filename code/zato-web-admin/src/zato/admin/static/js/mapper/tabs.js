
// Mapper kit - the tab strip.
// Click-to-activate tabs over a set of panels, with the selection
// remembered in browser storage across reloads. One instance drives
// the main page tabs, another the side Design-tab area.

(function($) {

    zato.mapper.tabs = {};

// ////////////////////////////////////////////////////////////////////////

    // Initializes one tab strip. Tab buttons match tabSelector and carry
    // data-tab, panels are resolved as '#' + panelPrefix + name.
    // tabsConfig:
    //   tabSelector: the selector the tab buttons match
    //   panelPrefix: the id prefix the panels resolve under
    //   activeClass: the class the active tab button carries
    //   storageKey:  browser storage key the selection is kept under
    //   defaultTab:  the tab shown when nothing is remembered
    // Returns {getTab, setTab}.
    zato.mapper.tabs.init = function(tabsConfig) {

        var tabSelector = tabsConfig.tabSelector;
        var panelPrefix = tabsConfig.panelPrefix;
        var activeClass = tabsConfig.activeClass;
        var storageKey = tabsConfig.storageKey;
        var currentTab = tabsConfig.defaultTab;

        // A remembered selection wins over the default, but only
        // when it still names an existing tab.
        var remembered = window.store.get(storageKey);
        if (remembered) {
            if ($(tabSelector + '[data-tab="' + remembered + '"]').length) {
                currentTab = remembered;
            }
        }

        function apply() {
            $(tabSelector).each(function() {
                var tabName = $(this).attr('data-tab');
                var isActive = tabName === currentTab;

                $(this).toggleClass(activeClass, isActive);
                $(this).attr('aria-selected', isActive ? 'true' : 'false');
                $('#' + panelPrefix + tabName).prop('hidden', !isActive);
            });
        }

        $(document).on('click', tabSelector, function() {
            currentTab = $(this).attr('data-tab');
            window.store.set(storageKey, currentTab);
            apply();
        });

        apply();

        return {
            getTab: function() {
                return currentTab;
            },
            setTab: function(tabName) {
                currentTab = tabName;
                window.store.set(storageKey, currentTab);
                apply();
            }
        };
    };

})(jQuery);
