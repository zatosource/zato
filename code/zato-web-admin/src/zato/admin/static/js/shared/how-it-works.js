/*
 * "How does it work?" badge - hover tooltip, click-to-describe fields.
 *
 * On hover, shows a tippy explaining what the badge does.
 * On click, enters help mode: walks through form fields one by one,
 * showing a descriptive tooltip for each. Arrow keys navigate,
 * Esc or clicking the form background exits help mode.
 */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.how_it_works === 'undefined') { $.fn.zato.how_it_works = {}; }

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._state = null;

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works.init = function(config) {

    var badge = document.getElementById(config.badge_id);
    if (!badge) {
        return;
    }

    // .. destroy any previous hover tippy ..
    if (badge._tippy) {
        badge._tippy.destroy();
    }

    // .. attach hover tooltip ..
    tippy(badge, {
        content: 'Click to see a description<br>of each field in this form',
        allowHTML: true,
        placement: 'left',
        theme: 'dark',
        arrow: true,
        interactive: false,
        inertia: true,
        appendTo: function() { return badge.closest('.ui-dialog') || document.body; },
    });

    // .. store config for click handler ..
    badge._how_it_works_config = config;

    // .. bind click ..
    $(badge).off('click.how_it_works').on('click.how_it_works', function() {
        var current_state = $.fn.zato.how_it_works._state;
        if (current_state) {
            $.fn.zato.how_it_works._deactivate();
        }
        else {
            $.fn.zato.how_it_works._activate(badge);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._activate = function(badge) {

    var config = badge._how_it_works_config;
    var dialog = badge.closest('.ui-dialog');
    var div = document.getElementById(config.div_id.replace('#', ''));

    // .. collect visible fields from the active tab ..
    var fields = $.fn.zato.how_it_works._collect_fields(div, config);

    if (!fields.length) {
        return;
    }

    // .. hide the hover tippy ..
    if (badge._tippy) {
        badge._tippy.hide();
    }

    // .. set state ..
    var state = {
        badge: badge,
        config: config,
        dialog: dialog,
        div: div,
        fields: fields,
        current_index: 0,
        field_tippy: null,
    };

    $.fn.zato.how_it_works._state = state;

    // .. mark badge as depressed ..
    badge.classList.add('how-it-works-active');

    // .. show first field ..
    $.fn.zato.how_it_works._show_field_tooltip(state, 0);

    // .. bind keyboard ..
    $(document).on('keydown.how_it_works', function(event) {
        $.fn.zato.how_it_works._on_keydown(event);
    });

    // .. bind click on form background to dismiss ..
    $(div).on('click.how_it_works', function(event) {
        var target = event.target;
        var is_input = target.tagName === 'INPUT' || target.tagName === 'SELECT' || target.tagName === 'TEXTAREA';
        var is_label = target.tagName === 'LABEL';
        var is_badge = target.closest('.how-it-works-badge');
        var is_toggle = target.closest('.toggle-switch');

        if (!is_input && !is_label && !is_badge && !is_toggle) {
            $.fn.zato.how_it_works._deactivate();
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._deactivate = function() {

    var state = $.fn.zato.how_it_works._state;
    if (!state) {
        return;
    }

    // .. destroy current field tooltip ..
    if (state.field_tippy) {
        state.field_tippy.destroy();
    }

    // .. remove depressed look ..
    state.badge.classList.remove('how-it-works-active');

    // .. unbind ..
    $(document).off('keydown.how_it_works');
    $(state.div).off('click.how_it_works');

    $.fn.zato.how_it_works._state = null;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._on_keydown = function(event) {

    var state = $.fn.zato.how_it_works._state;
    if (!state) {
        return;
    }

    if (event.key === 'Escape') {
        event.preventDefault();
        event.stopPropagation();
        $.fn.zato.how_it_works._deactivate();
        return;
    }

    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
        event.preventDefault();
        var next = state.current_index + 1;
        if (next < state.fields.length) {
            $.fn.zato.how_it_works._show_field_tooltip(state, next);
        }
        return;
    }

    if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
        event.preventDefault();
        var prev = state.current_index - 1;
        if (prev >= 0) {
            $.fn.zato.how_it_works._show_field_tooltip(state, prev);
        }
        return;
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._show_field_tooltip = function(state, index) {

    // .. destroy previous tooltip ..
    if (state.field_tippy) {
        state.field_tippy.destroy();
    }

    state.current_index = index;
    var field = state.fields[index];

    // .. find the target element to anchor the tooltip to ..
    var target = field.element;

    var result = tippy(target, {
        content: field.description,
        allowHTML: true,
        placement: 'left',
        theme: 'dark',
        arrow: true,
        interactive: false,
        inertia: true,
        trigger: 'manual',
        hideOnClick: false,
        appendTo: function() { return state.dialog || document.body; },
    });

    // .. tippy returns an instance for a single element, an array for multiple ..
    state.field_tippy = Array.isArray(result) ? result[0] : result;
    state.field_tippy.show();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._collect_fields = function(div, config) {

    var descriptions = config.descriptions || {};
    var fields = [];

    // .. find the active tab panel ..
    var panels = div.querySelectorAll('.dashboard-tab-panel');
    var active_panel = null;

    for (var panel_index = 0; panel_index < panels.length; panel_index++) {
        if (!panels[panel_index].hidden) {
            active_panel = panels[panel_index];
            break;
        }
    }

    if (!active_panel) {
        return fields;
    }

    // .. walk each row in the form table ..
    var rows = active_panel.querySelectorAll('table.form-data tr');

    for (var row_index = 0; row_index < rows.length; row_index++) {
        var label = rows[row_index].querySelector('label[for]');
        if (!label) {
            continue;
        }

        var field_id = label.getAttribute('for');
        var description = descriptions[field_id];
        if (!description) {
            continue;
        }

        var target = label;

        fields.push({
            element: target,
            description: description,
        });
    }

    return fields;
};
