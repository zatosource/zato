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

    // The tab shown when the URL does not name one
    default_tab: 'main',

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
    ]
};

// Filled in by init() - which action this page serves and where its list page is
$.fn.zato.channel.hl7.mllp.editor.state = {
    action: '',
    list_url: '',
    tab_handle: null
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
    var kit = $.fn.zato.dashboard_kit;
    var action = options.action;

    editor.state.action = action;
    editor.state.list_url = options.list_url;

    var prefix = action === 'edit' ? 'id_edit-' : 'id_';
    var form = $('#' + action + '-form');

    // The tab strip - the same engine the posture page uses, with the tab kept in the URL ..
    var defaultTab = kit.url_state.get('tab');
    if(!defaultTab) {
        defaultTab = editor.config.default_tab;
    }

    editor.state.tab_handle = kit.tabs.init({
        tab_selector: '.mllp-editor-card .dashboard-tab',
        panel_prefix: 'mllp-editor-tab-panel-',
        default_tab: defaultTab,
        on_change: function(tabName) {
            kit.url_state.set({tab: tabName});
        }
    });

    // .. handle browser back/forward ..
    kit.url_state.on_pop(function(params) {
        var popTab = params.get('tab');
        if(popTab) {
            editor.state.tab_handle.set_tab(popTab, true);
        }
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

    // .. the per-field help badge - the texts come from mllp-descriptions.js,
    // the map the wizard shares ..
    $.fn.zato.how_it_works.init({
        badgeId: 'mllp-editor-how-it-works',
        divId: '#mllp-editor',
        descriptions: $.fn.zato.channel.hl7.mllp.field_descriptions
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

    // .. the submit and cancel actions ..
    form.submit(function() {
        editor.save();
        return false;
    });

    $('#mllp-editor-cancel').on('click', function() {
        window.location.href = editor.state.list_url;
    });

    // .. and fade the page in.
    kit.reveal();
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
    statusElem.text('').removeClass('mllp-editor-status-saved mllp-editor-status-error');

    var callback = function(data, status) {

        if(status === 'success') {
            var response = JSON.parse(data.responseText);
            statusElem.text(editor.config.saved_message).addClass('mllp-editor-status-saved');
            $('#user-message-div').hide();

            // Back to the list page, with the saved channel highlighted
            setTimeout(function() {
                window.location.href = editor.state.list_url + '&highlight=' + response.id;
            }, editor.config.redirect_delay_ms);
        }
        else {
            statusElem.text(editor.config.save_error_message).addClass('mllp-editor-status-error');
            $.fn.zato.user_message(false, data.responseText);
        }
    };

    // .. and the actual POST to the create or edit endpoint.
    $.fn.zato.data_table._on_submit(form, callback);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
