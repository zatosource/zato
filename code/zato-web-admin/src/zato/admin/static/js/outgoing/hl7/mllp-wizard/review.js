// HL7 MLLP outgoing connection wizard - the card summaries and the review
// step.
//
// Each row of steps 1 and 2 carries a one-line summary of what its popover
// currently holds, so a step reads as a set of answers rather than as a set
// of links. The review step says the same things again, grouped, each group
// linking back to the popover its answers came from.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.outgoing.hl7.mllp.wizard;

$.fn.zato.wizard_kit.review.setup(wizard);

var review = wizard.review;

// The shared Delivery tab - the retry and DLQ summaries are its own
var deliveryTab = $.fn.zato.delivery_tab;
var deliveryConfig = deliveryTab.config;

// ////////////////////////////////////////////////////////////////////////

review.config_own = {

    // What the Retries line adds when the queue is on, and what the DLQ line and
    // the review say of a switch that is off or on
    queueOnSuffix: ', through the queue',
    offText: 'Off',
    onText: 'On',

    // What a summary says when TLS is off, when only the server is verified
    // and when the far side asks for a certificate of this side too
    tlsOffText: 'Plaintext',
    tlsVerifiedText: 'Verified',
    tlsMutualText: 'Verified, with a client certificate',

    // What the logging summary says when neither log is being written
    loggingOffText: 'Nothing logged',

    // The two logs, in the order the summary names them
    logNameList: [
        {field: 'should_log_messages', label: 'Server log'},
        {field: 'is_audit_log_active', label: 'Audit log'}
    ],

    // What one megabyte is, for the framing summary - a size in bytes says
    // little at a glance and the field itself is where the exact figure is
    bytesPerMegabyte: 1024 * 1024,

    // How many decimal places a size in megabytes is rounded to
    megabyteDecimals: 1,

    // What the review says instead of a value that has not been given
    emptyText: '-',

    // What an active connection and an inactive one are called
    activeText: 'Yes',
    inactiveText: 'No'
};

// ////////////////////////////////////////////////////////////////////////

