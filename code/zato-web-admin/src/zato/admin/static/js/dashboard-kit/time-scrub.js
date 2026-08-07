

/* Dashboard kit - the time scrubber.
   A timestamp whose every part is a filter - clicking the day means that whole day,
   clicking the minute means that one minute. Each part is a link like any other on
   its page, wearing whatever the page dresses its links in, and a hovered part says
   what a click means in a small bubble below itself. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.time_scrub = {};

    kit.time_scrub.config = {

        css_class: 'dashboard-time-scrub',
        seg_class: 'dashboard-time-scrub-seg',

        /* The bubble a hovered part explains itself in - it lives on the body and is
           placed by hand, because the frames a stamp sits in clip what hangs below
           their last line. */
        bubble_class: 'dashboard-time-scrub-bubble',
        bubble_offset: 8,

        /* What clicking each part means, said in the bubble a hovered part shows
           below itself, so the first hover explains the whole mechanism. */
        hints: {
            'year': 'Filter to this year',
            'month': 'Filter to this month',
            'day': 'Filter to this day',
            'hour': 'Filter to this hour',
            'minute': 'Filter to this minute',
            'second': 'Filter to this second'
        },

        /* The stamp's own separators - what stands between the date parts, between
           the date and the time of day, and between the time-of-day parts. */
        date_separator: '-',
        date_time_separator: ' ',
        time_separator: ':',

        /* What a clicked window does is one page's affair - assigned in init. */
        on_pick: null
    };

    /* One part of a stamp, worn as the filter down to its own unit - a link like
       any other on its page. */
    kit.time_scrub.seg = function(unit, text) {
        var config = kit.time_scrub.config;

        var html = '<a href="javascript:void(0)" class="' + config.seg_class + '" data-unit="' + unit + '"';
        html += ' data-hint="' + config.hints[unit] + '">';
        html += kit._esc_html(text);
        html += '</a>';

        return html;
    };

    /* The frame the parts stand in, carrying the moment they all belong to -
       the click handler reads the moment off the frame rather than re-parsing
       whatever text the parts happen to show. */
    kit.time_scrub.container = function(time_iso, inner_html) {
        var config = kit.time_scrub.config;

        var html = '<span class="' + config.css_class + '" data-time-iso="' +
            kit._esc_html(time_iso) + '">' + inner_html + '</span>';

        return html;
    };

    /* The whole stamp, local time, every part scrubbable - year down to second,
       the fraction the event was written down with riding along on its own second,
       because the two are one moment and a click on either means that second. */
    kit.time_scrub.stamp = function(time_iso) {
        var config = kit.time_scrub.config;
        var moment = new Date(time_iso);

        var year = String(moment.getFullYear());
        var month = ('0' + (moment.getMonth() + 1)).slice(-2);
        var day = ('0' + moment.getDate()).slice(-2);
        var hour = ('0' + moment.getHours()).slice(-2);
        var minute = ('0' + moment.getMinutes()).slice(-2);
        var second = ('0' + moment.getSeconds()).slice(-2);

        var fraction = time_iso.match(/\.(\d+)/);

        if (fraction !== null) {
            second += '.' + fraction[1];
        }

        var inner = kit.time_scrub.seg('year', year);
        inner += config.date_separator;
        inner += kit.time_scrub.seg('month', month);
        inner += config.date_separator;
        inner += kit.time_scrub.seg('day', day);
        inner += config.date_time_separator;
        inner += kit.time_scrub.seg('hour', hour);
        inner += config.time_separator;
        inner += kit.time_scrub.seg('minute', minute);
        inner += config.time_separator;
        inner += kit.time_scrub.seg('second', second);

        return kit.time_scrub.container(time_iso, inner);
    };

    /* One local moment's date, written the way the log's own stamps are. */
    kit.time_scrub._format_date = function(moment) {
        var config = kit.time_scrub.config;

        var out = String(moment.getFullYear()) + config.date_separator +
            ('0' + (moment.getMonth() + 1)).slice(-2) + config.date_separator +
            ('0' + moment.getDate()).slice(-2);

        return out;
    };

    /* One local moment's time of day, in full down to the second. */
    kit.time_scrub._format_time = function(moment) {
        var config = kit.time_scrub.config;

        var out = ('0' + moment.getHours()).slice(-2) + config.time_separator +
            ('0' + moment.getMinutes()).slice(-2) + config.time_separator +
            ('0' + moment.getSeconds()).slice(-2);

        return out;
    };

    /* Whether a local moment stands at its own day's start - a window whose both
       edges do is a window of whole days and says nothing about the time of day. */
    kit.time_scrub._is_day_start = function(moment) {
        var out = moment.getHours() === 0 && moment.getMinutes() === 0 && moment.getSeconds() === 0;
        return out;
    };

    /* What a window reads back as, from its own two edges alone - so the same words
       come out of a click and out of an address bar being reloaded. Whole days read
       as dates - one day by its date, one month as "2026-08", one year as "2026".
       A window of time of day reads both edges out in full, the far edge as the last
       second still inside - "2026-08-07 10:00:00-10:59:59" - the date said once when
       both edges share it, and a single second as its own whole stamp. */
    kit.time_scrub.window_label = function(start, end) {
        var config = kit.time_scrub.config;

        var start_date = kit.time_scrub._format_date(start);

        // One second is its own whole label
        if (end.getTime() - start.getTime() === 1000) {
            return start_date + config.date_time_separator + kit.time_scrub._format_time(start);
        }

        // The far edge as the reader sees it - the last second still inside the window,
        // the poll's own edge staying exclusive as it is
        var last_inside = new Date(end.getTime() - 1000);
        var end_date = kit.time_scrub._format_date(last_inside);

        // Whole days carry no time of day worth writing out
        if (kit.time_scrub._is_day_start(start) && kit.time_scrub._is_day_start(end)) {

            // One day is its date
            if (end_date === start_date) {
                return start_date;
            }

            var is_month_start = start.getDate() === 1 && end.getDate() === 1;

            // One month says the year and the month, one year the year alone
            if (is_month_start) {
                var months_apart = (end.getFullYear() - start.getFullYear()) * 12 +
                    (end.getMonth() - start.getMonth());

                if (months_apart === 12 && start.getMonth() === 0) {
                    return String(start.getFullYear());
                }

                if (months_apart === 1) {
                    return String(start.getFullYear()) + config.date_separator +
                        ('0' + (start.getMonth() + 1)).slice(-2);
                }
            }

            // Any other run of days names its first and its last one
            return start_date + '-' + end_date;
        }

        var label = start_date + config.date_time_separator + kit.time_scrub._format_time(start) + '-';

        // A window inside one day says the day once - one crossing days names both in full
        if (end_date !== start_date) {
            label += end_date + config.date_time_separator;
        }

        label += kit.time_scrub._format_time(last_inside);

        return label;
    };

    /* The window one clicked unit means - the start of that local year, month, day,
       hour, minute or second up to the start of the next one, both written the way
       the log's own stamps are, UTC with the offset spelled out, and the label the
       window reads back as. */
    kit.time_scrub.window_of = function(time_iso, unit) {
        var moment = new Date(time_iso);

        var year = moment.getFullYear();
        var month = moment.getMonth();
        var day = moment.getDate();
        var hour = moment.getHours();
        var minute = moment.getMinutes();
        var second = moment.getSeconds();

        var start;
        var end;

        if (unit === 'year') {
            start = new Date(year, 0, 1);
            end = new Date(year + 1, 0, 1);
        }
        else if (unit === 'month') {
            start = new Date(year, month, 1);
            end = new Date(year, month + 1, 1);
        }
        else if (unit === 'day') {
            start = new Date(year, month, day);
            end = new Date(year, month, day + 1);
        }
        else if (unit === 'hour') {
            start = new Date(year, month, day, hour);
            end = new Date(year, month, day, hour + 1);
        }
        else if (unit === 'minute') {
            start = new Date(year, month, day, hour, minute);
            end = new Date(year, month, day, hour, minute + 1);
        }
        else {
            start = new Date(year, month, day, hour, minute, second);
            end = new Date(year, month, day, hour, minute, second + 1);
        }

        var out = {
            time_from: start.toISOString().replace('Z', '+00:00'),
            time_to: end.toISOString().replace('Z', '+00:00'),
            label: kit.time_scrub.window_label(start, end)
        };

        return out;
    };

    /* The one bubble on the screen, if any - a new hover replaces it rather than
       stacking another one on top. */
    kit.time_scrub._bubble = null;

    kit.time_scrub._show_bubble = function(element) {
        var config = kit.time_scrub.config;

        kit.time_scrub._hide_bubble();

        var bubble = document.createElement('div');
        bubble.className = config.bubble_class;
        bubble.textContent = element.getAttribute('data-hint');

        document.body.appendChild(bubble);

        // Below the part and centered on it - fixed placement, so no frame the
        // stamp sits in can clip the bubble away
        var rect = element.getBoundingClientRect();
        bubble.style.top = (rect.bottom + config.bubble_offset) + 'px';
        bubble.style.left = (rect.left + rect.width / 2) + 'px';

        kit.time_scrub._bubble = bubble;
    };

    kit.time_scrub._hide_bubble = function() {
        if (kit.time_scrub._bubble !== null) {
            kit.time_scrub._bubble.remove();
            kit.time_scrub._bubble = null;
        }
    };

    /* One set of handlers for every scrubber on the page - a clicked part names its
       unit, the frame it stands in names the moment, and what the window does with
       the page is the page's own affair. */
    kit.time_scrub.init = function(config) {
        var scrubConfig = kit.time_scrub.config;
        scrubConfig.on_pick = config.on_pick;

        $(document).on('mouseenter', '.' + scrubConfig.seg_class, function() {
            kit.time_scrub._show_bubble(this);
        });

        $(document).on('mouseleave', '.' + scrubConfig.seg_class, function() {
            kit.time_scrub._hide_bubble();
        });

        $(document).on('click', '.' + scrubConfig.seg_class, function(event) {

            // The stamp sits inside a clickable row - the click filters,
            // it does not also open the event under it
            event.preventDefault();
            event.stopPropagation();

            // The click redraws the page under the pointer, and no mouseleave
            // ever reaches a part that is gone
            kit.time_scrub._hide_bubble();

            var unit = $(this).attr('data-unit');
            var timeIso = $(this).closest('.' + scrubConfig.css_class).attr('data-time-iso');

            var picked = kit.time_scrub.window_of(timeIso, unit);

            scrubConfig.on_pick(picked, unit);
        });
    };
})();
