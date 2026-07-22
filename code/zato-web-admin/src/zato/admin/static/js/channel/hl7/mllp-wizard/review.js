// HL7 MLLP channel wizard - live summaries, the option cards and the review step.
//
// Every card on steps 1 and 2 carries a one-line summary of what is currently
// configured, recomputed from the form each time a micro-form closes. The
// review step renders the same data as grouped rows through the wizard kit's
// renderer, each group with an Edit link that jumps back to the step the
// answers came from.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.channel.hl7.mllp.wizard;
var review = wizard.review;

$.fn.zato.wizard_kit.review.setup(wizard);

// ////////////////////////////////////////////////////////////////////////

review.config = {

    // The routing summary when no matcher is filled in
    anyMessageLabel: 'All messages',

    // What the review says when no destination is configured
    noDestinationsLabel: 'None - the service handles everything',

    // What the tolerance review says when nothing differs from the defaults
    allStandardFixupsLabel: 'All standard fixups enabled',

    // The matcher fields and their labels, in MSH order
    matcherFields: [
        {field: 'msh3_sending_app',        label: 'MSH-3 sending application'},
        {field: 'msh4_sending_facility',   label: 'MSH-4 sending facility'},
        {field: 'msh5_receiving_app',      label: 'MSH-5 receiving application'},
        {field: 'msh6_receiving_facility', label: 'MSH-6 receiving facility'},
        {field: 'msh9_message_type',       label: 'MSH-9.1 message type'},
        {field: 'msh9_trigger_event',      label: 'MSH-9.2 trigger event'},
        {field: 'msh11_processing_id',     label: 'MSH-11 processing ID'},
        {field: 'msh12_version_id',        label: 'MSH-12 version'}
    ],

    // The tolerance toggles, in the order the card shows them
    toleranceFields: [
        'normalize_line_endings',
        'force_standard_delimiters',
        'repair_truncated_msh',
        'split_concatenated_messages',
        'normalize_obx2_value_type',
        'replace_invalid_obx2_value_type',
        'normalize_invalid_escape_sequences',
        'normalize_obx8_abnormal_flags',
        'normalize_quadruple_quoted_empty',
        'allow_short_encoding_characters',
        'fix_off_by_one_field_index'
    ]
};

// The tolerance defaults, snapshotted from the form before the user touches it
review._toleranceDefaults = {};

// ////////////////////////////////////////////////////////////////////////

// The human label of a tolerance toggle - the text of the label wrapping it.
review._toleranceLabel = function(fieldName) {

    var label = wizard.field(fieldName).closest('label');
    var out = label.text().trim();

    return out;
};

// ////////////////////////////////////////////////////////////////////////

review.initOptionCards = function() {

    var config = review.config;

    // Remember what the tolerance defaults are so the review can diff against them ..
    for(var fieldIdx = 0; fieldIdx < config.toleranceFields.length; fieldIdx++) {
        var fieldName = config.toleranceFields[fieldIdx];
        review._toleranceDefaults[fieldName] = wizard.field(fieldName).prop('checked');
    }

    // .. the tolerance card expands and collapses in place ..
    $('#mllp-wizard-tolerance-header').on('click', function() {
        $('#mllp-wizard-tolerance-body').toggleClass('wizard-option-body-open');
        $('#mllp-wizard-tolerance-chevron').toggleClass('wizard-chevron-open');
    });

    // .. its summary follows the checkboxes as they are toggled ..
    $('#mllp-wizard-tolerance-body input[type="checkbox"]').on('change', function() {
        review.refreshSummaries();
    });

    // .. and the two smaller cards open their micro-forms.
    $('#mllp-wizard-card-dedup').on('click', function() {
        wizard.forms.open('dedup', this);
    });

    $('#mllp-wizard-card-logging').on('click', function() {
        wizard.forms.open('logging', this);
    });
};

// ////////////////////////////////////////////////////////////////////////

