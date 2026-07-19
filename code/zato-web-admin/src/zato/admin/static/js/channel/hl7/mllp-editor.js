// HL7 MLLP channel editor - the full-page create and edit forms.
//
// The page is rendered by zato/channel/hl7/mllp-editor.html, one page per
// action, and posts to the same create/edit endpoints that the channel list
// page used to call from its popup dialogs. After a successful save the
// browser goes back to the list page with the saved channel highlighted.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.editor.config = {

    // Messages shown next to the OK button after a save attempt
    saved_message: 'OK, saved',
    save_error_message: 'Could not save',

    // How long the success message stays on screen before the redirect
    redirect_delay_ms: 750,

    // Where the security groups for the REST bridge come from
    security_groups_url: '/zato/http-soap/get-security-groups/zato-api-creds/',
    security_groups_page_url: '/zato/groups/group/zato-api-creds/?cluster=1',
    security_groups_link_url: '/zato/groups/group/zato-api-creds/?cluster=1&query={1}&highlight={2}',

    // Fields that must not be empty on submit
    required_fields: [
        'name',
        'service',
        'logging_level',
        'max_msg_size',
        'max_msg_size_unit',
        'read_buffer_size',
        'recv_timeout',
        'start_seq',
        'end_seq',
        'default_character_encoding'
    ],

    // The tab strip, in display order
    tab_labels: {
        main:         'Main',
        destinations: 'Destinations',
        routing:      'Routing',
        protocol:     'Protocol',
        tolerance:    'Tolerance',
        dedup:        'Deduplication',
        logging:      'Logging'
    }
};

