

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
       with the fraction the event was written down with following as plain text,
       because no two moments share it and a filter by it would be a filter by one row. */
    kit.time_scrub.stamp = function(time_iso) {
        var config = kit.time_scrub.config;
        var moment = new Date(time_iso);

        var year = String(moment.getFullYear());
        var month = ('0' + (moment.getMonth() + 1)).slice(-2);
        var day = ('0' + moment.getDate()).slice(-2);
        var hour = ('0' + moment.getHours()).slice(-2);
        var minute = ('0' + moment.getMinutes()).slice(-2);
        var second = ('0' + moment.getSeconds()).slice(-2);

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

        // The fraction is read, not clicked - it follows the scrubbable parts as it is
        var fraction = time_iso.match(/\.(\d+)/);

        if (fraction !== null) {
            inner += '.' + fraction[1];
        }

        return kit.time_scrub.container(time_iso, inner);
    };

    /* The window one clicked unit means - the start of that local year, month, day,
       hour, minute or second up to the start of the next one, both written the way
       the log's own stamps are, UTC with the offset spelled out, and the label the
       window reads back as, which is the local prefix down to the clicked unit. */
    kit.time_scrub.window_of = function(time_iso, unit) {
        var config = kit.time_scrub.config;
        var moment = new Date(time_iso);

        var year = moment.getFullYear();
        var month = moment.getMonth();
        var day = moment.getDate();
        var hour = moment.getHours();
        var minute = moment.getMinutes();
        var second = moment.getSeconds();

        var start;
        var end;
        var label;

        // Each label is the stamp cut off at the clicked unit, so the window reads
        // back exactly the way it was picked
        var date_label = String(year) + config.date_separator +
            ('0' + (month + 1)).slice(-2) + config.date_separator +
            ('0' + day).slice(-2);

        if (unit === 'year') {
            start = new Date(year, 0, 1);
            end = new Date(year + 1, 0, 1);
            label = String(year);
        }
        else if (unit === 'month') {
            start = new Date(year, month, 1);
            end = new Date(year, month + 1, 1);
            label = String(year) + config.date_separator + ('0' + (month + 1)).slice(-2);
        }
        else if (unit === 'day') {
            start = new Date(year, month, day);
            end = new Date(year, month, day + 1);
            label = date_label;
        }
        else if (unit === 'hour') {
            start = new Date(year, month, day, hour);
            end = new Date(year, month, day, hour + 1);
            label = date_label + config.date_time_separator + ('0' + hour).slice(-2);
        }
        else if (unit === 'minute') {
            start = new Date(year, month, day, hour, minute);
            end = new Date(year, month, day, hour, minute + 1);
            label = date_label + config.date_time_separator +
                ('0' + hour).slice(-2) + config.time_separator + ('0' + minute).slice(-2);
        }
        else {
            start = new Date(year, month, day, hour, minute, second);
            end = new Date(year, month, day, hour, minute, second + 1);
            label = date_label + config.date_time_separator +
                ('0' + hour).slice(-2) + config.time_separator +
                ('0' + minute).slice(-2) + config.time_separator + ('0' + second).slice(-2);
        }

        var out = {
            time_from: start.toISOString().replace('Z', '+00:00'),
            time_to: end.toISOString().replace('Z', '+00:00'),
            label: label
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
