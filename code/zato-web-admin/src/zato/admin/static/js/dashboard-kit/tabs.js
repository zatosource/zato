
/* Dashboard kit - tabbed activity card.
   Click-to-activate tabs with persistent selection and an aggressive
   scroll-lock that keeps the viewport pinned for ~300ms after each
   switch. This defeats Firefox's scroll-anchoring / focus-scroll-into-
   view behaviour that would otherwise jump the page on tab changes. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var ns = $.fn.zato.dashboard_kit;
    ns.tabs = {};

    var SCROLL_LOCK_MS = 300;

    /* Initialise a tab group.
       config:
         tab_selector:   jQuery selector matching each tab button
         panel_prefix:   element id prefix; "#<panel_prefix><tab_name>"
                         must resolve to the panel for tab data-tab=<tab_name>
         active_cls:     class applied to the active tab (default dashboard-tab-active)
         storage_key:    localStorage key used to remember the selection
         default_tab:    tab name to show on first visit
         on_change:      optional callback(new_tab_name)
       Returns {set_tab, get_tab}. */
    ns.tabs.init = function(config) {
        var active_cls = config.active_cls || 'dashboard-tab-active';
        var tab_selector = config.tab_selector;
        var panel_prefix = config.panel_prefix;
        var stored = config.storage_key ? ns.storage_get(config.storage_key) : null;
        var current_tab = stored || config.default_tab;
        var user_chose = false;

        var valid_tabs = {};
        $(tab_selector).each(function() { valid_tabs[$(this).data('tab')] = true; });
        if (!valid_tabs[current_tab]) {
            current_tab = config.default_tab;
        }

        var apply = function() {
            $(tab_selector).each(function() {
                var is_active = $(this).data('tab') === current_tab;
                $(this).toggleClass(active_cls, is_active);
                $(this).attr('aria-selected', is_active ? 'true' : 'false');
            });

            $(tab_selector).each(function() {
                var tab_name = $(this).data('tab');
                var $panel = $('#' + panel_prefix + tab_name);
                if ($panel.length) {
                    $panel.prop('hidden', tab_name !== current_tab);
                }
            });
        };

        /* Prevent the default focus behaviour that would make the browser
           scroll the clicked button into view. Keyboard activation (Space /
           Enter) still works via the click handler. */
        $(document).on('mousedown', tab_selector, function(event) {
            event.preventDefault();
        });

        $(document).on('click', tab_selector, function(event) {
            event.preventDefault();
            var tab = $(this).data('tab');
            current_tab = tab;
            user_chose = true;
            if (config.storage_key) { ns.storage_set(config.storage_key, tab); }

            /* Capture scroll, swap panels, then keep pinning the viewport
               back for SCROLL_LOCK_MS. Firefox commits its scroll-anchor
               adjustments a frame or two AFTER the click handler returns;
               a single scrollTo is not enough. */
            var scroll_x = window.pageXOffset || document.documentElement.scrollLeft || 0;
            var scroll_y = window.pageYOffset || document.documentElement.scrollTop || 0;
            try { this.blur(); } catch(e) {}

            var locking = true;
            var snap_back = function() {
                if (!locking) return;
                if (window.pageXOffset !== scroll_x || window.pageYOffset !== scroll_y) {
                    window.scrollTo(scroll_x, scroll_y);
                }
            };
            window.addEventListener('scroll', snap_back, true);

            apply();
            window.scrollTo(scroll_x, scroll_y);

            var deadline = Date.now() + SCROLL_LOCK_MS;
            var tick = function() {
                snap_back();
                if (Date.now() < deadline) {
                    window.requestAnimationFrame(tick);
                } else {
                    locking = false;
                    window.removeEventListener('scroll', snap_back, true);
                }
            };
            if (typeof window.requestAnimationFrame === 'function') {
                window.requestAnimationFrame(tick);
            } else {
                setTimeout(function() {
                    locking = false;
                    window.removeEventListener('scroll', snap_back, true);
                }, SCROLL_LOCK_MS);
            }

            if (typeof config.on_change === 'function') {
                config.on_change(tab);
            }
        });

        apply();

        return {
            get_tab: function() { return current_tab; },
            set_tab: function(tab, force) {
                if (!force && user_chose) return;
                current_tab = tab;
                apply();
            },
            user_chose: function() { return user_chose; }
        };
    };
})();