// Filled in by init() - which action this page serves and where its list page is
$.fn.zato.channel.hl7.mllp.editor.state = {
    action: '',
    list_url: ''
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.editor.field_descriptions = {

    // Main tab
    'id_name': 'A unique name for this MLLP channel.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this channel accepts connections.<br>Inactive channels do not route messages.',
    'id_service': 'The service invoked for each<br>incoming HL7 message.',
    'id_use_rest': 'When on, HL7 messages can also be received<br>over REST in addition to MLLP.',
    'id_rest_only': 'When on, messages are received only over REST.<br>When off, messages are received over both<br>MLLP and REST.',
    'id_rest_url_path': 'URL path for the REST channel,<br>e.g. /api/hl7/v2.',
    'id_rest_security_id': 'Security definition used to authenticate<br>incoming REST requests.',
    'id_rest_security_groups': 'Security groups that can access<br>the REST channel.',

    // Destinations tab
    'destinations-respond-from-create': 'What the caller receives in response -<br>what the service returns or the response<br>of one, synchronously delivered, destination.',
    'destinations-respond-from-edit': 'What the caller receives in response -<br>what the service returns or the response<br>of one, synchronously delivered, destination.',

    // Routing tab
    'id_is_default': 'When enabled, this channel receives all messages<br>that no other channel claimed. Only one channel<br>can be the default at a time.',
    'id_msh3_sending_app': 'Only accept messages where MSH-3<br>(sending application) equals this value.<br>Empty means any. Case-insensitive.',
    'id_msh4_sending_facility': 'Only accept messages where MSH-4<br>(sending facility) equals this value.<br>Empty means any. Case-insensitive.',
    'id_msh5_receiving_app': 'Only accept messages where MSH-5<br>(receiving application) equals this value.<br>Empty means any. Case-insensitive.',
    'id_msh6_receiving_facility': 'Only accept messages where MSH-6<br>(receiving facility) equals this value.<br>Empty means any. Case-insensitive.',
    'id_msh9_message_type': 'Only accept messages where MSH-9.1<br>(message type, e.g. ADT, ORM) equals this value.<br>Empty means any. Case-insensitive.',
    'id_msh9_trigger_event': 'Only accept messages where MSH-9.2<br>(trigger event, e.g. A01, O01) equals this value.<br>Empty means any. Case-insensitive.',
    'id_msh11_processing_id': 'Only accept messages where MSH-11<br>(P=production, T=training, D=debugging)<br>equals this value. Empty means any. Case-insensitive.',
    'id_msh12_version_id': 'Only accept messages where MSH-12<br>(HL7 version, e.g. 2.5) equals this value.<br>Empty means any. Case-insensitive.',

    // Protocol tab
    'id_use_msh18_encoding': 'When on, the server reads the character encoding<br>from the MSH-18 field of each incoming message.<br>When off, or if MSH-18 is empty, the Encoding<br>setting below is used instead.',
    'id_default_character_encoding': 'Character encoding used to decode raw bytes<br>when MSH-18 is absent or the MSH-18 toggle is off.',
    'id_recv_timeout': 'Per-recv timeout in milliseconds.<br>The connection stays open between messages.',
    'id_max_msg_size': 'Maximum allowed message size.<br>Frames exceeding this are rejected.',
    'id_start_seq': 'MLLP start-of-block byte in hex.<br>Standard: 0b.',
    'id_end_seq': 'MLLP end-of-block bytes in hex.<br>Standard: 1c 0d.',

    // Tolerance tab - wire-level preprocessing
    'id_normalize_line_endings': 'Converts CRLF and LF to CR<br>as required by HL7 v2.',
    'id_force_standard_delimiters': 'Rewrites MSH-2 to standard delimiters<br>(^~\\&amp;).',
    'id_repair_truncated_msh': 'Recovers messages with a corrupted<br>or malformed MSH segment.',
    'id_split_concatenated_messages': 'Splits a TCP payload containing multiple<br>MSH segments into separate messages.',

    // Tolerance tab - parser-level fixups
    'id_normalize_obx2_value_type': 'When OBX-2 is empty but OBX-5 has data,<br>fills OBX-2 with ST so the observation<br>value can be accessed.',
    'id_replace_invalid_obx2_value_type': 'Replaces unrecognized OBX-2 data types<br>with ST. Prevents parse failures from<br>nonstandard value type codes.',
    'id_normalize_invalid_escape_sequences': 'Removes stray backslash characters that<br>do not form a valid HL7 escape sequence.<br>Prevents parse errors from malformed escapes.',
    'id_normalize_obx8_abnormal_flags': 'Clears OBX-8 (Abnormal Flags) when it<br>contains the literal string "null" instead<br>of a valid flag value.',
    'id_normalize_quadruple_quoted_empty': 'Strips sequences of two or more consecutive<br>double-quote characters that some systems<br>emit as empty-field placeholders.',
    'id_allow_short_encoding_characters': 'Pads MSH-2 with standard encoding characters<br>when the sender provides fewer than the<br>required four.',
    'id_fix_off_by_one_field_index': 'Removes a spurious empty first field from<br>non-MSH segments. Fixes messages where a<br>leading separator shifts all field indices.',

    // Deduplication tab
    'id_dedup_ttl_value': 'How long to remember message control IDs (MSH-10).<br>Duplicates within this window are acknowledged<br>but not delivered to the service.',
    'id_dedup_ttl_unit': 'Time unit for the dedup window<br>(minutes, hours, or days).',

    // Logging tab
    'id_should_return_errors': 'When on, error details are included<br>in NAK responses sent to the sender (ERR segment).<br>When off, the NAK code is sent without details.',
    'id_should_log_messages': 'When on, each incoming message body and<br>routing decision is written to the server log<br>(server.log in the server directory).',
    'id_logging_level': 'Verbosity level for this channel\'s entries<br>in the server log (server.log).'
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.editor._toggle_groups = function(selector) {
    var groupsBlock = $(selector);
    if(groupsBlock.is(':visible')) {
        groupsBlock.hide();
    }
    else {
        groupsBlock.css('display', '');
        groupsBlock.show();
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.editor._routing_fields = [
    'msh3_sending_app',
    'msh4_sending_facility',
    'msh5_receiving_app',
    'msh6_receiving_facility',
    'msh9_message_type',
    'msh9_trigger_event',
    'msh11_processing_id',
    'msh12_version_id'
];

$.fn.zato.channel.hl7.mllp.editor._toggle_routing_fields = function(prefix) {
    var is_default = $('#' + prefix + 'is_default').is(':checked');
    var fields = $.fn.zato.channel.hl7.mllp.editor._routing_fields;
    for(var fieldIdx = 0; fieldIdx < fields.length; fieldIdx++) {
        var input = $('#' + prefix + fields[fieldIdx]);
        input.prop('readonly', is_default);
        input.toggleClass('routing-disabled', is_default);
    }
};

$.fn.zato.channel.hl7.mllp.editor._bind_default_toggle = function(prefix) {
    var checkbox = $('#' + prefix + 'is_default');
    checkbox.off('change.routing').on('change.routing', function() {
        $.fn.zato.channel.hl7.mllp.editor._toggle_routing_fields(prefix);
    });
    $.fn.zato.channel.hl7.mllp.editor._toggle_routing_fields(prefix);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.editor._toggle_rest_fields = function(form_selector) {
    var checkbox = $(form_selector).find('input[name$="use_rest"]');
    var rows = $(form_selector).find('tr.rest-field');
    if(checkbox.is(':checked')) {
        rows.css('display', 'table-row');
    }
    else {
        rows.css('display', 'none');
        $(form_selector).find('.mllp-create-groups-block, .mllp-edit-groups-block').hide();
    }
};

$.fn.zato.channel.hl7.mllp.editor._bind_rest_toggle = function(form_selector) {
    var checkbox = $(form_selector).find('input[name$="use_rest"]');
    checkbox.off('change.rest').on('change.rest', function() {
        $.fn.zato.channel.hl7.mllp.editor._toggle_rest_fields(form_selector);
    });
    $.fn.zato.channel.hl7.mllp.editor._toggle_rest_fields(form_selector);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.editor._populate_groups_callback = function(data, status) {

    if(status != 'success') {
        return;
    }

    var editor = $.fn.zato.channel.hl7.mllp.editor;
    var action = editor.state.action;

    // The checkbox names carry the same prefix the form's other fields use
    var checkboxPrefix = action === 'edit' ? 'edit-mllp_security_group_checkbox_' : 'mllp_security_group_checkbox_';

    var itemList = $.parseJSON(data.responseText);

    if(itemList && itemList.length) {
        $.fn.zato.populate_multi_checkbox(
            itemList,
            checkboxPrefix,
            'id',
            'name',
            'is_assigned',
            editor.config.security_groups_link_url,
            'multi-select-table',
            '#mllp-multi-select-div-' + action,
            'id',
            false
        );
    }
    else {
        var container = $('#mllp-multi-select-div-' + action);
        container.removeClass('multi-select-div');
        container.html('No security groups found. Click to <a href="' + editor.config.security_groups_page_url +
            '" target="_blank">create one</a>.');
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.editor.init = function(options) {

    var editor = $.fn.zato.channel.hl7.mllp.editor;
    var action = options.action;

    editor.state.action = action;
    editor.state.list_url = options.list_url;

    var prefix = action === 'edit' ? 'id_edit-' : 'id_';
    var form = $('#' + action + '-form');

    // The tab strip - the same engine the popup dialogs used, pointed at the page container ..
    $.fn.zato.form_tabs.reset({
        div_id: '#mllp-editor',
        panel_prefix: 'mllp-editor-tab-panel-',
        default_tab: 'main',
        tab_labels: editor.config.tab_labels
    });

    // .. mark the fields that must not be empty ..
    for(var fieldIdx = 0; fieldIdx < editor.config.required_fields.length; fieldIdx++) {
        $.fn.zato.data_table.set_field_required('#' + prefix + editor.config.required_fields[fieldIdx]);
    }

    // .. when editing, fill the form in from the channel's current values ..
    if(action === 'edit') {
        $.fn.zato.form.populate(form, options.item, 'edit-', '#id_edit-');
    }

    // .. the destinations tab reads its rows from the hidden JSON fields ..
    $.fn.zato.destinations.init(action);

    // .. security groups for the REST bridge arrive asynchronously ..
    $.fn.zato.post(editor.config.security_groups_url, editor._populate_groups_callback, '', '', true);

    // .. the Default and Use REST checkboxes drive other fields' visibility ..
    editor._bind_default_toggle(prefix);
    editor._bind_rest_toggle('#' + action + '-form');

    // .. searchable selects for services and security definitions ..
    $.fn.zato.turn_selects_into_chosen('#mllp-editor');

    // .. the per-field help badge ..
    $.fn.zato.how_it_works.init({
        badgeId: 'mllp-editor-how-it-works',
        divId: '#mllp-editor',
        descriptions: editor.field_descriptions
    });

    // .. live uniqueness indicators ..
    $.fn.zato.validate_unique('#' + prefix + 'name', 'generic_connection', 'name');
    $.fn.zato.validate_unique('#' + prefix + 'rest_url_path', 'channel_rest', 'url_path');

    // .. keep the service and security selects fresh while the page is open ..
    $.fn.zato.live_form_updates.register(action, [
        {object_type: 'service', target_select: '#' + prefix + 'service'},
        {object_type: 'security', target_select: '#' + prefix + 'rest_security_id'},
        {
            object_type: 'security_group',
            handler: 'multi_checkbox',
            container: '#mllp-multi-select-div-' + action,
            reload_callback: function() {
                $.fn.zato.post(editor.config.security_groups_url, editor._populate_groups_callback, '', '', true);
            }
        }
    ]);
    $.fn.zato.live_form_updates.start(action);

    // .. and finally the submit and cancel actions.
    form.submit(function() {
        editor.save();
        return false;
    });

    $('#mllp-editor-cancel').on('click', function() {
        window.location.href = editor.state.list_url;
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.editor.save = function() {

    var editor = $.fn.zato.channel.hl7.mllp.editor;
    var action = editor.state.action;
    var form = $('#' + action + '-form');

    // The destinations rows travel in hidden JSON fields the backend reads ..
    $.fn.zato.destinations._serialize(action);

    // .. client-side validation first ..
    if(!$.fn.zato.is_form_valid(form)) {
        return;
    }

    // .. then the synchronous uniqueness checks ..
    if(!$.fn.zato.validate_unique_on_submit(form)) {
        return;
    }

    var statusElem = $('#mllp-editor-status');
    statusElem.removeClass('show fade status-message-success status-message-error');

    var callback = function(data, status) {

        if(status === 'success') {
            var response = JSON.parse(data.responseText);
            statusElem.text(editor.config.saved_message).addClass('show status-message-success');
            $('#user-message-div').hide();

            // Back to the list page, with the saved channel highlighted
            setTimeout(function() {
                window.location.href = editor.state.list_url + '&highlight=' + response.id;
            }, editor.config.redirect_delay_ms);
        }
        else {
            statusElem.text(editor.config.save_error_message).addClass('show status-message-error');
            $.fn.zato.user_message(false, data.responseText);
        }
    };

    // .. and the actual POST to the create or edit endpoint.
    $.fn.zato.data_table._on_submit(form, callback);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
