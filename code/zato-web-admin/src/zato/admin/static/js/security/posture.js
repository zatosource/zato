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

$.fn.zato.security.posture._makeDescription = function(title, body) {
    return '<div class="how-it-works-posture-explanation">' +
        '<div class="how-it-works-posture-title">' + title + '</div>' +
        '<div class="how-it-works-posture-body">' + body + '</div>' +
        '<div class="how-it-works-posture-toggle">' +
            '<span class="how-it-works-posture-toggle-label">Toggle</span>' +
            '<label class="toggle-switch how-it-works-toggle-switch">' +
                '<input type="checkbox" class="how-it-works-posture-toggle-input">' +
                '<span class="toggle-slider"></span>' +
            '</label>' +
        '</div>' +
    '</div>';
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture._buildFieldDescriptions = function() {
    var make = $.fn.zato.security.posture._makeDescription;
    var highlight = function(text) {
        return '<span class="how-it-works-posture-highlight">' + text + '</span>';
    };

    return {

        // .. authentication tab ..

        'posture-toggle-auth-no-credentials': make('Channels without credentials',
            'Every REST channel can be protected by assigning a security definition, such as Basic Auth or API keys.' +
            '<br><br>' +
            'This check ' + highlight('flags any REST channels that do not have a security definition assigned') + '.' +
            '<br><br>' +
            'A channel without credentials means anyone who knows the URL can call it freely.' +
            '<br><br>' +
            'Often fine during development, but in production it can be a serious exposure.' +
            '<br><br>' +
            'The check helps you spot these channels so you can secure them or mark them as intentionally public.'
        ),

        'posture-toggle-auth-weak-credentials': make('Weak passwords',
            'Security definitions in Zato store the credentials that clients use to authenticate.' +
            '<br><br>' +
            'This check ' + highlight('measures the strength of every password in your security definitions') + '.' +
            '<br><br>' +
            'Strength is scored from 0 to 4:' +
            '<br>0 or 1 - cracked almost instantly' +
            '<br>2 - guessable with some effort' +
            '<br>3 - safe' +
            '<br>4 - very hard to crack' +
            '<br><br>' +
            'The scoring considers length, character variety, common patterns, and known breach lists.'
        ),

        'posture-toggle-rate-limiting': make('Missing rate limiting',
            'Rate limiting controls how many requests a client can make in a given time window.' +
            '<br><br>' +
            'This check ' + highlight('finds REST channels and services that do not have any rate limiting configured') + '.' +
            '<br><br>' +
            'Without it, a single client can flood your server with requests.' +
            '<br><br>' +
            'Even a simple limit like 1,000 requests per minute protects against runaway loops and denial-of-service attempts.'
        ),

        'posture-toggle-admin-services-exposed': make('Admin services exposed',
            'Zato has built-in admin services used by the dashboard and CLI.' +
            '<br><br>' +
            'They can create users, change passwords, deploy code, and read configuration.' +
            '<br><br>' +
            'This check ' + highlight('finds admin services mounted on channels reachable from outside the cluster') + '.'
        ),

        'posture-toggle-internal-no-auth': make('Internal services without auth',
            'Some services are meant only for internal use - called by other services, scheduled jobs, or internal tooling.' +
            '<br><br>' +
            'This check ' + highlight('flags internal services that have a channel but no security definition protecting it') + '.' +
            '<br><br>' +
            'Without authentication, any process that can reach the channel URL can invoke the service.'
        ),

        // .. incoming channels tab (includes data protection checks) ..

        'posture-toggle-request-forgery': make('Request forgery risks',
            'If a service accepts a URL from a caller and uses it to make an outgoing request, an attacker can supply an internal URL instead.' +
            '<br><br>' +
            'This check ' + highlight('scans service code for patterns where user-supplied URLs are passed to outgoing connections') + '.' +
            '<br><br>' +
            'This lets the attacker reach internal systems that should not be accessible from outside.'
        ),

        'posture-toggle-unused-channels': make('Unused channels',
            'Channels that receive no traffic are easy to forget about.' +
            '<br><br>' +
            'This check ' + highlight('finds channels with no requests in the configured time window') + '.' +
            '<br><br>' +
            'Unused channels still accept connections, so removing or disabling them reduces the number of entry points into your system.'
        ),

        'posture-toggle-orphaned-services': make('Unattached services',
            'A service with no channel and no scheduled job cannot be invoked by external clients.' +
            '<br><br>' +
            'This check ' + highlight('detects services that have no channel or scheduled job attached') + '.' +
            '<br><br>' +
            'Unattached services may be leftover from earlier development or a sign of incomplete configuration.'
        ),

        // .. configuration tab ..

        'posture-toggle-debug-mode': make('Debug mode enabled',
            'Debug mode exposes detailed error messages, stack traces, and internal state to callers.' +
            '<br><br>' +
            'This check ' + highlight('warns if the server is running with debug or development settings') + '.' +
            '<br><br>' +
            'In production, debug output can reveal file paths, database queries, and internal logic to attackers.'
        ),

        'posture-toggle-plaintext-secrets': make('Plaintext secrets in config',
            'Configuration files can contain passwords, API tokens, and database credentials.' +
            '<br><br>' +
            'This check ' + highlight('scans configuration files for passwords and tokens stored in clear text') + '.' +
            '<br><br>' +
            'Secrets in plain text can be read by anyone with file system access or by accident through version control.'
        ),

        'posture-toggle-known-vulnerabilities': make('Known vulnerabilities',
            'Python packages can have publicly disclosed security flaws.' +
            '<br><br>' +
            'This check ' + highlight('compares installed packages against known CVE databases') + '.'
        ),

        'posture-toggle-tls-certificates': make('TLS certificates',
            'TLS certificates encrypt traffic and prove server identity.' +
            '<br><br>' +
            'This check ' + highlight('validates certificate chains and warns about upcoming expirations') + '.' +
            '<br><br>' +
            'An expired or misconfigured certificate causes outages and can expose traffic to interception.'
        ),

        // .. outgoing connections tab ..

        'posture-toggle-unencrypted-traffic': make('Unencrypted traffic',
            'Outgoing connections using plain HTTP send data without encryption.' +
            '<br><br>' +
            'This check ' + highlight('finds outgoing connections using HTTP instead of HTTPS') + '.' +
            '<br><br>' +
            'Unencrypted traffic can be intercepted by anyone on the network path between your server and the remote system.'
        ),

        'posture-toggle-missing-timeouts': make('Missing timeouts',
            'An outgoing connection without a timeout will wait indefinitely if the remote system stops responding.' +
            '<br><br>' +
            'This check ' + highlight('detects outgoing connections without timeout values set') + '.' +
            '<br><br>' +
            'Hanging connections consume resources and can eventually make the server unresponsive.'
        ),

        'posture-toggle-outgoing-cert-issues': make('Certificate issues',
            'Outgoing TLS connections rely on valid certificates to ensure traffic goes to the right destination.' +
            '<br><br>' +
            'This check ' + highlight('looks for expired, self-signed, or weak certificates on outgoing connections') + '.' +
            '<br><br>' +
            'A bad certificate means traffic may not be going where you think it is.'
        ),

        'posture-toggle-backend-no-auth': make('Backend connections without auth',
            'Outgoing connections to backend systems can be configured with authentication.' +
            '<br><br>' +
            'This check ' + highlight('finds outgoing connections with no authentication configured') + '.' +
            '<br><br>' +
            'Without credentials, anyone who can reach the same backend endpoint can use it.'
        ),

        'posture-toggle-backend-tls-version': make('Outdated TLS versions',
            'TLS 1.0 and 1.1 have known vulnerabilities and are deprecated.' +
            '<br><br>' +
            'This check ' + highlight('flags outgoing connections that allow TLS 1.0 or 1.1') + '.' +
            '<br><br>' +
            'All connections should use TLS 1.2 or newer.'
        ),

        'posture-toggle-backend-tls-ciphers': make('Weak TLS ciphers',
            'Some older cipher suites can be broken with modern hardware.' +
            '<br><br>' +
            'This check ' + highlight('detects outgoing connections using deprecated cipher suites') + '.' +
            '<br><br>' +
            'Weak ciphers make encrypted traffic vulnerable to decryption.'
        ),

        // .. runtime and data tab ..

        'posture-toggle-pii-detection': make('Personal data in responses',
            'API responses can accidentally include credit card numbers, national IDs, or other personal data.' +
            '<br><br>' +
            'This check ' + highlight('scans outgoing payloads for common PII patterns') + '.' +
            '<br><br>' +
            'Catching PII in responses helps prevent data leaks before they reach external consumers.'
        ),

        'posture-toggle-connection-string-leaks': make('Connection string leaks',
            'Database and broker connection strings contain hostnames, ports, and sometimes credentials.' +
            '<br><br>' +
            'This check ' + highlight('detects connection strings appearing in API responses') + '.' +
            '<br><br>' +
            'Leaking a connection string gives attackers a direct path to your internal infrastructure.'
        ),

        'posture-toggle-cumulative-data': make('Cumulative data exposure',
            'A single response may look harmless, but many small responses can add up to a full data set.' +
            '<br><br>' +
            'This check ' + highlight('tracks the total volume of sensitive fields returned per consumer over time') + '.' +
            '<br><br>' +
            'Monitoring cumulative exposure catches slow, distributed data exfiltration.'
        ),

        'posture-toggle-bulk-extraction': make('Bulk data extraction',
            'A single request that returns an unusually large response may indicate data scraping.' +
            '<br><br>' +
            'This check ' + highlight('detects responses with abnormally large payloads') + '.' +
            '<br><br>' +
            'Monitoring response sizes helps catch unauthorized bulk downloads early.'
        ),

        'posture-toggle-enumeration': make('Enumeration attempts',
            'Attackers probe APIs by trying sequential IDs to discover valid resources.' +
            '<br><br>' +
            'This check ' + highlight('watches for sequential ID probing and resource enumeration patterns') + '.' +
            '<br><br>' +
            'A burst of requests with incrementing IDs is a strong signal of enumeration.'
        ),

        'posture-toggle-credential-anomaly': make('Credential anomalies',
            'Repeated authentication failures from the same IP address suggest a brute-force attack.' +
            '<br><br>' +
            'This check ' + highlight('tracks per-IP authentication failure rates') + '.' +
            '<br><br>' +
            'Flagging IPs with high failure rates lets you block them before they succeed.'
        ),

        'posture-toggle-pagination-abuse': make('Pagination abuse',
            'Some APIs accept offset and page-size parameters.' +
            '<br><br>' +
            'This check ' + highlight('detects requests with extreme offset or page-size values') + '.' +
            '<br><br>' +
            'Very large values can cause excessive memory use or expose more data than intended.'
        ),

        'posture-toggle-request-rate-anomaly': make('Request rate anomalies',
            'A sudden spike in requests to a single endpoint may indicate an attack or a misbehaving client.' +
            '<br><br>' +
            'This check ' + highlight('uses sliding window counters to flag unusual traffic spikes per endpoint') + '.' +
            '<br><br>' +
            'Rate anomalies are detected even when individual requests stay within normal rate limits.'
        ),

        'posture-toggle-call-pattern-anomaly': make('Call pattern anomalies',
            'Normal API consumers follow predictable sequences of calls.' +
            '<br><br>' +
            'This check ' + highlight('uses ML-based detection to find abnormal API call sequences and timing') + '.' +
            '<br><br>' +
            'Unusual patterns can reveal automated attacks, credential stuffing, or compromised accounts.'
        )
    };
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture._fieldDescriptions = $.fn.zato.security.posture._buildFieldDescriptions();

// ////////////////////////////////////////////////////////////////////////
// Initialization
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.security.posture.init = function(initialData) {
    var posture = $.fn.zato.security.posture;
    var kit = $.fn.zato.dashboard_kit;

    // .. [1] page opacity at init start
    var pageElement = document.querySelector('.dashboard-page');
    console.log('[posture:1] init start, page opacity=' + (pageElement ? getComputedStyle(pageElement).opacity : 'no-element'));

    // .. [2] read URL tab before tabs.init
    var urlTab = kit.url_state.get('tab');
    var storedTab = localStorage.getItem('zato-posture-tab');
    console.log('[posture:2] url_tab=' + JSON.stringify(urlTab) + ', localStorage=' + JSON.stringify(storedTab));

    // .. [3] determine which tab to use as default so tabs.init opens it directly
    var effectiveDefault = urlTab || storedTab || 'authentication';
    console.log('[posture:3] effective default_tab=' + JSON.stringify(effectiveDefault));

    posture._tabHandle = kit.tabs.init({
        tab_selector: '.posture-card .dashboard-tab',
        panel_prefix: 'posture-tab-panel-',
        default_tab: effectiveDefault,
        on_change: function(tabName) {
            console.log('[posture:5] on_change fired, tab=' + JSON.stringify(tabName));
            kit.url_state.set({tab: tabName});
        }
    });

    // .. [4] after tabs.init, check which tab is active
    var activeAfterInit = posture._tabHandle.get_tab();
    console.log('[posture:4] after tabs.init, active tab=' + JSON.stringify(activeAfterInit) + ', page opacity=' + (pageElement ? getComputedStyle(pageElement).opacity : 'no-element'));

    // .. handle browser back/forward
    kit.url_state.on_pop(function(params) {
        var popTab = params.get('tab');
        console.log('[posture:6] on_pop fired, tab=' + JSON.stringify(popTab));
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
        descriptions: posture._fieldDescriptions,
        inlineBadge: true,
        inlineBadgeRowSelector: '.posture-check-item',
        inlineBadgeAnchorSelector: '.posture-check-name-text'
    });

    // .. [7] right before reveal
    console.log('[posture:7] about to reveal, active tab=' + JSON.stringify(posture._tabHandle.get_tab()) + ', page opacity=' + (pageElement ? getComputedStyle(pageElement).opacity : 'no-element'));

    // .. fade in
    kit.reveal();
};

})(jQuery);
