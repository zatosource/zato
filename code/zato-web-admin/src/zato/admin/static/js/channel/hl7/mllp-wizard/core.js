// HL7 MLLP channel wizard - the wizard kit instance.
//
// The page is rendered by zato/channel/hl7/mllp-wizard.html. The generic
// machinery - the step strip, the name badge, the footer and the save -
// comes from the wizard kit, configured here. This file holds only what
// is MLLP's own: the required fields, the help texts, the wizard-wide
// overview and the multi-security REST bridge inputs. The micro-forms
// live in forms.js, the destination rows in destinations.js and the
// summaries plus the review step in review.js.
//
// One page serves both create and edit. On edit the Django form carries
// the edit- prefix its endpoint reads its input under, and the wizard
// follows it through the kit's fieldPrefix, so nothing here knows which
// of the two actions is under way.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.channel.hl7.mllp.wizard;

// ////////////////////////////////////////////////////////////////////////

wizard.config_own = {

    // Where the Edit page's fields are found - the prefix the edit endpoint
    // reads its input under
    editFieldPrefix: 'edit-',

    // What the last step's button says, named after the action it performs
    createLabel: 'Create',
    editLabel: 'Save',

    // The connection type the name has to be unique within - generic
    // connection names are unique per type rather than across all of them
    connectionType: 'channel-hl7-mllp',

    // Which set of live form updates the page subscribes to
    createAction: 'create',
    editAction: 'edit'
};

// ////////////////////////////////////////////////////////////////////////

