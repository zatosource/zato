
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Everything a row of an HTTP/SOAP listing changes without leaving the page - the four pages
// this serves (REST and SOAP channels, REST and SOAP outgoing connections) all post to the
// same endpoint, each page filling in its own connection and transport below.
$.fn.zato.http_soap.inline = {};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.inline.config = {

    // Which of the four listings this page is - written in by the page itself
    connection: '',
    transport: '',

    // Where a row goes when it is edited where it stands, its id following it
    inline_edit_url: '/zato/http-soap/inline-edit/',

    // Where the security groups of one channel come from, the channel's id following it
    groups_url: '/zato/http-soap/get-security-groups/zato-api-creds/?http_soap_channel_id=',

    // Where a service is opened
    service_ide_url: '/zato/service/ide/service/{name}/?cluster=1',

    // The things a cell's popup offers, one to a button
    open_ide_label: 'Open in IDE',
    change_service_label: 'Change service',
    go_to_definition_label: 'Go to definition',
    change_definition_label: 'Change definition',
    menu_theme: 'light',
    menu_placement: 'left',

    // Where the page's security select lives and under which name a row keeps
    // its composite value - the outgoing SOAP page overrides both
    security_select: '#id_edit-security',
    security_attr: 'security',

    // Whether the security cell names the definition's type above its name,
    // the way the outgoing SOAP listing does
    show_sec_type_in_cell: false,

    // The single-pick panels and how their filters speak
    filter_label: 'Filter',
    service_panel_title: 'Service',
    service_filter_placeholder: 'Type to filter the services',
    security_panel_title: 'Security definition',
    security_filter_placeholder: 'Type to filter the definitions',
    panel_width: 420,
    panel_min_width: 320,
    service_panel_key: 'http-soap-row-service-panel',
    security_panel_key: 'http-soap-row-security-panel',

    // The one popup a channel's security cell opens - the definition picker and
    // the groups badge picker inside it, the IDE's own action-menu layout with
    // the list on the left and the live pane on the right
    security_menu_title: 'Security',
    security_menu_key: 'http-soap-row-security-menu',
    definition_pane_label: 'Definition',
    groups_pane_label: 'Groups',

    // The groups pane and the badge picker inside it
    groups_filter_placeholder: 'Filter groups...',
    groups_panel_width: 640,
    groups_panel_min_width: 420,
    groups_element_action: 'http-soap-groups',

    // What a picker cell says when its list could not be brought over
    load_error_label: 'Could not load the list',

    // What a pane says when there is nothing to pick from
    definitions_empty_message: 'No security definitions are available',
    groups_empty_message: 'No security groups are available',

    // What a cell with no security definition says - clicking it opens the picker
    empty_security_label: 'Click to add',

    // How long a confirmation takes to fade once it has been read
    confirmation_fade_ms: 200,

    // What the flag reads as, in the order a boolean puts them
    flag_labels: ['No', 'Yes']
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// What the uniqueness checks are scoped to - each of the four listings keeps names
// and URL paths of its own
$.fn.zato.http_soap.inline.entity_type = function() {

    var config = $.fn.zato.http_soap.inline.config;

    var side = config.connection === 'channel' ? 'channel_' : 'outgoing_';
    var kind = config.transport === 'plain_http' ? 'rest' : 'soap';

    var out = side + kind;
    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Says beside a row that it went through, for as long as that takes to read
$.fn.zato.http_soap.inline.flash = function(link, message) {

    var config = $.fn.zato.inline_edit.config;

    var instance = tippy(link, {
        content: message,
        theme: 'dark',
        trigger: 'manual',
        placement: config.confirmation_placement,
        hideOnClick: false,
        allowHTML: false
    });

    instance.show();

    // The tooltip leaves nothing of itself behind
    setTimeout(function() {
        instance.hide();
        setTimeout(function() {
            instance.destroy();
        }, $.fn.zato.http_soap.inline.config.confirmation_fade_ms);
    }, config.saved_hide_ms);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Sends what one row changed and hands the answer over to whoever asked for the save
$.fn.zato.http_soap.inline.save = function(link, id, data, on_saved, saved_label) {

    var inline = $.fn.zato.http_soap.inline;
    var config = $.fn.zato.inline_edit.config;
    var url = inline.config.inline_edit_url + id + '/';

    // The one endpoint serves all four listings, told apart by these two
    data['connection'] = inline.config.connection;
    data['transport'] = inline.config.transport;

    $.fn.zato.action_runner.run({
        link_elem: link,
        url: url,
        data: data,
        spinner_label: config.saving_label,
        details_modal_title: config.details_modal_title,
        show_delay_ms: config.saving_lead_in_ms,

        // The endpoint answers with JSON when it saved and with an error page when it did not
        parse: function(jqXHR) {

            var is_http_ok = (jqXHR.status >= 200 && jqXHR.status < 300);

            return {
                is_success: is_http_ok,
                label: is_http_ok ? saved_label : config.error_label,
                details_title: config.error_label,
                details_body: jqXHR.responseText,
                details_lexer: '',
                status_code: jqXHR.status,
                jqXHR: jqXHR
            };
        },

        on_success: function(instance, result) {

            // The spinner makes way for the confirmation
            instance.hide();
            instance.destroy();

            on_saved(JSON.parse(result.jqXHR.responseText));

            $.fn.zato.http_soap.inline.flash(link, saved_label);
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Yes or No, the way a row shows a flag of its own
$.fn.zato.http_soap.inline.flag_label = function(value) {
    var out = $.fn.zato.http_soap.inline.config.flag_labels[value ? 1 : 0];
    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Turns the active flag of one row over, the opposite of what the row stands at being what is sent
$.fn.zato.http_soap.inline.toggle_active = function(id, link) {

    var inline = $.fn.zato.http_soap.inline;
    var instance = $.fn.zato.data_table.data[id];

    var data = {
        'is_active': !$.fn.zato.to_bool(instance.is_active)
    };

    var on_saved = function(saved) {

        // The row stands at what came back
        instance.is_active = saved.is_active;
        link.textContent = inline.flag_label(saved.is_active);
    };

    inline.save(link, id, data, on_saved, $.fn.zato.inline_edit.config.saved_label);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// One line of one row, edited in the small form the MCP list and the scheduler use,
// opened right above the value it changes
$.fn.zato.http_soap.inline._edit_text = function(id, link, name, label, unique, is_required, write_cell) {

    var inline = $.fn.zato.http_soap.inline;
    var instance = $.fn.zato.data_table.data[id];

    $.fn.zato.inline_edit.form_tippy({
        link_elem: link,
        title: label,
        input_width: '18em',
        rows: [
            {name: name, label: label, value: instance[name], unique: unique}
        ],
        validate: function(values) {
            if(is_required && !values[name]) {
                return 'This field is required: ' + label;
            }
            return '';
        },
        on_submit: function(values) {

            var data = {};
            data[name] = values[name];

            var on_saved = function(saved) {

                // The row stands at what came back
                instance[name] = saved[name];
                write_cell(saved[name]);
            };

            inline.save(link, id, data, on_saved, $.fn.zato.inline_edit.config.saved_label);
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.inline.edit_name = function(id, link) {

    var inline = $.fn.zato.http_soap.inline;

    // Names are unique within the listing's own kind of object
    var unique = {entity_type: inline.entity_type(), attr_name: 'name'};

    var write_cell = function(value) {
        link.querySelector('.name-value').textContent = value;
    };

    inline._edit_text(id, link, 'name', 'Name', unique, true, write_cell);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.inline.edit_url_path = function(id, link) {

    var inline = $.fn.zato.http_soap.inline;
    var is_channel = inline.config.connection === 'channel';
    var instance = $.fn.zato.data_table.data[id];

    // Only channels keep their URL paths unique, and the check runs against the same
    // method and Accept header the create service compares
    var unique = null;

    if(is_channel) {
        unique = {entity_type: inline.entity_type(), attr_name: 'url_path', filter: function() {
            return {
                'method': instance.method,
                'http_accept': instance.http_accept
            };
        }};
    }

    var write_cell = function(value) {
        link.textContent = value;
    };

    inline._edit_text(id, link, 'url_path', 'URL path', unique, is_channel, write_cell);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
