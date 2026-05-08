/*
 * "How does it work?" badge - hover tooltip, click-to-describe fields.
 *
 * On hover, shows a tippy explaining what the badge does.
 * On click, enters help mode: walks through form fields one by one,
 * showing a descriptive tooltip for each. Arrow keys navigate,
 * Esc deactivates help mode (does not close the form).
 * Clicking a label switches to that field's tooltip.
 * Clicking outside the form deactivates help mode.
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
        onShow: function() {
            if ($.fn.zato.how_it_works._state) {
                return false;
            }
        },
    });

    // .. store config for click handler ..
    badge._how_it_works_config = config;

    // .. bind click ..
    $(badge).off('click.how_it_works').on('click.how_it_works', function(event) {
        event.stopPropagation();
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
        last_index_per_tab: {},
        tab_observer: null,
    };

    $.fn.zato.how_it_works._state = state;

    // .. mark badge as depressed ..
    badge.classList.add('how-it-works-active');

    // .. show first field ..
    $.fn.zato.how_it_works._show_field_tooltip(state, 0);

    // .. suppress dialog closeOnEscape while help mode is active ..
    $(config.div_id).dialog('option', 'closeOnEscape', false);

    // .. bind keyboard on the dialog element in capture phase
    // .. so it fires before jQuery UI's own handler ..
    state._keydown_handler = function(event) {
        $.fn.zato.how_it_works._on_keydown(event);
    };
    dialog.addEventListener('keydown', state._keydown_handler, true);

    // .. bind click on labels to switch field ..
    $(div).on('click.how_it_works_label', 'label[for]', function(event) {
        event.stopPropagation();
        var field_id = $(this).attr('for');
        var field_index = $.fn.zato.how_it_works._find_field_index(state, field_id);
        if (field_index >= 0) {
            $.fn.zato.how_it_works._show_field_tooltip(state, field_index);
        }
    });

    // .. bind click on selects to switch field ..
    $(div).on('mousedown.how_it_works_select', 'select', function(event) {
        var field_id = this.id;
        var field_index = $.fn.zato.how_it_works._find_field_index_by_input(state, field_id);
        if (field_index >= 0 && field_index !== state.current_index) {
            $.fn.zato.how_it_works._show_field_tooltip(state, field_index);
        }
    });

    // .. follow focus to switch tooltip ..
    state._focusin_handler = function(event) {
        var row = event.target.closest('tr');
        if (!row) {
            return;
        }
        var label = row.querySelector('label[for]');
        if (!label) {
            return;
        }
        var field_index = $.fn.zato.how_it_works._find_field_index(state, label.getAttribute('for'));
        if (field_index >= 0 && field_index !== state.current_index) {
            $.fn.zato.how_it_works._show_field_tooltip(state, field_index);
        }
    };
    div.addEventListener('focusin', state._focusin_handler, true);

    // .. watch for tab switches via hidden attribute changes on panels ..
    var panels_container = div.querySelector('.dashboard-tab-panel');
    if (panels_container) {
        var parent_of_panels = panels_container.parentNode;
        state.tab_observer = new MutationObserver(function(mutation_list) {
            $.fn.zato.how_it_works._on_tab_switch(state);
        });
        state.tab_observer.observe(parent_of_panels, {
            attributes: true,
            attributeFilter: ['hidden'],
            subtree: true,
        });
    }

    // .. clicking outside the dialog closes help mode ..
    $(document).on('mousedown.how_it_works_outside', function(event) {
        if (!dialog.contains(event.target)) {
            $.fn.zato.how_it_works._deactivate();
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._on_tab_switch = function(state) {

    // .. save current index for the old tab ..
    var old_tab_name = $.fn.zato.how_it_works._get_active_tab_name(state.div);

    // .. re-collect fields from the newly active tab ..
    var new_fields = $.fn.zato.how_it_works._collect_fields(state.div, state.config);

    if (!new_fields.length) {
        if (state.field_tippy) {
            state.field_tippy.destroy();
            state.field_tippy = null;
        }
        state.fields = new_fields;
        return;
    }

    // .. destroy old tooltip ..
    if (state.field_tippy) {
        state.field_tippy.destroy();
        state.field_tippy = null;
    }

    state.fields = new_fields;

    // .. find the new active tab name ..
    var new_tab_name = $.fn.zato.how_it_works._get_active_tab_name(state.div);

    // .. restore last index for this tab, or start at 0 ..
    var restored_index = state.last_index_per_tab[new_tab_name];

    if (restored_index === undefined) {
        restored_index = 0;
    }

    if (restored_index >= new_fields.length) {
        restored_index = 0;
    }

    $.fn.zato.how_it_works._show_field_tooltip(state, restored_index);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._get_active_tab_name = function(div) {

    var buttons = div.querySelectorAll('.dashboard-tab-button');

    for (var button_index = 0; button_index < buttons.length; button_index++) {
        if (buttons[button_index].classList.contains('active')) {
            return buttons[button_index].textContent.trim();
        }
    }

    return '';
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

    // .. disconnect tab observer ..
    if (state.tab_observer) {
        state.tab_observer.disconnect();
    }

    // .. remove depressed look ..
    state.badge.classList.remove('how-it-works-active');

    // .. restore dialog closeOnEscape ..
    $(state.config.div_id).dialog('option', 'closeOnEscape', true);

    // .. unbind ..
    state.dialog.removeEventListener('keydown', state._keydown_handler, true);
    state.div.removeEventListener('focusin', state._focusin_handler, true);
    $(document).off('mousedown.how_it_works_outside');
    $(state.div).off('click.how_it_works_label');
    $(state.div).off('mousedown.how_it_works_select');

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

    // .. skip if already showing this field ..
    if (state.field_tippy && state.current_index === index) {
        return;
    }

    // .. destroy previous tooltip ..
    if (state.field_tippy) {
        state.field_tippy.destroy();
    }

    state.current_index = index;

    // .. remember this index for the current tab ..
    var tab_name = $.fn.zato.how_it_works._get_active_tab_name(state.div);
    state.last_index_per_tab[tab_name] = index;

    var field = state.fields[index];
    var target = field.element;

    var tooltip_content = field.description +
        '<div style="text-align:right;font-size:9px;font-family:monospace;opacity:0.7;margin-top:6px">' +
        'Esc, left arrow, right arrow</div>';

    var result = tippy(target, {
        content: tooltip_content,
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

    state.field_tippy = Array.isArray(result) ? result[0] : result;
    state.field_tippy.show();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._find_field_index = function(state, field_id) {

    for (var index = 0; index < state.fields.length; index++) {
        if (state.fields[index].element.getAttribute('for') === field_id) {
            return index;
        }
    }

    return -1;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._find_field_index_by_input = function(state, input_id) {

    // .. find which label points to this input ..
    for (var index = 0; index < state.fields.length; index++) {
        var label_for = state.fields[index].element.getAttribute('for');
        if (label_for === input_id) {
            return index;
        }
    }

    return -1;
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

        fields.push({
            element: label,
            description: description,
        });
    }

    return fields;
};
