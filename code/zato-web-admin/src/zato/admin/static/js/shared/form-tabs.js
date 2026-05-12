/*
 * Form tabs - reusable tab management for jQuery UI dialog forms.
 *
 * Works together with /static/css/shared/form-tabs.css and the
 * dashboard-kit tabs.js engine. This module provides a single
 * helper, $.fn.zato.form_tabs.reset(), which prepares a dialog's
 * tab strip before the dialog opens.
 *
 * ---------------------------------------------------------------
 * Why this exists
 * ---------------------------------------------------------------
 *
 * Zato edit/create dialogs are jQuery UI dialogs that start hidden.
 * The dashboard-kit tabs.init() must run after the dialog markup is
 * in the DOM but before the dialog is shown, so that the correct
 * tab is visible and aria attributes are set. Each page would
 * otherwise duplicate this boilerplate.
 *
 * ---------------------------------------------------------------
 * Usage
 * ---------------------------------------------------------------
 *
 * In your page JS, call reset() before opening the dialog:
 *
 *   $.fn.zato.form_tabs.reset({
 *       div_id:       '#create-div',
 *       panel_prefix: 'my-create-tab-panel-',
 *       tab_names:    ['main', 'routing', 'protocol'],
 *       default_tab:  'main'
 *   });
 *   $.fn.zato.data_table._create_edit('create', 'Title', null);
 *
 * Parameters:
 *   div_id       - jQuery selector for the dialog wrapper, e.g. '#create-div'
 *   panel_prefix - ID prefix for tab panels, e.g. 'my-create-tab-panel-'
 *                  Each panel must have id="<prefix><tab_name>"
 *   tab_labels   - Object mapping data-tab names to display labels,
 *                  e.g. {main: 'Main', dedup: 'Deduplication'}.
 *                  Keys define the tab order, values set button text.
 *                  This is the single source of truth for tab names.
 *   tab_names    - Optional array override; derived from tab_labels keys
 *                  when omitted.
 *   default_tab  - Which tab to activate on open (must be in tab_names)
 *   independent_tabs - If true, each tab is treated as an independent
 *                  form. Validation is only applied to the active tab's
 *                  fields; required markers on hidden tabs are suppressed
 *                  before submit and restored on tab switch.
 *
 * The function:
 *   1. Resets all tabs to inactive and hides all panels
 *   2. Activates the default tab and shows its panel
 *   3. Calls dashboard_kit.tabs.init() to wire up click handlers
 *   4. If independent_tabs is true, installs a before_submit_hook
 *      that suppresses validation on hidden tab panels
 */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.form_tabs === 'undefined') { $.fn.zato.form_tabs = {}; }

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.form_tabs._suppress_hidden_validation = function(form) {

    var required_attr = $.fn.zato.validate_required_attr;

    // Find all hidden tab panels inside this form ..
    form.find('.dashboard-tab-panel[hidden]').each(function() {

        // .. and strip required markers from their inputs, saving the original value.
        $(this).find('[' + required_attr + ']').each(function() {
            $(this).attr('data-zato-tab-suppressed', $(this).attr(required_attr));
            $(this).removeAttr(required_attr);
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.form_tabs._restore_hidden_validation = function(form) {

    // Restore any previously suppressed required markers
    form.find('[data-zato-tab-suppressed]').each(function() {
        $(this).attr($.fn.zato.validate_required_attr, $(this).attr('data-zato-tab-suppressed'));
        $(this).removeAttr('data-zato-tab-suppressed');
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.form_tabs._clear_hidden_panels = function(form) {

    // Collect IDs of inputs that are mirror targets - these must not be cleared
    // because they receive their value from the active tab's mirror input.
    var mirror_targets = {};
    form.find('.form-tab-mirror').each(function() {
        mirror_targets[$(this).attr('data-mirror-target')] = true;
    });

    // Clear all input values in hidden tab panels so they are not submitted.
    form.find('.dashboard-tab-panel[hidden]').each(function() {
        $(this).find('input[type="text"], input[type="hidden"], textarea').each(function() {
            if ($(this).hasClass('form-tab-mirror')) {
                return;
            }
            if (mirror_targets[$(this).attr('id')]) {
                return;
            }
            $(this).val('');
        });
        $(this).find('select').each(function() {
            $(this).prop('selectedIndex', 0);
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.form_tabs._init_mirrors = function(div_id) {

    // Mirror inputs (class form-tab-mirror) sync bi-directionally with a
    // target field specified by data-mirror-target (the id of the real input).
    $(div_id).find('.form-tab-mirror').each(function() {
        var $mirror = $(this);
        var target_id = $mirror.attr('data-mirror-target');
        var $target = $('#' + target_id);

        // Seed mirror from target
        $mirror.val($target.val());

        // Mirror -> target
        $mirror.on('input', function() {
            $target.val($mirror.val());
        });

        // Target -> mirror
        $target.on('input', function() {
            $mirror.val($target.val());
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.form_tabs.reset = function(config) {

    var div_id = config.div_id;
    var panel_prefix = config.panel_prefix;
    var tab_labels = config.tab_labels;
    var tab_names = config.tab_names || Object.keys(tab_labels);
    var default_tab = config.default_tab;
    var independent_tabs = config.independent_tabs || false;

    $(div_id + ' .dashboard-tab').each(function() {
        var tab_name = $(this).data('tab');
        var is_default = tab_name === default_tab;
        $(this).toggleClass('dashboard-tab-active', is_default);
        $(this).attr('aria-selected', is_default ? 'true' : 'false');
        if (tab_labels && tab_labels[tab_name]) {
            $(this).text(tab_labels[tab_name]);
        }
    });

    for (var i = 0; i < tab_names.length; i++) {
        var panel = document.getElementById(panel_prefix + tab_names[i]);
        if (panel) {
            panel.hidden = tab_names[i] !== default_tab;
        }
    }

    var caller_on_change = config.on_change || null;
    var on_change = null;
    var tab_focus = {};

    if (independent_tabs) {

        on_change = function(tab) {
            var form = $(div_id).find('form');
            $.fn.zato.form_tabs._restore_hidden_validation(form);
            $.fn.zato.form_tabs._suppress_hidden_validation(form);

            // Remember which field had focus in the panel we are leaving
            var focused = document.activeElement;
            if (focused) {
                var $panel = $(focused).closest('.dashboard-tab-panel');
                if ($panel.length) {
                    var leaving_tab = $panel.attr('id').replace(panel_prefix, '');
                    tab_focus[leaving_tab] = focused.id || null;
                }
            }

            // Restore focus in the panel we are entering
            var remembered = tab_focus[tab];
            if (remembered) {
                $('#' + remembered).focus();
            }
            else {
                var $active_panel = $('#' + panel_prefix + tab);
                var $first = $active_panel.find('input:visible, select:visible, textarea:visible').first();
                if ($first.length) {
                    $first.focus();
                }
            }

            if (caller_on_change) {
                caller_on_change(tab);
            }
        };

        // Install a before_submit_hook that suppresses hidden-tab validation
        // and clears values in hidden panels so they are not submitted.
        var previous_hook = $.fn.zato.data_table.before_submit_hook;

        $.fn.zato.data_table.before_submit_hook = function(form) {
            $.fn.zato.form_tabs._suppress_hidden_validation(form);
            $.fn.zato.form_tabs._clear_hidden_panels(form);
            if (previous_hook) {
                return previous_hook(form);
            }
            return true;
        };

        // .. and suppress right away for the initial state.
        var form = $(div_id).find('form');
        $.fn.zato.form_tabs._suppress_hidden_validation(form);
    }
    else if (caller_on_change) {
        on_change = caller_on_change;
    }

    // Initialize mirror fields that sync between tabs
    $.fn.zato.form_tabs._init_mirrors(div_id);

    $.fn.zato.dashboard_kit.tabs.init({
        tab_selector: div_id + ' .dashboard-tab',
        panel_prefix: panel_prefix,
        default_tab: default_tab,
        on_change: on_change,
        no_scroll_lock: true
    });

    // Focus the first visible input in the default tab panel
    var $default_panel = $('#' + panel_prefix + default_tab);
    var $first = $default_panel.find('input:visible, select:visible, textarea:visible').first();
    if ($first.length) {
        $first.focus();
    }
};
