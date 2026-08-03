// HL7 MLLP channel - the MSH fields a channel matches incoming messages on.
//
// The wizard edits them on its Match row and the channel list edits them in
// its Match column, both through the same popover micro-form, so what the
// fields are, what the form looks like and how the whole match is written
// out in one line all live here rather than on either page.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var matchers = {};
$.fn.zato.channel.hl7.mllp.matchers = matchers;

// ////////////////////////////////////////////////////////////////////////

// What a channel filling in none of them is said to take
matchers.anyLabel = 'All messages';

// The title of the popover the fields are edited in, and how wide it opens
matchers.formTitle = 'Message matchers';
matchers.formWidth = '430px';

// ////////////////////////////////////////////////////////////////////////

// The fields in MSH order - the full label names the field on a review page,
// the short one is what a one-line match has room for.
matchers.fields = [
    {field: 'msh3_sending_app',        label: 'MSH-3 sending application',  short: 'MSH-3'},
    {field: 'msh4_sending_facility',   label: 'MSH-4 sending facility',     short: 'MSH-4'},
    {field: 'msh5_receiving_app',      label: 'MSH-5 receiving application', short: 'MSH-5'},
    {field: 'msh6_receiving_facility', label: 'MSH-6 receiving facility',   short: 'MSH-6'},
    {field: 'msh9_message_type',       label: 'MSH-9.1 message type',       short: 'MSH-9.1'},
    {field: 'msh9_trigger_event',      label: 'MSH-9.2 trigger event',      short: 'MSH-9.2'},
    {field: 'msh11_processing_id',     label: 'MSH-11 processing ID',       short: 'MSH-11'},
    {field: 'msh12_version_id',        label: 'MSH-12 version',             short: 'MSH-12'}
];

// ////////////////////////////////////////////////////////////////////////

// The micro-form the fields are edited in, two to a row in MSH order
matchers.descriptor = {
    title: matchers.formTitle,
    width: matchers.formWidth,
    pages: [[
        [
            {field: 'msh3_sending_app',        label: 'Sending application (MSH-3)',  kind: 'text'},
            {field: 'msh4_sending_facility',   label: 'Sending facility (MSH-4)',     kind: 'text'}
        ],
        [
            {field: 'msh5_receiving_app',      label: 'Receiving application (MSH-5)', kind: 'text'},
            {field: 'msh6_receiving_facility', label: 'Receiving facility (MSH-6)',   kind: 'text'}
        ],
        [
            {field: 'msh9_message_type',   label: 'Message type (MSH-9.1)',  kind: 'text', placeholder: 'e.g. ORU'},
            {field: 'msh9_trigger_event',  label: 'Trigger event (MSH-9.2)', kind: 'text', placeholder: 'e.g. R01'}
        ],
        [
            {field: 'msh11_processing_id', label: 'Processing ID (MSH-11)',  kind: 'text', placeholder: 'e.g. P'},
            {field: 'msh12_version_id',    label: 'Version (MSH-12)',        kind: 'text', placeholder: 'e.g. 2.5'}
        ]
    ]]
};

// ////////////////////////////////////////////////////////////////////////

// Says in one line which messages a channel takes - each matcher it fills in
// narrows what reaches it, a matcher left empty matching anything. The caller
// says where a field's value is read from, a page keeping them wherever it does.
matchers.summary = function(getValue) {

    var parts = [];

    for(var fieldIdx = 0; fieldIdx < matchers.fields.length; fieldIdx++) {
        var matcher = matchers.fields[fieldIdx];
        var value = getValue(matcher.field).trim();

        if(value) {
            parts.push(matcher.short + ' = ' + value);
        }
    }

    if(!parts.length) {
        var out = matchers.anyLabel;
        return out;
    }

    var out = parts.join(', ');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
