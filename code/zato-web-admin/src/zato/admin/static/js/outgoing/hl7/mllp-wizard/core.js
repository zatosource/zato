// HL7 MLLP outgoing connection wizard - the wizard kit instance.
//
// The page is rendered by zato/outgoing/hl7/mllp-wizard.html. The generic
// machinery - the step strip, the name badge, the footer and the save -
// comes from the wizard kit, configured here. This file holds only what
// is MLLP's own: the required fields, the help texts, the wizard-wide
// overview and the two mounts of the live check. The micro-forms live in
// forms.js and the summaries plus the review step in review.js.
//
// One page serves both create and edit. On edit the Django form carries
// the edit- prefix its endpoint reads its input under, and the wizard
// follows it through the kit's fieldPrefix, so nothing here knows which
// of the two actions is under way.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.outgoing.hl7.mllp.wizard;

// ////////////////////////////////////////////////////////////////////////

wizard.config_own = {

    // Where the Edit page's fields are found - the prefix the edit endpoint
    // reads its input under
    editFieldPrefix: 'edit-',

    // What the button ending either of the two actions says
    saveLabel: 'Save',

    // The sections the review is read in, each group of answers under its own -
    // the missing targets below name them too, which is why they are here rather
    // than in the review module, loaded after this one
    groups: {
        destination: 'Destination',
        framing: 'Framing and timing',
        delivery: 'Delivery',
        logging: 'Logging and audit'
    },

    // The connection type the name has to be unique within - generic
    // connection names are unique per type rather than across all of them
    connectionType: 'outconn-hl7-mllp',

    // What the live check sends its answers to, filled in by init from the
    // url the template resolved
    testUrl: '',

    // What the two mounts of the live check say on their buttons
    probeRunLabel: 'Send a test message',
    probeBusyLabel: 'Sending ..',

    // The fields the live check carries with it - what it takes to reach an
    // endpoint and read one acknowledgment back from it
    probeFields: [
        'address',
        'start_seq',
        'end_seq',
        'recv_timeout',
        'max_msg_size',
        'read_buffer_size',
        'tls_ca_path',
        'tls_cert_path',
        'tls_key_path'
    ]
};

// ////////////////////////////////////////////////////////////////////////

