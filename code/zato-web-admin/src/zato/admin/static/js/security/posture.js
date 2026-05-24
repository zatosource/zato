(function($) {

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.security === 'undefined') { $.fn.zato.security = {}; }
$.fn.zato.security.posture = {};

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
// Field descriptions for "How does it work?"
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture._fieldDescriptions = {

    'posture-toggle-auth-no-credentials':
        '<div class="how-it-works-posture-explanation">' +
            '<div class="how-it-works-posture-title">Channels without credentials</div>' +
            '<div class="how-it-works-posture-body">' +
                'Every REST channel can be protected by assigning a security definition, such as Basic Auth or API keys.' +
                '<br><br>' +
                'This check ' +
                '<span class="how-it-works-posture-highlight">flags any REST channels that do not have a security definition assigned</span>.' +
                '<br><br>' +
                'A channel without credentials means anyone who knows the URL can call it freely.' +
                '<br><br>' +
                'Often fine during development, but in production it can be a serious exposure.' +
                '<br><br>' +
                'The check helps you spot these channels so you can secure them or mark them as intentionally public.' +
            '</div>' +
            '<div class="how-it-works-posture-toggle">' +
                '<span class="how-it-works-posture-toggle-label">Toggle</span>' +
                '<label class="toggle-switch how-it-works-toggle-switch">' +
                    '<input type="checkbox" class="how-it-works-posture-toggle-input">' +
                    '<span class="toggle-slider"></span>' +
                '</label>' +
            '</div>' +
        '</div>',

    'posture-toggle-auth-weak-credentials':
        '<div class="how-it-works-posture-explanation">' +
            '<div class="how-it-works-posture-title">Weak passwords</div>' +
            '<div class="how-it-works-posture-body">' +
                'Security definitions in Zato store the credentials that clients use to authenticate. ' +
                'A password that is too short or too common can be guessed easily.' +
                '<br><br>' +
                'This check ' +
                '<span class="how-it-works-posture-highlight">measures the strength of every password in your security definitions</span>.' +
                '<br><br>' +
                'Strength is scored from 0 to 4:' +
                '<br>' +
                '0 or 1 - cracked almost instantly' +
                '<br>' +
                '2 - guessable with some effort' +
                '<br>' +
                '3 - safe' +
                '<br>' +
                '4 - very hard to crack' +
                '<br><br>' +
                'The scoring considers length, character variety, common patterns, and known breach lists.' +
            '</div>' +
            '<div class="how-it-works-posture-toggle">' +
                '<span class="how-it-works-posture-toggle-label">Toggle</span>' +
                '<label class="toggle-switch how-it-works-toggle-switch">' +
                    '<input type="checkbox" class="how-it-works-posture-toggle-input">' +
                    '<span class="toggle-slider"></span>' +
                '</label>' +
            '</div>' +
        '</div>',

    'posture-toggle-rate-limiting':
        '<div class="how-it-works-posture-explanation">' +
            '<div class="how-it-works-posture-title">Missing rate limiting</div>' +
            '<div class="how-it-works-posture-body">' +
                'Rate limiting controls how many requests a client can make in a given time window.' +
                '<br><br>' +
                'This check ' +
                '<span class="how-it-works-posture-highlight">finds REST channels and services that do not have any rate limiting configured</span>.' +
                '<br><br>' +
                'Without it, a single client can flood your server with requests.' +
                '<br><br>' +
                'Even a simple limit like 1,000 requests per minute protects against runaway loops and denial-of-service attempts.' +
            '</div>' +
            '<div class="how-it-works-posture-toggle">' +
                '<span class="how-it-works-posture-toggle-label">Toggle</span>' +
                '<label class="toggle-switch how-it-works-toggle-switch">' +
                    '<input type="checkbox" class="how-it-works-posture-toggle-input">' +
                    '<span class="toggle-slider"></span>' +
                '</label>' +
            '</div>' +
        '</div>',

    'posture-toggle-admin-services-exposed':
        '<div class="how-it-works-posture-explanation">' +
            '<div class="how-it-works-posture-title">Admin services exposed</div>' +
            '<div class="how-it-works-posture-body">' +
                'Zato has built-in admin services used by the dashboard and CLI.' +
                '<br><br>' +
                'They can create users, change passwords, deploy code, and read configuration.' +
                '<br><br>' +
                'This check ' +
                '<span class="how-it-works-posture-highlight">finds admin services mounted on channels reachable from outside the cluster</span>.' +
            '</div>' +
            '<div class="how-it-works-posture-toggle">' +
                '<span class="how-it-works-posture-toggle-label">Toggle</span>' +
                '<label class="toggle-switch how-it-works-toggle-switch">' +
                    '<input type="checkbox" class="how-it-works-posture-toggle-input">' +
                    '<span class="toggle-slider"></span>' +
                '</label>' +
            '</div>' +
        '</div>',

    'posture-toggle-internal-no-auth':
        '<div class="how-it-works-posture-explanation">' +
            '<div class="how-it-works-posture-title">Internal services without auth</div>' +
            '<div class="how-it-works-posture-body">' +
                'Some services are meant only for internal use - called by other services, scheduled jobs, or internal tooling.' +
                '<br><br>' +
                'This check ' +
                '<span class="how-it-works-posture-highlight">flags internal services that have a channel but no security definition protecting it</span>.' +
                '<br><br>' +
                'Without authentication, any process that can reach the channel URL can invoke the service.' +
            '</div>' +
            '<div class="how-it-works-posture-toggle">' +
                '<span class="how-it-works-posture-toggle-label">Toggle</span>' +
                '<label class="toggle-switch how-it-works-toggle-switch">' +
                    '<input type="checkbox" class="how-it-works-posture-toggle-input">' +
                    '<span class="toggle-slider"></span>' +
                '</label>' +
            '</div>' +
        '</div>'
};

// ////////////////////////////////////////////////////////////////////////
// Initialization
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture.init = function(initialData) {
    var posture = $.fn.zato.security.posture;
    var kit = $.fn.zato.dashboard_kit;

    // .. tabs
    posture._tabHandle = kit.tabs.init({
        tab_selector: '.posture-card .dashboard-tab',
        panel_prefix: 'posture-tab-panel-',
        storage_key: 'zato-posture-tab',
        default_tab: 'authentication'
    });

    // .. restore check states from server data
    if (initialData.checkStates) {
        posture._setCheckStates(initialData.checkStates);
    }

    // .. clicking the text area toggles the slider
    $(document).on('click', '.posture-check-text', function() {
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
        descriptions: posture._fieldDescriptions,
        inlineBadge: true,
        inlineBadgeRowSelector: '.posture-check-item',
        inlineBadgeAnchorSelector: '.posture-check-name-text'
    });

    // .. fade in
    kit.reveal();
};

})(jQuery);
