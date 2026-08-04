

/* Dashboard kit - the direction tag.
   Which way a message went, said in words rather than drawn as an arrow, so it reads
   the same at any size and in any font. What makes a record inbound or outbound is
   the caller's business - this only draws the answer. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.direction = {};

    kit.direction.config = {

        labels: {
            'in': 'IN',
            'out': 'OUT',
            'none': '\u2013'
        },

        css_classes: {
            'in': 'dashboard-direction-in',
            'out': 'dashboard-direction-out',
            'none': 'dashboard-direction-none'
        }
    };

    /* One direction tag. The title is what the tag stands for in full, e.g. the event type
       the direction was read out of. */
    kit.direction.tag = function(direction, title) {
        var config = kit.direction.config;

        var html = '<span class="dashboard-direction ' + config.css_classes[direction] + '"';
        html += ' title="' + kit._esc_html(title) + '">';
        html += config.labels[direction];
        html += '</span>';

        return html;
    };
})();
