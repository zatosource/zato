
/* Dashboard kit - auto-refresh pill menu.
   A configurable interval timer with a pill/dropdown UI that reuses
   the same visual style as the time-range selector. The caller supplies
   on_tick to do the actual data fetch. Selection persists to localStorage
   and (optionally) to the URL query string.

   Nothing in here knows about the scheduler, EDA, or any concrete page. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var ns = $.fn.zato.dashboard_kit;
    ns.auto_refresh = {};

    var INTERVALS = [
        {seconds: 0,   label: 'Off',        short_label: ''},
        {seconds: 5,   label: 'Every 5s',   short_label: '5s'},
        {seconds: 10,  label: 'Every 10s',  short_label: '10s'},
        {seconds: 15,  label: 'Every 15s',  short_label: '15s'},
        {seconds: 30,  label: 'Every 30s',  short_label: '30s'},
        {seconds: 60,  label: 'Every 1m',   short_label: '1m'},
        {seconds: 300, label: 'Every 5m',   short_label: '5m'},
        {seconds: 900, label: 'Every 15m',  short_label: '15m'},
        {seconds: 1800, label: 'Every 30m', short_label: '30m'}
    ];

    /* Initialise auto-refresh.
       config:
         pill:         selector for the toggle badge
         menu:         selector for the dropdown menu container
         storage_key:  localStorage key for persistence
         url_param:    query-string key (optional, e.g. 'refresh')
         on_tick:      callback() invoked every interval
         default_seconds: fallback if nothing stored (default 0 = off)
         intervals:    custom [{seconds, label}] (optional, defaults to INTERVALS)
       Returns handle: {start, stop, toggle, destroy, get_seconds, set_seconds} */
    ns.auto_refresh.init = function(config) {
        var intervals = config.intervals || INTERVALS;
        var $pill = $(config.pill);
        var $menu = $(config.menu);
        var open_cls = 'dashboard-time-range-menu-open';
        var active_cls = 'dashboard-time-range-active';
        var option_cls = 'dashboard-time-range-option';

        var timer_id = null;
        var current_seconds = 0;
        var paused = false;

        var url_param = config.url_param || null;
        var url_seconds = null;
        if (url_param && ns.url_state) {
            var raw = ns.url_state.get(url_param);
            if (raw !== null) url_seconds = parseInt(raw, 10);
        }

        if (url_seconds !== null && !isNaN(url_seconds)) {
            current_seconds = url_seconds;
        } else {
            current_seconds = config.default_seconds || 0;
        }

        var build_menu = function() {
            var html = '';
            for (var i = 0; i < intervals.length; i++) {
                var iv = intervals[i];
                var is_active = iv.seconds === current_seconds ? ' ' + active_cls : '';
                html += '<div class="' + option_cls + is_active + '" data-seconds="' + iv.seconds + '">' + iv.label + '</div>';
            }
            $menu.html(html);
        };

        var interval_short_label = function() {
            for (var i = 0; i < intervals.length; i++) {
                if (intervals[i].seconds === current_seconds) return intervals[i].short_label || '';
            }
            return current_seconds + 's';
        };

        var update_pill = function() {
            if (current_seconds > 0 && !paused) {
                $pill.text('Live \u00b7 ' + interval_short_label());
                $pill.removeClass('dashboard-refresh-badge-paused').addClass('dashboard-refresh-badge-live');
            } else {
                $pill.text('Paused');
                $pill.removeClass('dashboard-refresh-badge-live').addClass('dashboard-refresh-badge-paused');
            }
        };

        var clear_timer = function() {
            if (timer_id) {
                clearInterval(timer_id);
                timer_id = null;
            }
        };

        var start_timer = function() {
            clear_timer();
            if (current_seconds > 0 && !paused && typeof config.on_tick === 'function') {
                timer_id = setInterval(config.on_tick, current_seconds * 1000);
            }
        };

        var persist = function() {
            ns.storage_set(config.storage_key, String(current_seconds));
            if (url_param && ns.url_state) {
                var updates = {};
                updates[url_param] = current_seconds > 0 ? current_seconds : null;
                ns.url_state.set(updates);
            }
        };

        var apply_seconds = function(seconds) {
            current_seconds = seconds;
            paused = false;
            persist();
            build_menu();
            update_pill();
            start_timer();
        };

        var lock_width = function() {
            var longest = 'Paused';
            for (var i = 0; i < intervals.length; i++) {
                if (intervals[i].seconds > 0) {
                    var candidate = 'Live \u00b7 ' + (intervals[i].short_label || intervals[i].seconds + 's');
                    if (candidate.length > longest.length) longest = candidate;
                }
            }
            var span = document.createElement('span');
            var pill_cs = window.getComputedStyle($pill[0]);
            span.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;' +
                'font:' + pill_cs.font + ';letter-spacing:' + pill_cs.letterSpacing + ';' +
                'padding:0 ' + pill_cs.paddingRight + ' 0 ' + pill_cs.paddingLeft;
            span.textContent = longest;
            document.body.appendChild(span);
            var w = span.offsetWidth;
            document.body.removeChild(span);
            $pill.css({'min-width': w + 'px', 'text-align': 'center'});
        };

        build_menu();
        update_pill();
        lock_width();
        start_timer();

        $pill.on('click', function(event) {
            event.stopPropagation();
            $menu.toggleClass(open_cls);
        });

        $menu.on('click', '.' + option_cls, function(event) {
            event.stopPropagation();
            var seconds = parseInt($(this).data('seconds'), 10);
            if (isNaN(seconds)) seconds = 0;
            apply_seconds(seconds);
            $menu.removeClass(open_cls);
            if (seconds > 0 && typeof config.on_tick === 'function') {
                config.on_tick();
            }
        });

        $(document).on('click.auto_refresh', function() {
            $menu.removeClass(open_cls);
        });

        return {
            start: function() { paused = false; update_pill(); start_timer(); },
            stop: function() { paused = true; update_pill(); clear_timer(); },
            show_paused: function() { paused = true; update_pill(); },
            show_live: function() { paused = false; update_pill(); },
            toggle: function() {
                if (current_seconds > 0) {
                    paused = !paused;
                    update_pill();
                    if (paused) { clear_timer(); } else { start_timer(); }
                }
            },
            destroy: function() { clear_timer(); $pill.off(); $menu.off(); },
            get_seconds: function() { return current_seconds; },
            set_seconds: function(seconds) { apply_seconds(seconds); }
        };
    };

    /* Expose the default interval list for consumers that build
       custom menus or need to validate user input. */
    ns.auto_refresh.INTERVALS = INTERVALS;
})();