// A size in bytes, said the way a reader thinks of it.
review._humanSize = function(byteCount) {

    var ownConfig = review.config_own;
    var megabytes = byteCount / ownConfig.bytesPerMegabyte;

    var out = parseFloat(megabytes.toFixed(ownConfig.megabyteDecimals)) + ' MB';
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review.summaryFraming = function() {

    var startSequence = wizard.field('start_seq').val();
    var endSequence = wizard.field('end_seq').val();
    var maxSize = review._humanSize(parseInt(wizard.field('max_msg_size').val()));

    var out = startSequence + ' / ' + endSequence + ', up to ' + maxSize;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review.summaryTiming = function() {

    var out = 'ACK within ' + wizard.field('recv_timeout').val() + ' ms';
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review.summaryTls = function() {

    var ownConfig = review.config_own;

    if(!wizard.forms.isTlsOn()) {
        return ownConfig.tlsOffText;
    }

    // A client certificate is what turns a verified connection into a mutual one
    if(wizard.field('tls_cert_path').val().trim()) {
        return ownConfig.tlsMutualText;
    }

    return ownConfig.tlsVerifiedText;
};

// ////////////////////////////////////////////////////////////////////////

review.summaryPool = function() {

    var out = wizard.field('pool_size').val() + ' connections';
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review.isQueueOn = function() {
    var out = wizard.field(deliveryConfig.fieldUseQueue).prop('checked');
    return out;
};

review.isDlqOn = function() {
    var out = wizard.field(deliveryConfig.fieldUseDLQ).prop('checked');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The tab's own sentence about the retries, and where they run when the queue is on
review.summaryRetries = function() {

    var out = deliveryTab.formatRetriesSummary();

    if(review.isQueueOn()) {
        out += review.config_own.queueOnSuffix;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Off, or the tab's own sentence about what the DLQ rule does with a message
review.summaryDlq = function() {

    if(!review.isDlqOn()) {
        return review.config_own.offText;
    }

    var out = deliveryTab.formatSummary();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review._switchText = function(isOn) {

    var ownConfig = review.config_own;
    var out = isOn ? ownConfig.onText : ownConfig.offText;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The word failures has to be here - "50% in 60 s" on its own would read
// as a cap on how much may be sent, which is not what the limit is
review.summarySendLimit = function() {

    var failurePercent = wizard.field('circuit_breaker_threshold_percent').val();
    var window_ = wizard.field('circuit_breaker_window_seconds').val();
    var resume = wizard.field('circuit_breaker_reset_seconds').val();

    var out = failurePercent + '% failures in ' + window_ + ' s, resume after ' + resume + ' s';
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review.summaryLogging = function() {

    var ownConfig = review.config_own;
    var nameList = [];

    for(var logIdx = 0; logIdx < ownConfig.logNameList.length; logIdx++) {

        var log = ownConfig.logNameList[logIdx];

        if(wizard.field(log.field).prop('checked')) {
            nameList.push(log.label);
        }
    }

    if(!nameList.length) {
        return ownConfig.loggingOffText;
    }

    var out = nameList.join(', ') + ' at ' + wizard.field('logging_level').val();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

review.initOptionCards = function() {

    // The logging card is folded away behind one line, the way the options
    // of the channel wizard's second step are, its link saying what is inside
    $.fn.zato.wizard_kit.collapse.initSection({
        toggleId: 'mllp-outconn-wizard-edit-options',
        bodyId: 'mllp-outconn-wizard-options-body',
        hintId: 'mllp-outconn-wizard-hint-options'
    });
};

// ////////////////////////////////////////////////////////////////////////

// Unfolds the options section, since a popover anchored at a card inside it
// would otherwise have nothing on screen to point at.
review.openOptions = function() {

    var body = $('#mllp-outconn-wizard-options-body');

    if(body.prop('hidden')) {
        $('#mllp-outconn-wizard-edit-options').trigger('click');
    }
};

// ////////////////////////////////////////////////////////////////////////

// Recomputed from the form each time a popover closes, which is the only
// moment any of these answers can have changed.
review.refreshSummaries = function() {

    // The switch of a row whose popover has just closed follows what was
    // filled in there rather than what was clicked to open it ..
    wizard.forms.syncTlsToggle();

    review.setSummary('mllp-outconn-wizard-summary-framing', review.summaryFraming());
    review.setSummary('mllp-outconn-wizard-summary-timing', review.summaryTiming());
    review.setSummary('mllp-outconn-wizard-summary-tls', review.summaryTls());

    review.setSummary('mllp-outconn-wizard-summary-pool', review.summaryPool());
    review.setSummary('mllp-outconn-wizard-summary-retries', review.summaryRetries());
    review.setSummary('mllp-outconn-wizard-summary-dlq', review.summaryDlq());
    review.setSummary('mllp-outconn-wizard-summary-send-limit', review.summarySendLimit());
    review.setSummary(wizard.alerts.config.summaryId, wizard.alerts.summary());

    review.setSummary('mllp-outconn-wizard-summary-options', review.summaryLogging());
    review.setSummary('mllp-outconn-wizard-summary-logging', review.summaryLogging());

    // .. and whatever the live check last said was about the answers as they
    // were before this, so it no longer stands.
    wizard.resetProbes();
};

// ////////////////////////////////////////////////////////////////////////

// One value as the review shows it - a field left empty says so rather
// than leaving a row that looks unfinished.
review._value = function(fieldName) {

    var value = wizard.field(fieldName).val().trim();

    if(!value) {
        return review.config_own.emptyText;
    }

    return value;
};

// ////////////////////////////////////////////////////////////////////////

// Opens the named popover on the row it belongs to - what an Edit link of
// the review does once it has jumped to the step.
review._buildEdit = function(descriptorName, linkId) {

    var out = function() {
        wizard.forms.open(descriptorName, document.getElementById(linkId));
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

review.render = function() {

    var ownConfig = review.config_own;
    var groups = wizard.config_own.groups;
    var isActive = wizard.field('is_active').prop('checked');

    review.renderGroups([
        {
            label: groups.destination,
            step: 0,
            rows: [
                ['Name', review._value('name')],
                ['Address', review._value('address')],
                ['Active', isActive ? ownConfig.activeText : ownConfig.inactiveText]
            ]
        },
        {
            label: groups.framing,
            step: 0,
            edit: review._buildEdit('framing', 'mllp-outconn-wizard-edit-framing'),
            rows: [
                ['Framing', review.summaryFraming()],
                ['Timing', review.summaryTiming()],
                ['TLS', review.summaryTls()]
            ]
        },
        {
            label: groups.delivery,
            step: 1,
            edit: function() {
                wizard.forms.openRetries(document.getElementById(wizard.forms.config_own.retriesEditLinkId));
            },
            rows: [
                ['Pool', review.summaryPool()],
                ['Retries', deliveryTab.formatRetriesSummary()],
                ['Use queue', review._switchText(review.isQueueOn())],
                ['Dead-letter queue', review.summaryDlq()],
                ['Send limit', review.summarySendLimit()]
            ]
        },
        {
            label: groups.alerts,
            step: 1,
            edit: function() {
                wizard.alerts.open(document.getElementById(wizard.alerts.config.editLinkId));
            },
            rows: wizard.alerts.reviewRows()
        },
        {
            label: groups.logging,
            step: 1,
            edit: function() {
                review.openOptions();
                wizard.forms.open('logging', document.getElementById('mllp-outconn-wizard-card-logging'));
            },
            rows: [
                ['Behavior', review.summaryLogging()]
            ]
        }
    ]);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
