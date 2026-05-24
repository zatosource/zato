
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.security === 'undefined') { $.fn.zato.security = {}; }
$.fn.zato.security.posture = {};

$.fn.zato.security.posture.config = {
    cluster_id: '1',
    poll_url: '/zato/security/posture/poll/',
    scan_url: '/zato/security/posture/scan/',
    save_url: '/zato/security/posture/save/',
    show_hero: false,
    show_chart: false,
    show_chart_controls: false
};

// ////////////////////////////////////////////////////////////////////////////
// State
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture._tab_handle = null;

// ////////////////////////////////////////////////////////////////////////////
// Check state management
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture._get_check_states = function() {
    var out = {};
    $('.posture-check-item input[type="checkbox"]').each(function() {
        var key = $(this).data('check');
        out[key] = $(this).is(':checked');
    });
    return out;
};

$.fn.zato.security.posture._set_check_states = function(states) {
    for (var key in states) {
        var $input = $('.posture-check-item input[data-check="' + key + '"]');
        if ($input.length) {
            $input.prop('checked', states[key]);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////////
// Actions
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture._save = function() {
    var ns = $.fn.zato.security.posture;
    var $btn = $('#posture-save');
    var $status = $('#posture-status');
    var states = ns._get_check_states();

    $btn.prop('disabled', true);
    $status.text('Saving...').removeClass('posture-status-saved posture-status-error');

    $.ajax({
        type: 'POST',
        url: ns.config.save_url,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        data: JSON.stringify(states),
        contentType: 'application/json',
        dataType: 'json',
        success: function() {
            $status.text('Saved').addClass('posture-status-saved');
            setTimeout(function() { $status.text(''); }, 2000);
        },
        error: function() {
            $status.text('Error saving').addClass('posture-status-error');
        },
        complete: function() {
            $btn.prop('disabled', false);
        }
    });
};

$.fn.zato.security.posture._run_scan = function() {
    var ns = $.fn.zato.security.posture;
    var $btn = $('#posture-run-scan');
    var $status = $('#posture-status');

    $btn.prop('disabled', true);
    $status.text('Scanning...').removeClass('posture-status-saved posture-status-error');

    $.ajax({
        type: 'POST',
        url: ns.config.scan_url,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        data: JSON.stringify(ns._get_check_states()),
        contentType: 'application/json',
        dataType: 'json',
        success: function(response) {
            var total = response.total_findings;
            $status.text('Scan complete - ' + total + ' finding' + (total === 1 ? '' : 's'));
            setTimeout(function() { $status.text(''); }, 4000);
        },
        error: function() {
            $status.text('Scan failed').addClass('posture-status-error');
        },
        complete: function() {
            $btn.prop('disabled', false);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////////
// Field descriptions for "How does it work?"
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture._field_descriptions = {

    'posture-toggle-auth-no-credentials':
        '<div class="hiw-posture-explanation">' +
            '<div class="hiw-posture-title">Channels without credentials</div>' +
            '<div class="hiw-posture-body">' +
                'Every REST channel in Zato can be protected by assigning a security definition to it, ' +
                'such as Basic Auth, API keys, or OAuth tokens.' +
                '<br><br>' +
                'When this check is enabled, the scanner looks at each REST channel and flags any that ' +
                '<span class="hiw-posture-highlight">do not have a security definition assigned</span>. ' +
                'A channel without credentials means that anyone who knows the URL can call it freely ' +
                'without any authentication.' +
                '<br><br>' +
                'This is often fine during development, but in production it can be a serious exposure. ' +
                'The check helps you spot these channels so you can decide whether to secure them or ' +
                'mark them as intentionally public.' +
            '</div>' +
            '<div class="hiw-posture-toggle">' +
                '<span class="hiw-posture-toggle-label">Toggle</span>' +
                '<label class="toggle-switch hiw-toggle-switch">' +
                    '<input type="checkbox" class="hiw-posture-toggle-input">' +
                    '<span class="toggle-slider"></span>' +
                '</label>' +
            '</div>' +
        '</div>'
};

// ////////////////////////////////////////////////////////////////////////////
// Initialization
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture.init = function(initial_data) {
    var ns = $.fn.zato.security.posture;
    var kit = $.fn.zato.dashboard_kit;

    // .. tabs
    ns._tab_handle = kit.tabs.init({
        tab_selector: '.posture-card .dashboard-tab',
        panel_prefix: 'posture-tab-panel-',
        storage_key: 'zato-posture-tab',
        default_tab: 'authentication'
    });

    // .. restore check states from server data
    if (initial_data.check_states) {
        ns._set_check_states(initial_data.check_states);
    }

    // .. clicking the text area toggles the slider
    $(document).on('click', '.posture-check-text', function() {
        var $item = $(this).closest('.posture-check-item');
        var $checkbox = $item.find('input[type="checkbox"]');
        $checkbox.prop('checked', !$checkbox.prop('checked'));
    });

    // .. save button
    $('#posture-save').on('click', function() {
        ns._save();
    });

    // .. scan button
    $('#posture-run-scan').on('click', function() {
        ns._run_scan();
    });

    // .. "How does it work?" badge
    $.fn.zato.how_it_works.init({
        badge_id: 'posture-how-it-works-badge',
        div_id: 'posture-card-container',
        container_selector: '.posture-card',
        field_selector: '.posture-check-item',
        target_selector: '.posture-check-name',
        placement: 'right',
        descriptions: ns._field_descriptions
    });

    // .. fade in
    kit.reveal();
};
