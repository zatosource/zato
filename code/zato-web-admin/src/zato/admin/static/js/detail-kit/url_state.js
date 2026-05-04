
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.url_state = {};

    kit.url_state.get = function(key, fallback) {
        var params = new URLSearchParams(window.location.search);
        return params.has(key) ? params.get(key) : (fallback || null);
    };

    kit.url_state.get_all = function(key) {
        var params = new URLSearchParams(window.location.search);
        return params.getAll(key);
    };

    kit.url_state.set = function(updates) {
        var params = new URLSearchParams(window.location.search);
        for (var key in updates) {
            if (!updates.hasOwnProperty(key)) continue;
            var val = updates[key];
            if (val === null || val === undefined || val === '') {
                params.delete(key);
            } else {
                params.set(key, val);
            }
        }
        var qs = params.toString();
        var new_url = window.location.pathname + (qs ? '?' + qs : '');
        history.pushState(null, '', new_url);
    };

    kit.url_state.set_list = function(key, values) {
        var params = new URLSearchParams(window.location.search);
        params.delete(key);
        for (var idx = 0; idx < values.length; idx++) {
            params.append(key, values[idx]);
        }
        var qs = params.toString();
        var new_url = window.location.pathname + (qs ? '?' + qs : '');
        history.pushState(null, '', new_url);
    };

    /* Register a callback for the browser back/forward button.
       The callback receives the full URLSearchParams from the restored URL.
       Multiple calls add multiple listeners (idempotent per callback). */
    kit.url_state.on_pop = function(callback) {
        window.addEventListener('popstate', function() {
            if (typeof callback === 'function') {
                callback(new URLSearchParams(window.location.search));
            }
        });
    };
})();