// The instance's own state - the kit adds its keys on top
wizard.state = {

    // Which of the two actions the page is serving
    isEdit: false,

    // Where messages go, in the order they were picked -
    // {type, connection, isActive, options}
    destinationList: [],

    // How the destinations receive a message - all at once, one after
    // another, or whenever the service hands them one
    delivery: 'same-time',

    // Which of them produces the reply the caller waits for - either the
    // literal 'service' or the name of one destination
    respondFrom: 'service',

    // The security definitions picked for the REST bridge, in row order -
    // each entry is a sec_type/id value of the Django security select
    securityKeyList: [],

    // Whether the REST bridge requires callers to authenticate at all -
    // with this off the picks above are kept but not applied
    isSecurityEnabled: true
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.wizard_kit.core.setup(wizard, {

    idPrefix: 'mllp-wizard',
    formSelector: '#create-form',

    // How many steps the wizard has
    stepCount: 3,

    // What the create page is - the edit page says so in its init options
    // and the two keys below follow it before the kit's own init runs
    fieldPrefix: '',
    finishLabel: wizard.config_own.createLabel,

    // The rows the "How does it work?" badge walks through - the card
    // header with the wizard-wide overview, then anything on a step
    // body holding a labeled field
    helpRowSelector: '.dashboard-card-header, .wizard-name-row, .wizard-toggle-row, ' +
        '.wizard-section-title, .wizard-line, .mllp-wizard-tolerance-grid',

    // Fields that must not be empty on submit - the service is not among them
    // because the destinations may take the messages instead
    requiredFields: [
        'name',
        'max_msg_size',
        'max_msg_size_unit',
        'recv_timeout',
        'idle_timeout',
        'start_seq',
        'end_seq',
        'default_character_encoding'
    ],

    // The name check is scoped to MLLP channels because generic
    // connection names are unique per connection type
    nameUnique: {
        source: 'generic_connection',
        field: 'name',
        filterName: 'type_',
        filterValue: wizard.config_own.connectionType
    },

// ////////////////////////////////////////////////////////////////////////

    onInit: function() {

        // The transport, REST and routing cards on step 1 ..
        wizard.forms.initCards();

        // .. the decision lines and the option cards on step 2 ..
        wizard.destinations.init();
        wizard.review.initOptionCards();

        // .. a live uniqueness indicator for the REST URL path - the name
        // has its own check through the kit config above ..
        $.fn.zato.validate_unique(wizard.fieldSelector('rest_url_path'), 'channel_rest', 'url_path');

        // .. keep the services and the security definitions fresh while
        // the page is open - no reloading to pick up new ones ..
        var ownConfig = wizard.config_own;
        var action = wizard.state.isEdit ? ownConfig.editAction : ownConfig.createAction;

        $.fn.zato.live_form_updates.register(action, [
            {object_type: 'service', target_select: wizard.fieldSelector('service')},
            {object_type: 'security', target_select: wizard.fieldSelector('rest_security_id')}
        ]);
        $.fn.zato.live_form_updates.start(action);

        // .. an open REST popover clones the security select into its rows,
        // so a live update to the underlying form select re-clones them.
        wizard.field('rest_security_id').on('chosen:updated', function() {
            wizard.forms.refreshSecuritySelect();
        });
    },

// ////////////////////////////////////////////////////////////////////////

    beforeSave: function(form) {

        // The destination rows travel in hidden JSON fields the backend reads ..
        wizard.destinations.serialize();

        // .. so do the security definitions picked for the REST bridge ..
        wizard._writeSecurityIdInputs(form);

        // .. and a channel handing its messages to neither a service nor a destination
        // is not created at all, the step saying which of the two is missing.
        if(!wizard._has_target()) {
            $.fn.zato.user_message(false, $.fn.zato.destinations.config.noTargetMessage);
            return false;
        }

        return true;
    }
});

// ////////////////////////////////////////////////////////////////////////

// The page hands its resolved urls and which of the two actions it is over
// once the DOM is ready, and the kit's own init does the rest. Everything
// the kit reads out of its config it reads when it needs it, so an edit
// page saying so here reaches the fields under the right prefix from the
// very first read.
wizard._kitInit = wizard.init;

wizard.init = function(options) {

    var ownConfig = wizard.config_own;

    wizard.state.isEdit = options.is_edit;

    if(options.is_edit) {
        wizard.config.fieldPrefix = ownConfig.editFieldPrefix;
        wizard.config.finishLabel = ownConfig.editLabel;

        // The steps read the state rather than the form for everything that is
        // not one field of its own, so what the channel already holds goes in
        // before the first step is drawn
        wizard._seedState(options);
    }

    wizard._kitInit(options);

    // The name and the path a channel already has are its own, so keeping them
    // is not the same as taking someone else's - this is what the uniqueness
    // checks compare each edit against
    if(options.is_edit) {
        wizard._rememberOwnValue(wizard.config.nameField);
        wizard._rememberOwnValue('rest_url_path');
    }
};

// ////////////////////////////////////////////////////////////////////////

wizard._rememberOwnValue = function(fieldName) {

    var field = wizard.field(fieldName);
    field.data('zato-original-value', field.val());
};

// ////////////////////////////////////////////////////////////////////////

// What the four decisions of step 2 and the REST security rows open with on
// edit. Each of them is answered on the page through the wizard state, so a
// stored channel says what that state starts out as - the three hidden
// fields it was serialized into, and the security list the view read out of
// the channel's own group.
wizard._seedState = function(options) {

    wizard.state.securityKeyList = options.security_key_list;

    // A bridge that is on, has no definition of its own and no group behind it is one
    // that authenticates nobody, which is what the slider says. A channel with no bridge
    // at all opens the way a new one does, with security on.
    var useRest = wizard.field('use_rest').prop('checked');
    var securityValue = wizard.field('rest_security_id').val();
    var hasSingleSecurity = false;

    if(securityValue) {
        if(securityValue !== wizard.forms.securityConfig.noSecurityValue) {
            hasSingleSecurity = true;
        }
    }

    if(useRest) {
        if(!options.security_key_list.length) {
            if(!hasSingleSecurity) {
                wizard.state.isSecurityEnabled = false;
            }
        }
    }

    wizard.destinations.deserialize();
};

// ////////////////////////////////////////////////////////////////////////

// Whether the channel has anything to hand a message to - a service, a
// destination that receives messages, or both.
wizard._has_target = function() {

    if(wizard.field('service').val()) {
        return true;
    }

    return wizard.destinations.activeList().length > 0;
};

// ////////////////////////////////////////////////////////////////////////

// The help texts behind every "How does it work?" badge on the page - the
// map keyed by field name, re-keyed for the popover inputs, plus entries
// for the controls that are not fields at all.
wizard.helpDescriptions = function() {

    var shared = $.fn.zato.channel.hl7.mllp.field_descriptions;
    var out = $.extend({}, shared);

    // The popover micro-forms name their inputs mllp-wizard-tippy-<field>
    for(var key in shared) {
        if(key.indexOf('id_') === 0) {
            out['mllp-wizard-tippy-' + key.substring(3)] = shared[key];
        }
    }

    // The page title carries the wizard-wide overview
    out['mllp-wizard-title'] = wizard.titleHelp();

    // The security rows of the REST popover allow more than one pick
    out['mllp-wizard-tippy-rest_security_id'] = 'Security definitions used to authenticate<br>incoming REST requests.<br>More than one can be assigned.<br>When the slider is off, with security disabled,<br>the channel will accept requests from anyone<br>who knows its address.';

    // The step 1 transport toggles and the routing link ..
    out['mllp-wizard-toggle-mllp'] = 'When on, HL7 v2 messages framed with MLLP<br>are received over plain TCP.<br>When off, messages arrive over REST only.';
    out['mllp-wizard-toggle-rest'] = shared['id_use_rest'];
    out['mllp-wizard-edit-routing'] = 'Which incoming messages this channel will accept.<br>With no matchers, every message will be accepted -<br>matchers filter by MSH header fields,<br>e.g. sending application or message type.';

    // .. and the four decisions of step 2.
    out['mllp-wizard-slot-destinations-chip'] = 'The outgoing connections every message reaches<br>once the service has run.<br>Each of them carries the options its kind has,<br>e.g. the HTTP method of a REST call,<br>and a switch deciding whether it receives messages at all.';
    out['mllp-wizard-slot-service-chip'] = shared['id_service'];
    out['mllp-wizard-slot-delivery'] = 'All the destinations at once,<br>or one after another in the order<br>they were picked.';
    out['mllp-wizard-slot-reply-chip'] = shared['destinations-respond-from'];

    // .. and the options folded away under the four decisions.
    out['mllp-wizard-edit-options'] = 'The fixups applied to messages that do not<br>quite follow the standard, how long control IDs<br>are remembered for and what is written to the logs.<br>The line says what is currently set.';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The wizard-wide overview shown when the page title is clicked - one of
// the regular "How does it work?" stops. Everyone gets the short pitch,
// and the MLLP primer waits folded inside for those who want the
// background - the help tooltips are interactive, so the fold can be
// clicked open in place.
wizard.titleHelp = function() {

    var out =
        '<div class="wizard-title-help">' +

        '<p>This wizard creates a channel - the entry point through which ' +
        'HL7 v2 messages reach the platform.</p>' +

        '<p><span class="wizard-title-help-step">01</span> decides how messages arrive - ' +
        'MLLP over TCP, REST, or both - and which ones will be accepted. ' +
        '<span class="wizard-title-help-step">02</span> picks the service that handles ' +
        'each message and where results go next. ' +
        '<span class="wizard-title-help-step">03</span> is a review before the channel is created.</p>' +

        '<details class="wizard-title-help-details">' +
        '<summary>New to MLLP? A 30-second primer</summary>' +
        '<div class="wizard-title-help-primer">' +

        '<p>HL7 v2 is the format clinical systems use to tell each other ' +
        'what just happened - an admission, a lab result, an order.</p>' +

        '<p>MLLP, the Minimal Lower Layer Protocol, is the envelope those ' +
        'messages travel in over a TCP connection - one control byte marks where ' +
        'a message begins and two more where it ends, so both sides always ' +
        'agree on message boundaries.</p>' +

        '<p>A channel is a listener for such connections - it unwraps each ' +
        'message, hands it to a service and replies with an acknowledgment ' +
        'on its own. If in doubt, name the channel, pick a service on step 02 ' +
        'and keep the defaults.</p>' +

        '</div>' +
        '</details>' +
        '</div>';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// With two or more security definitions picked, all of them travel as
// repeated hidden inputs and the backend wraps them in a security group
// of the channel's own. A single pick travels in the rest_security_id
// select alone.
wizard._writeSecurityIdInputs = function(form) {

    form.find('.mllp-wizard-security-input').remove();

    // With security off the picks stay in the wizard state only -
    // the channel goes out with no security at all
    if(!wizard.state.isSecurityEnabled) {
        return;
    }

    // A definition deleted after the picks were made - and reported by
    // a broadcast since - must not travel to the backend, so only the
    // picks the Django select still knows about go out.
    var knownValues = {};
    wizard.field('rest_security_id').find('option').each(function() {
        knownValues[this.value] = true;
    });

    var keyList = wizard.state.securityKeyList.filter(function(key) {
        return knownValues[key];
    });

    if(keyList.length < 2) {
        return;
    }

    for(var keyIdx = 0; keyIdx < keyList.length; keyIdx++) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.className = 'mllp-wizard-security-input';
        input.name = 'mllp_security_id_list';
        input.value = keyList[keyIdx];
        form.append(input);
    }
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
