

/* Dashboard kit - the log line and the panel it collapses into.
   One record as one line of five slots - a stripe, something to read it by, a badge, the record
   itself and whatever can be done with it - and a shell that opens and closes under a line.
   What goes into each slot is the caller's business, the shape of the line is not. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.log_line = {};

    /* An attribute list out of a name-to-value object, in the order the object names them. */
    kit.log_line._attrs = function(attrs) {
        if (attrs === undefined) {
            return '';
        }

        var out = '';

        for (var name in attrs) {
            if (attrs.hasOwnProperty(name)) {
                out += ' ' + name + '="' + attrs[name] + '"';
            }
        }

        return out;
    };

    /* A style attribute, left out altogether by a slot that was given no style at all. */
    kit.log_line._style = function(style) {
        if (style === undefined) {
            return '';
        }

        return ' style="' + style + '"';
    };

    kit.log_line._classes = function(base, extra) {
        if (extra === undefined) {
            return base;
        }

        return base + ' ' + extra;
    };

    /* One line.
       parts:
         classes:        what this line is besides a log line, e.g. the mirror of a record
         attrs:          the attributes the line carries, e.g. which record it stands for
         style:          the style of the line itself, e.g. the rule under it
         stripe:         the colour of the stripe down its left edge
         lead_html:      what the line is read by - a time, a number, a link
         lead_style:     the style of that, left out when it wears the panel's own colour
         badge_html:     the badge beside it - a level, an outcome, a direction
         message_html:   the record itself
         message_style:  the style of that
         message_attrs:  the attributes of that, e.g. the raw text behind what is shown
         actions_html:   what can be done with the record */
    kit.log_line.render = function(parts) {
        var line_classes = kit.log_line._classes('detail-log-line', parts.classes);

        var html = '<div class="' + line_classes + '"' + kit.log_line._attrs(parts.attrs) +
            kit.log_line._style(parts.style) + '>';

        html += '<div class="detail-log-stripe" style="background:' + parts.stripe + '"></div>';
        html += '<div class="detail-log-ts"' + kit.log_line._style(parts.lead_style) + '>' +
            parts.lead_html + '</div>';
        html += '<div class="detail-log-level-col">' + parts.badge_html + '</div>';
        html += '<div class="detail-log-msg"' + kit.log_line._attrs(parts.message_attrs) +
            kit.log_line._style(parts.message_style) + '>' + parts.message_html + '</div>';
        html += '<div class="detail-log-actions">' + parts.actions_html + '</div>';
        html += '</div>';

        return html;
    };

    /* The shell one line opens into - a grid of a single row, collapsed by taking that row down
       to nothing, so opening and closing is one transition and nothing is ever measured.
       config:
         tag:        what the shell is, 'tr' for a panel under a table row and 'div' otherwise
         colspan:    how many cells it spans, for a shell that is a table row
         classes:    what this shell is besides a panel row
         attrs:      the attributes the shell carries, e.g. which record it belongs to
         is_framed:  whether the shell draws the dark frame itself - a shell already inside
                     one holds a plain body instead
         body_attrs: the attributes of what the shell holds
         body_html:  what it holds, empty for a shell filled in later */
    kit.log_line.panel = function(config) {
        var is_table_row = config.tag === 'tr';
        var panel_classes = kit.log_line._classes('detail-panel-row', config.classes);

        var html = '<' + config.tag + ' class="' + panel_classes + '"' + kit.log_line._attrs(config.attrs) + '>';

        if (is_table_row) {
            html += '<td colspan="' + config.colspan + '">';
        }

        html += '<div class="detail-panel-grid">';
        html += '<div class="detail-panel-inner">';

        var body_class = config.is_framed ? 'detail-panel-log' : 'detail-panel-body';

        html += '<div class="' + body_class + '"' + kit.log_line._attrs(config.body_attrs) + '>';

        if (config.body_html !== undefined) {
            html += config.body_html;
        }

        html += '</div>';
        html += '</div></div>';

        if (is_table_row) {
            html += '</td>';
        }

        html += '</' + config.tag + '>';

        return html;
    };
})();
