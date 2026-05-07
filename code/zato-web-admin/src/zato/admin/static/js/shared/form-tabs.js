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
 *   tab_names    - Array of tab name strings matching data-tab attributes
 *   default_tab  - Which tab to activate on open (must be in tab_names)
 *
 * The function:
 *   1. Resets all tabs to inactive and hides all panels
 *   2. Activates the default tab and shows its panel
 *   3. Calls dashboard_kit.tabs.init() to wire up click handlers
 */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.form_tabs === 'undefined') { $.fn.zato.form_tabs = {}; }

$.fn.zato.form_tabs.reset = function(config) {

    var div_id = config.div_id;
    var panel_prefix = config.panel_prefix;
    var tab_names = config.tab_names;
    var default_tab = config.default_tab;

    $(div_id + ' .dashboard-tab').each(function() {
        var is_default = $(this).data('tab') === default_tab;
        $(this).toggleClass('dashboard-tab-active', is_default);
        $(this).attr('aria-selected', is_default ? 'true' : 'false');
    });

    for (var i = 0; i < tab_names.length; i++) {
        var panel = document.getElementById(panel_prefix + tab_names[i]);
        if (panel) {
            panel.hidden = tab_names[i] !== default_tab;
        }
    }

    $.fn.zato.dashboard_kit.tabs.init({
        tab_selector: div_id + ' .dashboard-tab',
        panel_prefix: panel_prefix,
        default_tab: default_tab
    });
};
