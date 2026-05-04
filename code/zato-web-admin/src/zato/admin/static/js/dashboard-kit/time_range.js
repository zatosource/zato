
/* Dashboard kit - time-range pill menu.
   The "5m / 15m / 1h / ... All" drop-down that clamps the main chart's
   visible window. Selection is persisted to localStorage under the
   caller-supplied key. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var ns = $.fn.zato.dashboard_kit;
    ns.time_range = {};

    /* Initialise the time-range menu.
       config:
         pill:        selector for the pill trigger (click opens the menu)
         menu:        selector for the .dashboard-time-range-menu container
         option_cls:  class applied to each .dashboard-time-range-option
         active_cls:  class applied to the currently selected option
         storage_key: localStorage key used to remember the selection
         on_change:   callback(minutes) fired after a new option is picked
       Returns the handle {get_minutes, set_minutes}. */
    ns.time_range.init = function(config) {
        var $menu = $(config.menu);
        var $pill = $(config.pill);
        var active_cls = config.active_cls || 'dashboard-time-range-active';
        var open_cls = 'dashboard-time-range-menu-open';
        var option_sel = '.' + (config.option_cls || 'dashboard-time-range-option');

        var stored_minutes = parseInt(ns.storage_get(config.storage_key) || '0', 10);
        if (isNaN(stored_minutes)) stored_minutes = 0;

        $menu.find(option_sel).removeClass(active_cls);
        $menu.find(option_sel + '[data-minutes="' + stored_minutes + '"]').addClass(active_cls);

        $pill.on('click', function(event) {
            event.stopPropagation();
            $menu.toggleClass(open_cls);
        });

        $menu.on('click', option_sel, function(event) {
            event.stopPropagation();
            var minutes = parseInt($(this).data('minutes'), 10);
            if (isNaN(minutes)) minutes = 0;
            stored_minutes = minutes;
            ns.storage_set(config.storage_key, String(minutes));
            $menu.find(option_sel).removeClass(active_cls);
            $(this).addClass(active_cls);
            $menu.removeClass(open_cls);
            if (typeof config.on_change === 'function') {
                config.on_change(minutes);
            }
        });

        $(document).on('click', function() {
            $menu.removeClass(open_cls);
        });

        return {
            get_minutes: function() { return stored_minutes; },
            set_minutes: function(minutes) {
                stored_minutes = minutes;
                ns.storage_set(config.storage_key, String(minutes));
                $menu.find(option_sel).removeClass(active_cls);
                $menu.find(option_sel + '[data-minutes="' + minutes + '"]').addClass(active_cls);
            }
        };
    };

    /* Filter a timeline down to records whose `ts_accessor(record)` (in
       milliseconds) is within the last N minutes. N=0 means "no filter". */
    ns.time_range.filter_timeline = function(timeline, minutes, ts_accessor) {
        if (!minutes || minutes <= 0 || !timeline) {
            return timeline;
        }
        var cutoff = Date.now() - (minutes * 60 * 1000);
        var filtered = [];
        for (var i = 0; i < timeline.length; i++) {
            var ts = ts_accessor(timeline[i]);
            if (ts !== null && ts !== undefined && !isNaN(ts) && ts >= cutoff) {
                filtered.push(timeline[i]);
            }
        }
        return filtered;
    };
})();