// The instance's own state - the kit adds its keys on top
wizard.state = {

    // The two live checks, so that an answer they were about changing
    // clears whatever they last said
    probeList: []
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.wizard_kit.core.setup(wizard, {

    idPrefix: 'mllp-outconn-wizard',
    formSelector: '#create-form',

    // How many steps the wizard has
    stepCount: 3,

    // What the create page is - the edit page says so in its init options
    // and the prefix below follows it before the kit's own init runs
    fieldPrefix: '',
    finishLabel: wizard.config_own.saveLabel,

    // The rows the "How does it work?" badge walks through - the card header
    // with the wizard-wide overview, then anything on a step body holding a
    // labeled field
    helpRowSelector: '.dashboard-card-header, .wizard-name-row, .wizard-field-row, ' +
        '.wizard-toggle-row, .wizard-line, .wizard-option-header',

    // Fields that must not be empty on submit - the same list the popup form
    // held the connection to, an endpoint with no address being the one
    // answer nothing can stand in for
    requiredFields: [
        'name',
        'address',
        'start_seq',
        'end_seq',
        'recv_timeout',
        'max_msg_size',
        'read_buffer_size',
        'pool_size'
    ],

    // Where each of them is read on the review and answered on its step - the
    // name and the address stand on rows of their own, the rest are edited in
    // the popovers the three lines below open
    missingTargets: {
        name:             {group: wizard.config_own.groups.destination, label: 'Name'},
        address:          {group: wizard.config_own.groups.destination, label: 'Address'},
        start_seq:        {group: wizard.config_own.groups.framing, anchorSelector: '#mllp-outconn-wizard-row-framing'},
        end_seq:          {group: wizard.config_own.groups.framing, anchorSelector: '#mllp-outconn-wizard-row-framing'},
        max_msg_size:     {group: wizard.config_own.groups.framing, anchorSelector: '#mllp-outconn-wizard-row-framing'},
        read_buffer_size: {group: wizard.config_own.groups.framing, anchorSelector: '#mllp-outconn-wizard-row-framing'},
        recv_timeout:     {group: wizard.config_own.groups.framing, anchorSelector: '#mllp-outconn-wizard-row-timing'},
        pool_size:        {group: wizard.config_own.groups.delivery, anchorSelector: '#mllp-outconn-wizard-row-pool'}
    },

    // The name check is scoped to MLLP outgoing connections because generic
    // connection names are unique per connection type
    nameUnique: {
        source: 'generic_connection',
        field: 'name',
        filterName: 'type_',
        filterValue: wizard.config_own.connectionType
    },

// ////////////////////////////////////////////////////////////////////////

    onInit: function() {

        // The popovers behind the summary links of both steps ..
        wizard.forms.initRows();

        // .. the logging card folded away under step 2 ..
        wizard.review.initOptionCards();

        // .. and the live check, mounted once at the foot of step 1 where
        // everything it needs has just been answered, and once more at the
        // foot of the review so the endpoint can be tried again before the
        // connection is created.
        wizard._initProbes();
    }
});

// ////////////////////////////////////////////////////////////////////////

// Both mounts of the live check. They are independent of each other and
// each keeps its own verdict, so walking back to step 1 does not wipe what
// the review's check said.
wizard._initProbes = function() {

    var ownConfig = wizard.config_own;

    var mountList = [
        {slotId: 'mllp-outconn-wizard-slot-check', buttonId: 'mllp-outconn-wizard-check'},
        {slotId: 'mllp-outconn-wizard-slot-review-check', buttonId: 'mllp-outconn-wizard-review-check'}
    ];

    for(var mountIdx = 0; mountIdx < mountList.length; mountIdx++) {

        var mount = mountList[mountIdx];

        var probe = $.fn.zato.wizard_kit.probe.init(wizard, {
            slotId: mount.slotId,
            buttonId: mount.buttonId,
            endpoint: ownConfig.testUrl,
            fields: ownConfig.probeFields,
            runLabel: ownConfig.probeRunLabel,
            busyLabel: ownConfig.probeBusyLabel
        });

        wizard.state.probeList.push(probe);
    }

    // A verdict is about the endpoint that was on screen when it was given,
    // so changing the address makes both of them stale
    wizard.field('address').on('input', function() {
        wizard.resetProbes();
    });
};

// ////////////////////////////////////////////////////////////////////////

// Clears what both checks last said - called whenever an answer they were
// about has changed.
wizard.resetProbes = function() {

    var probeList = wizard.state.probeList;

    for(var probeIdx = 0; probeIdx < probeList.length; probeIdx++) {
        probeList[probeIdx].reset();
    }
};

// ////////////////////////////////////////////////////////////////////////

// The page hands its resolved urls and which of the two actions it is over
// once the DOM is ready, and the kit's own init does the rest. Everything
// the kit reads out of its config it reads when it needs it, so an edit
// page saying so here reaches the fields under the right prefix from the
// very first read.
wizard._kitInit = wizard.init;

wizard.init = function(options) {

    var ownConfig = wizard.config_own;

    ownConfig.testUrl = options.test_url;

    if(options.is_edit) {
        wizard.config.fieldPrefix = ownConfig.editFieldPrefix;
    }

    wizard._kitInit(options);

    // The name a connection already has is its own, so keeping it is not the
    // same as taking someone else's - this is what the uniqueness check
    // compares each edit against
    if(options.is_edit) {
        var nameField = wizard.field(wizard.config.nameField);
        nameField.data('zato-original-value', nameField.val());
    }
};

// ////////////////////////////////////////////////////////////////////////

// The help texts behind every "How does it work?" badge on the page - the
// map the list page uses, re-keyed for the popover inputs, plus entries for
// the controls only the wizard has.
wizard.helpDescriptions = function() {

    var shared = $.fn.zato.outgoing.hl7.mllp.field_descriptions;
    var out = $.extend({}, shared);

    // The popover micro-forms name their inputs mllp-outconn-wizard-tippy-<field>
    for(var key in shared) {
        if(key.indexOf('id_') === 0) {
            out['mllp-outconn-wizard-tippy-' + key.substring(3)] = shared[key];
        }
    }

    // The page title carries the wizard-wide overview
    out['mllp-outconn-wizard-title'] = wizard.titleHelp();

    // The summary links of step 1, each standing for the popover behind it ..
    out['mllp-outconn-wizard-edit-framing'] = 'How each message is wrapped on the wire -<br>the bytes that mark where a message begins<br>and ends, and how large a reply may be.<br>The defaults follow the MLLP standard.';
    out['mllp-outconn-wizard-edit-timing'] = 'How long to wait for the acknowledgment<br>the receiving system sends back.<br>A message with no answer within that time<br>counts as a failed send.';
    out['mllp-outconn-wizard-toggle-tls'] = 'When on, the connection is encrypted with TLS<br>and the receiving system\'s certificate is verified<br>against the CA bundle given.<br>When off, messages travel in plaintext.';
    out['mllp-outconn-wizard-edit-tls'] = out['mllp-outconn-wizard-toggle-tls'];

    // .. the live check, which both of its mounts share ..
    out['mllp-outconn-wizard-check'] = 'Sends one test message to the address above<br>and reports what came back.<br>Nothing is saved either way, so this can be used<br>before the connection is created.';
    out['mllp-outconn-wizard-review-check'] = out['mllp-outconn-wizard-check'];

    // .. the three decisions of step 2 ..
    out['mllp-outconn-wizard-edit-pool'] = shared['id_pool_size'];
    out['mllp-outconn-wizard-edit-retries'] = 'What happens to a message the receiving system<br>did not take - how many times it is sent again<br>and how long the platform waits between attempts.';
    out['mllp-outconn-wizard-edit-breaker'] = 'When too many sends fail in a row, the platform<br>stops trying for a while rather than queueing up<br>work for an endpoint that is down.<br>One trial message decides when to resume.';

    // .. and what is folded away under them.
    out['mllp-outconn-wizard-edit-options'] = 'What this connection writes about the messages<br>it sends - the server log and the audit log.<br>The line says what is currently set.';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The wizard-wide overview shown when the page title is clicked - one of
// the regular "How does it work?" stops. Everyone gets the short pitch, and
// the MLLP primer waits folded inside for those who want the background -
// the help tooltips are interactive, so the fold can be clicked open in
// place.
wizard.titleHelp = function() {

    var out =
        '<div class="wizard-title-help">' +

        '<p>This wizard creates an outgoing connection - the way services on ' +
        'this platform send HL7 v2 messages to a system elsewhere.</p>' +

        '<p><span class="wizard-title-help-step">01</span> names the connection ' +
        'and says which system it reaches, with a test message that can be sent ' +
        'before anything is saved. ' +
        '<span class="wizard-title-help-step">02</span> decides what happens to a ' +
        'message the far side did not take. ' +
        '<span class="wizard-title-help-step">03</span> is a review before the ' +
        'connection is created.</p>' +

        '<details class="wizard-title-help-details">' +
        '<summary>New to MLLP? A 30-second primer</summary>' +
        '<div class="wizard-title-help-primer">' +

        '<p>HL7 v2 is the format clinical systems use to tell each other ' +
        'what just happened - an admission, a lab result, an order.</p>' +

        '<p>MLLP, the Minimal Lower Layer Protocol, is the envelope those ' +
        'messages travel in over a TCP connection - one control byte marks where ' +
        'a message begins and two more where it ends, so both sides always ' +
        'agree on message boundaries.</p>' +

        '<p>An outgoing connection is the sending end of that. A service ' +
        'hands it a message, it frames it, sends it and waits for the ' +
        'acknowledgment. If in doubt, name the connection, fill in the ' +
        'address and keep the defaults.</p>' +

        '</div>' +
        '</details>' +
        '</div>';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
