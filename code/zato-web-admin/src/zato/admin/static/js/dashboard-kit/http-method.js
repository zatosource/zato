

/* Dashboard kit - HTTP methods.
   An endpoint value like "POST https://..." reads better when the method wears its own
   ink - what asks is told apart from what changes and from what removes at a glance.
   A value that does not lead with a method comes back escaped and untouched. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.http_method = {};

    kit.http_method.config = {

        css_classes: {
            'GET': 'dashboard-method-get',
            'POST': 'dashboard-method-post',
            'PUT': 'dashboard-method-put',
            'PATCH': 'dashboard-method-patch',
            'DELETE': 'dashboard-method-delete',
            'HEAD': 'dashboard-method-head',
            'OPTIONS': 'dashboard-method-options'
        }
    };

    kit.http_method.html = function(value) {
        var config = kit.http_method.config;
        var space_at = value.indexOf(' ');

        // A value of one word is no method-and-address pair
        if (space_at === -1) {
            return kit._esc_html(value);
        }

        var method = value.slice(0, space_at);
        var css_class = config.css_classes[method];

        // A first word that is no HTTP method - a folder, a topic - is left as it stands
        if (css_class === undefined) {
            return kit._esc_html(value);
        }

        var rest = value.slice(space_at);

        var out = '<span class="dashboard-method ' + css_class + '">' + method + '</span>' +
            kit._esc_html(rest);

        return out;
    };
})();
