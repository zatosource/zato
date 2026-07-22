// HL7 MLLP channel wizard - the wizard kit instance.
//
// The page is rendered by zato/channel/hl7/mllp-wizard.html. The generic
// machinery - the step strip, the name badge, the footer and the save -
// comes from the wizard kit, configured here. This file holds only what
// is MLLP's own: the required fields, the help texts, the wizard-wide
// overview and the multi-security REST bridge inputs. The micro-forms
// live in forms.js, the destination rows in destinations.js and the
// summaries plus the review step in review.js.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.channel.hl7.mllp.wizard;

// The instance's own state - the kit adds its keys on top
wizard.state = {

    // Destination rows - {type, connection, isActive, options}
    destinationList: [],

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

    // The rows the "How does it work?" badge walks through - the card
    // header with the wizard-wide overview, then anything on a step
    // body holding a labeled field
    helpRowSelector: '.dashboard-card-header, .wizard-name-row, .wizard-toggle-row, ' +
        '.wizard-section-title, .wizard-respond-from-row, .mllp-wizard-tolerance-grid',

    // Fields that must not be empty on submit - the same list the editor uses
    requiredFields: [
        'name',
        'service',
        'logging_level',
        'max_msg_size',
        'max_msg_size_unit',
        'recv_timeout',
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
        filterValue: 'channel-hl7-mllp'
    },

// ////////////////////////////////////////////////////////////////////////

    onInit: function() {

        // The transport, REST and routing cards on step 1 ..
        wizard.forms.initCards();

        // .. the destination rows and the option cards on step 2 ..
        wizard.destinations.init();
        wizard.review.initOptionCards();

        // .. the searchable select for services ..
        $.fn.zato.turn_selects_into_chosen('#mllp-wizard-service-row');

        // .. a live uniqueness indicator for the REST URL path - the name
        // has its own check through the kit config above ..
        $.fn.zato.validate_unique('#id_rest_url_path', 'channel_rest', 'url_path');

        // .. keep the services and the security definitions fresh while
        // the page is open - no reloading to pick up new ones ..
        $.fn.zato.live_form_updates.register('create', [
            {object_type: 'service', target_select: '#id_service'},
            {object_type: 'security', target_select: '#id_rest_security_id'}
        ]);
        $.fn.zato.live_form_updates.start('create');

        // .. an open REST popover clones the security select into its rows,
        // so a live update to the underlying form select re-clones them.
        $('#id_rest_security_id').on('chosen:updated', function() {
            wizard.forms.refreshSecuritySelect();
        });
    },

// ////////////////////////////////////////////////////////////////////////

    beforeSave: function(form) {

        // The destination rows travel in hidden JSON fields the backend reads ..
        wizard.destinations.serialize();

        // .. so do the security definitions picked for the REST bridge.
        wizard._writeSecurityIdInputs(form);
    }
});

// ////////////////////////////////////////////////////////////////////////

// The help texts behind every "How does it work?" badge on the page -
// the map the full-page editor uses, re-keyed for the popover inputs,
// plus entries for the controls only the wizard has.
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

    // .. and the step 2 destination controls.
    out['mllp-wizard-respond-from'] = shared['destinations-respond-from-create'];
    out['mllp-wizard-destination-type'] = 'The kind of the outgoing connection<br>this destination delivers to.';
    out['mllp-wizard-destination-connection'] = 'The connection each message is delivered to<br>after the service runs.';
    out['mllp-wizard-destination-active'] = 'Whether this destination receives messages.<br>Inactive destinations are skipped.';

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
// it creates on its own. A single pick stays in the rest_security_id
// select alone, exactly the way the full-page editor posts it.
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
