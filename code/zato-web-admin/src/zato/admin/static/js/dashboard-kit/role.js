

/* Dashboard kit - the role tag.
   The part a message plays in its exchange, said in words rather than drawn as an arrow -
   a request is the request whichever way it travelled, so the tag reads the same on a
   channel and on an outgoing connection. What makes a record a request or a reply is
   the caller's business - this only draws the answer. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.role = {};

    kit.role.config = {

        /* A record that is neither a request nor a reply is one the platform itself wrote
           down - an alert it raised, a message it expired - so it is marked as its own
           rather than left blank. */
        labels: {
            'request': 'REQ',
            'response': 'REPLY',
            'none': 'SYS'
        },

        css_classes: {
            'request': 'dashboard-role-request',
            'response': 'dashboard-role-response',
            'none': 'dashboard-role-none'
        },

        dark_class: 'dashboard-role-dark'
    };

    /* One role tag. The title is what the tag stands for in full, e.g. the event type
       the role was read out of. `variant` is 'dark' for a tag inside a dark frame and
       is left out everywhere else. */
    kit.role.tag = function(role, title, variant) {
        var config = kit.role.config;
        var classes = 'dashboard-role ' + config.css_classes[role];

        if (variant === 'dark') {
            classes += ' ' + config.dark_class;
        }

        var html = '<span class="' + classes + '"';
        html += ' title="' + kit._esc_html(title) + '">';
        html += config.labels[role];
        html += '</span>';

        return html;
    };
})();
