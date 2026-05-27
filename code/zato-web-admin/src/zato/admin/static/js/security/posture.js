(function($) {

$.fn.zato.security.posture.config = {
    clusterId: '1',
    pollUrl: '/zato/security/posture/poll/',
    scanUrl: '/zato/security/posture/scan/',
    saveUrl: '/zato/security/posture/save/',
    showHero: false,
    showChart: false,
    showChartControls: false
};

// ////////////////////////////////////////////////////////////////////////
// State
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture._tabHandle = null;

// ////////////////////////////////////////////////////////////////////////
// Check state management
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture._getCheckStates = function() {
    var out = {};
    $('.posture-check-item input[type="checkbox"]').each(function() {
        var key = $(this).data('check');
        out[key] = $(this).is(':checked');
    });
    return out;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture._setCheckStates = function(states) {
    for (var key in states) {
        var $input = $('.posture-check-item input[data-check="' + key + '"]');
        if ($input.length) {
            $input.prop('checked', states[key]);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////
// Actions
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture._save = function() {
    var posture = $.fn.zato.security.posture;
    var $button = $('#posture-save');
    var $statusMessage = $('#posture-status');
    var states = posture._getCheckStates();

    $button.prop('disabled', true);
    $statusMessage.text('Saving...').removeClass('posture-status-saved posture-status-error');

    $.ajax({
        type: 'POST',
        url: posture.config.saveUrl,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        data: JSON.stringify(states),
        contentType: 'application/json',
        dataType: 'json',
        success: function() {
            $statusMessage.text('Saved').addClass('posture-status-saved');
            setTimeout(function() { $statusMessage.text(''); }, 2000);
        },
        error: function() {
            $statusMessage.text('Error saving').addClass('posture-status-error');
        },
        complete: function() {
            $button.prop('disabled', false);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture._runScan = function() {
    var posture = $.fn.zato.security.posture;
    var $button = $('#posture-run-scan');
    var $statusMessage = $('#posture-status');

    $button.prop('disabled', true);
    $statusMessage.text('Scanning...').removeClass('posture-status-saved posture-status-error');

    $.ajax({
        type: 'POST',
        url: posture.config.scanUrl,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        data: JSON.stringify(posture._getCheckStates()),
        contentType: 'application/json',
        dataType: 'json',
        success: function(response) {
            var totalFindings = response.total_findings;
            $statusMessage.text('Scan complete - ' + totalFindings + ' finding' + (totalFindings === 1 ? '' : 's'));
            setTimeout(function() { $statusMessage.text(''); }, 4000);
        },
        error: function() {
            $statusMessage.text('Scan failed').addClass('posture-status-error');
        },
        complete: function() {
            $button.prop('disabled', false);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////
// Initialization
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture.init = function(initialData) {
    var posture = $.fn.zato.security.posture;
    var kit = $.fn.zato.dashboard_kit;

    var fieldDescriptions = JSON.parse(document.getElementById('posture-field-descriptions').textContent);

    posture._tabHandle = kit.tabs.init({
        tab_selector: '.posture-card .dashboard-tab',
        panel_prefix: 'posture-tab-panel-',
        default_tab: kit.url_state.get('tab'),
        on_change: function(tabName) {
            kit.url_state.set({tab: tabName});
        }
    });

    // .. handle browser back/forward
    kit.url_state.on_pop(function(params) {
        var popTab = params.get('tab');
        if (popTab) {
            posture._tabHandle.set_tab(popTab, true);
        }
    });

    // .. restore check states from server data
    if (initialData.checkStates) {
        posture._setCheckStates(initialData.checkStates);
    }

    // .. clicking the text area toggles the slider, or jumps to the tooltip when help mode is active
    $(document).on('click', '.posture-check-text', function() {
        var howItWorks = $.fn.zato.how_it_works;
        var state = howItWorks._state;
        if (state) {
            var $item = $(this).closest('.posture-check-item');
            var fieldId = $item.find('label[for]').attr('for');
            var fieldIndex = howItWorks._findFieldIndex(state, fieldId);
            if (fieldIndex >= 0) {
                howItWorks._showFieldTooltip(state, fieldIndex);
            }
            return;
        }
        var $item = $(this).closest('.posture-check-item');
        var $checkbox = $item.find('input[type="checkbox"]');
        $checkbox.prop('checked', !$checkbox.prop('checked'));
    });

    // .. save button
    $('#posture-save').on('click', function() {
        posture._save();
    });

    // .. scan button
    $('#posture-run-scan').on('click', function() {
        posture._runScan();
    });

    // .. "How does it work?" badge
    $.fn.zato.how_it_works.init({
        badgeId: 'posture-how-it-works-badge',
        divId: 'posture-card-container',
        containerSelector: '.posture-card',
        fieldSelector: '.posture-check-item',
        targetSelector: '.posture-check-description',
        placement: 'right',
        descriptions: fieldDescriptions,
        inlineBadge: true,
        inlineBadgeRowSelector: '.posture-check-item',
        inlineBadgeAnchorSelector: '.posture-check-name-text'
    });

    // .. fade in
    kit.reveal();
};

})(jQuery);
