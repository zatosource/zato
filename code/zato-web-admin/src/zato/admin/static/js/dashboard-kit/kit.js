
/* Dashboard kit - root namespace and shared helpers.
   Provides formatters, time helpers and a small utility registry used
   by every component. Nothing in here knows about the scheduler, EDA,
   or any other concrete dashboard. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var kit = $.fn.zato.dashboard_kit;

    /* Compact number: 1234 -> "1.2K", 28937423 -> "29M". Single decimal
       when the integer part is a single digit so numbers stay short. */
    kit.format_number_compact = function(n) {
        if (n === null || n === undefined) return '-';
        var num = Number(n);
        if (!isFinite(num)) return String(n);
        var abs = Math.abs(num);
        var sign = num < 0 ? '-' : '';
        if (abs < 1000) {
            return sign + (Math.round(abs * 10) / 10);
        }
        var units = [
            {v: 1e12, s: 'T'},
            {v: 1e9,  s: 'B'},
            {v: 1e6,  s: 'M'},
            {v: 1e3,  s: 'K'}
        ];
        for (var i = 0; i < units.length; i++) {
            if (abs >= units[i].v) {
                var scaled = abs / units[i].v;
                var rendered = scaled >= 10
                    ? String(Math.round(scaled))
                    : (Math.round(scaled * 10) / 10).toFixed(1);
                return sign + rendered + units[i].s;
            }
        }
        return sign + String(abs);
    };

    /* Full thousands-separated form: 28937423 -> "28,937,423". Used as
       the authoritative display of a number in title= hover tooltips. */
    kit.format_number_full = function(n) {
        if (n === null || n === undefined) return '-';
        var num = Number(n);
        if (!isFinite(num)) return String(n);
        try {
            return num.toLocaleString('en-US');
        } catch(e) {
            var s = String(Math.trunc(num));
            var sign = '';
            if (s.charAt(0) === '-') { sign = '-'; s = s.substring(1); }
            return sign + s.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        }
    };

    kit.set_number = function($el, n) {
        var compact = kit.format_number_compact(n);
        var full = kit.format_number_full(n);
        $el.text(compact);
        if (compact === full) {
            $el.removeAttr('title');
        } else {
            $el.attr('title', full);
        }
    };

    kit.format_compact_duration = function(seconds) {
        if (seconds <= 0) return '0s';
        if (seconds < 60) return seconds + 's';
        if (seconds < 3600) {
            var mins = Math.floor(seconds / 60);
            var rem_s = seconds % 60;
            return rem_s > 0 ? mins + 'm ' + rem_s + 's' : mins + 'm';
        }
        if (seconds < 86400) {
            var hours = Math.floor(seconds / 3600);
            var rem_m = Math.floor((seconds % 3600) / 60);
            return rem_m > 0 ? hours + 'h ' + rem_m + 'm' : hours + 'h';
        }
        var days = Math.floor(seconds / 86400);
        var rem_h = Math.floor((seconds % 86400) / 3600);
        return rem_h > 0 ? days + 'd ' + rem_h + 'h' : days + 'd';
    };

    kit.format_ago = function(seconds) {
        if (seconds <= 0) return 'Now';
        return kit.format_compact_duration(seconds) + ' ago';
    };

    kit.format_duration_ms = function(duration_ms) {
        if (duration_ms === null || duration_ms === undefined || duration_ms === '') {
            return '-';
        }
        var ms = parseInt(duration_ms, 10);
        if (isNaN(ms)) {
            return '-';
        }
        if (ms < 1000) {
            return ms + ' ms';
        }
        if (ms < 60000) {
            return (ms / 1000).toFixed(1) + ' s';
        }
        return (ms / 60000).toFixed(1) + ' min';
    };

    kit.relative_time_future = function(iso_string) {
        if (!iso_string) return '-';
        var target = new Date(iso_string).getTime();
        var now = Date.now();
        var diff_seconds = Math.floor((target - now) / 1000);

        if (diff_seconds < 0) return 'Overdue';
        if (diff_seconds === 0) return 'Now';
        if (diff_seconds < 60) return 'In ' + diff_seconds + 's';
        if (diff_seconds < 3600) return 'In ' + Math.floor(diff_seconds / 60) + 'm';
        if (diff_seconds < 86400) return 'In ' + Math.floor(diff_seconds / 3600) + 'h';
        return 'In ' + Math.floor(diff_seconds / 86400) + 'd';
    };

    kit.relative_time_past = function(iso_string) {
        if (!iso_string) return '-';
        var target = new Date(iso_string).getTime();
        var now = Date.now();
        var diff_seconds = Math.floor((now - target) / 1000);

        if (diff_seconds < 0) diff_seconds = 0;
        if (diff_seconds < 60) return diff_seconds + 's ago';
        if (diff_seconds < 3600) return Math.floor(diff_seconds / 60) + 'm ago';
        if (diff_seconds < 86400) return Math.floor(diff_seconds / 3600) + 'h ago';
        return Math.floor(diff_seconds / 86400) + 'd ago';
    };

    kit.format_local_time = function(iso_string) {
        if (!iso_string) return '';
        var date = new Date(iso_string);
        var year = date.getFullYear();
        var month = ('0' + (date.getMonth() + 1)).slice(-2);
        var day = ('0' + date.getDate()).slice(-2);
        var hours = ('0' + date.getHours()).slice(-2);
        var minutes = ('0' + date.getMinutes()).slice(-2);
        var seconds = ('0' + date.getSeconds()).slice(-2);
        return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
    };

    /* Bucket `timeline` into `bucket_count` consecutive equal-width time
       slots ending at `now`, counting only records for which
       `predicate(record)` returns true. `ts_accessor(record)` must
       return the record's timestamp in milliseconds; a common accessor
       is `function(r){return new Date(r.actual_fire_time_iso).getTime();}`.
       Returns {series: [{ts, value} * bucket_count], total: N}. */
    kit.bucket_events_per_minute = function(timeline, predicate, ts_accessor, window_ms, bucket_count) {
        window_ms = window_ms || (60 * 60 * 1000);
        bucket_count = bucket_count || 60;
        var now = Date.now();
        var bucket_size = window_ms / bucket_count;
        var window_start = now - window_ms;

        var series = new Array(bucket_count);
        for (var b = 0; b < bucket_count; b++) {
            series[b] = {
                ts: window_start + (b + 1) * bucket_size,
                value: 0
            };
        }

        var total = 0;
        if (timeline) {
            for (var r = 0; r < timeline.length; r++) {
                var record = timeline[r];
                if (!predicate(record)) continue;
                var t_ms = ts_accessor(record);
                if (t_ms === null || t_ms === undefined || isNaN(t_ms)) continue;
                if (t_ms < window_start || t_ms > now) continue;
                var idx = Math.floor((t_ms - window_start) / bucket_size);
                if (idx < 0) idx = 0;
                if (idx >= bucket_count) idx = bucket_count - 1;
                series[idx].value++;
                total++;
            }
        }

        return {series: series, total: total};
    };

    /* Tiny localStorage wrapper that silently tolerates SecurityError
       (incognito with disabled storage, blocked by extensions, etc.). */
    kit.storage_get = function(key) {
        try { return localStorage.getItem(key); } catch(e) { return null; }
    };

    kit.storage_set = function(key, value) {
        try { localStorage.setItem(key, value); } catch(e) {}
    };

    kit.storage_get_json = function(key) {
        try {
            var raw = localStorage.getItem(key);
            return raw ? JSON.parse(raw) : null;
        } catch(e) {
            return null;
        }
    };

    kit.storage_set_json = function(key, value) {
        try { localStorage.setItem(key, JSON.stringify(value)); } catch(e) {}
    };
})();