review._transportSummary = function() {

    var startSeq = wizard.field('start_seq').val();
    var endSeq = wizard.field('end_seq').val();
    var maxSize = wizard.field('max_msg_size').val();
    var maxSizeUnit = wizard.field('max_msg_size_unit').find('option:selected').text();

    // With the MSH-18 flag on, each message names its own encoding
    // and the configured one applies when a message does not
    var useMsh18 = wizard.field('use_msh18_encoding').prop('checked');
    var encoding = wizard.field('default_character_encoding').val();

    if(useMsh18) {
        encoding = 'MSH-18 or ' + encoding;
    }

    var out = startSeq + ' / ' + endSeq + ', ' + maxSize + ' ' + maxSizeUnit + ' max, ' + encoding;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review._restSummary = function() {

    var useRest = wizard.field('use_rest').prop('checked');
    if(!useRest) {
        return '';
    }

    var parts = [];

    var urlPath = wizard.field('rest_url_path').val().trim();
    if(urlPath) {
        parts.push(urlPath);
    }
    else {
        parts.push('On');
    }

    if(wizard.field('rest_only').prop('checked')) {
        parts.push('REST only');
    }

    var securityCount = wizard.state.securityKeyList.length;

    if(!wizard.state.isSecurityEnabled) {
        parts.push('no security');
    }
    else if(securityCount > 1) {
        parts.push(securityCount + ' security definitions');
    }

    var out = parts.join(', ');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review._routingSummary = function() {

    var config = review.config;

    var parts = [];

    for(var matcherIdx = 0; matcherIdx < config.matcherFields.length; matcherIdx++) {
        var matcher = config.matcherFields[matcherIdx];
        var value = wizard.field(matcher.field).val().trim();

        if(value) {
            var shortLabel = matcher.label.split(' ')[0];
            parts.push(shortLabel + ' = ' + value);
        }
    }

    if(!parts.length) {
        var out = config.anyMessageLabel;
        return out;
    }

    var out = parts.join(', ');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review._toleranceSummary = function() {

    var config = review.config;

    var enabledCount = 0;

    for(var fieldIdx = 0; fieldIdx < config.toleranceFields.length; fieldIdx++) {
        if(wizard.field(config.toleranceFields[fieldIdx]).prop('checked')) {
            enabledCount++;
        }
    }

    var out = enabledCount + ' of ' + config.toleranceFields.length + ' fixups enabled';
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review._dedupSummary = function() {

    var ttlValue = parseInt(wizard.field('dedup_ttl_value').val());
    if(isNaN(ttlValue)) {
        ttlValue = 0;
    }

    if(!ttlValue) {
        return 'Off';
    }

    var unit = wizard.field('dedup_ttl_unit').find('option:selected').text().toLowerCase();

    var out = ttlValue + ' ' + unit;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review._loggingSummary = function() {

    var parts = [];

    var returnErrors = wizard.field('should_return_errors').prop('checked');
    parts.push(returnErrors ? 'Errors returned' : 'Errors hidden');

    var logMessages = wizard.field('should_log_messages').prop('checked');
    parts.push(logMessages ? 'log I/O on' : 'log I/O off');

    parts.push(wizard.field('logging_level').val());

    var out = parts.join(', ');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Recomputes every card summary and the card selection states.
review.refreshSummaries = function() {

    // A summary shows only while its transport is on - it doubles
    // as the link that opens the protocol options popover
    var isMllpOn = !wizard.field('rest_only').prop('checked');
    var useRest = wizard.field('use_rest').prop('checked');

    review.setSummary('mllp-wizard-summary-transport', isMllpOn ? review._transportSummary() : '');
    review.setSummary('mllp-wizard-summary-rest', review._restSummary());
    review.setSummary('mllp-wizard-summary-tolerance', review._toleranceSummary());
    review.setSummary('mllp-wizard-summary-dedup', review._dedupSummary());
    review.setSummary('mllp-wizard-summary-logging', review._loggingSummary());

    // .. and the transport toggles mirror the hidden form flags.
    $('#mllp-wizard-toggle-mllp').prop('checked', isMllpOn);
    $('#mllp-wizard-toggle-rest').prop('checked', useRest);

    review.setSummary('mllp-wizard-summary-routing', review._routingSummary());
};

// ////////////////////////////////////////////////////////////////////////

// The tolerance rows for the review - only what differs from the defaults.
review._toleranceReviewRows = function() {

    var config = review.config;

    var out = [];

    for(var fieldIdx = 0; fieldIdx < config.toleranceFields.length; fieldIdx++) {
        var fieldName = config.toleranceFields[fieldIdx];

        var isChecked = wizard.field(fieldName).prop('checked');
        if(isChecked === review._toleranceDefaults[fieldName]) {
            continue;
        }

        out.push([review._toleranceLabel(fieldName), isChecked ? 'On' : 'Off']);
    }

    if(!out.length) {
        out.push([config.allStandardFixupsLabel, '']);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Renders the review step from the current form state.
review.render = function() {

    var config = review.config;

    // Basics
    var basicsRows = [
        ['Name', wizard.field('name').val().trim()],
        ['Active', wizard.field('is_active').prop('checked') ? 'Yes' : 'No']
    ];

    // Transport
    var isRestOnly = wizard.field('rest_only').prop('checked');
    var transportRows = [
        ['MLLP', isRestOnly ? 'Off - REST only' : review._transportSummary()]
    ];

    var restSummary = review._restSummary();
    transportRows.push(['REST bridge', restSummary ? restSummary : 'Off']);

    // A REST bridge anyone can call deserves a loud reminder
    if(restSummary && !wizard.state.isSecurityEnabled) {
        var securityBadge = document.createElement('span');
        securityBadge.className = 'wizard-badge wizard-badge-alert wizard-badge-blink';
        securityBadge.textContent = 'DISABLED';
        transportRows.push(['REST security', securityBadge]);
    }

    // Routing - the default flag and the matchers live side by side,
    // just like on the full-page editor's routing tab
    var routingRows = [];

    if(wizard.field('is_default').prop('checked')) {
        routingRows.push(['Default channel', 'Receives everything no other channel claimed']);
    }

    for(var matcherIdx = 0; matcherIdx < config.matcherFields.length; matcherIdx++) {
        var matcher = config.matcherFields[matcherIdx];
        var matcherValue = wizard.field(matcher.field).val().trim();
        if(matcherValue) {
            routingRows.push([matcher.label, matcherValue]);
        }
    }

    if(!routingRows.length) {
        routingRows.push([config.anyMessageLabel, '']);
    }

    // Service and destinations
    var serviceRows = [
        ['Service', wizard.field('service').val()]
    ];

    var destinationCount = 0;

    for(var destinationIdx = 0; destinationIdx < wizard.state.destinationList.length; destinationIdx++) {
        var destination = wizard.state.destinationList[destinationIdx];
        if(destination.connection) {
            destinationCount++;
            var rowLabel = wizard.destinations._rowLabel(destination);
            if(!destination.isActive) {
                rowLabel += ' (inactive)';
            }
            serviceRows.push(['Destination', rowLabel]);
        }
    }

    if(!destinationCount) {
        serviceRows.push(['Destinations', config.noDestinationsLabel]);
    }
    else {
        var respondFrom = $('#mllp-wizard-respond-from').find('option:selected').text();
        serviceRows.push(['Respond from', respondFrom]);
    }

    review.renderGroups([
        {label: 'Basics',       step: 0, rows: basicsRows},
        {label: 'Transport',    step: 0, rows: transportRows},
        {label: 'Routing',      step: 0, rows: routingRows},
        {label: 'Service and destinations', step: 1, rows: serviceRows},
        {label: 'Tolerance',    step: 1, rows: review._toleranceReviewRows()},
        {label: 'Deduplication', step: 1, rows: [['Window', review._dedupSummary()]]},
        {label: 'Logging',      step: 1, rows: [['Behavior', review._loggingSummary()]]}
    ]);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
