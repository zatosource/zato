/*
 * Form block hover highlight.
 *
 * Works together with /static/css/shared/form-highlight.css. On document
 * ready, every table.form-data is inspected - if it has at least
 * min_field_rows field rows, each such row is marked with the
 * form-highlight-row class and the CSS highlights the whole row on hover
 * or focus-within.
 *
 * A field row is a direct tr of the table that is visible (no .hidden
 * class and no inline display:none), contains a label and contains a
 * field widget - an input other than submit, button or hidden, a select,
 * a textarea or a nested table. Rows holding only OK and Cancel buttons,
 * message rows and hidden rows do not count and are not marked.
 *
 * Pages that show and hide rows dynamically can recount via
 * $.fn.zato.form_highlight.refresh().
 */

$.fn.zato.form_highlight.config = {
    min_field_rows: 3,
    row_class: 'form-highlight-row'
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.form_highlight._is_field_row = function($row) {

    // Hidden rows do not count - all popups are invisible at page load,
    // so visibility is checked via markers, not offsetParent.
    if ($row.hasClass('hidden')) {
        return false;
    }
    if ($row[0].style.display === 'none') {
        return false;
    }

    // A field row pairs a label with a field widget - submit and button
    // inputs mean an OK and Cancel row, hidden inputs carry no visible
    // field. A nested table also counts, e.g. the parameter editors on
    // the Request tab whose rows are only added dynamically.
    if (!$row.find('label').length) {
        return false;
    }
    var widgets = 'input:not([type=submit]):not([type=button]):not([type=hidden]), select, textarea, table';
    if (!$row.find(widgets).length) {
        return false;
    }

    return true;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.form_highlight.refresh = function() {

    var config = $.fn.zato.form_highlight.config;

    $('table.form-data').each(function() {

        // Only direct rows count - nested tables, e.g. parameter tables
        // inside a cell, must not qualify or be marked on their own.
        var $rows = $(this).children('tbody').children('tr');

        var $field_rows = $rows.filter(function() {
            return $.fn.zato.form_highlight._is_field_row($(this));
        });

        // Clear first so rows hidden since the last run lose the marker
        $rows.removeClass(config.row_class);

        if ($field_rows.length >= config.min_field_rows) {
            $field_rows.addClass(config.row_class);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $.fn.zato.form_highlight.refresh();
});
