
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OnPremGateway = new Class({
    toString: function() {
        var s = '<OnPremGateway id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.status = {
    notEnrolled: 'Not enrolled'
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.config = {

    // The range that a port number is required to fall in
    port_min: 1,
    port_max: 65535,

    // Where a validation message is displayed in relation to the field it concerns
    error_placement: 'bottom',

    // Where the outcome of an action is displayed in relation to the link that invoked it,
    // and for how long a confirmation of success remains visible
    message_placement: 'top',
    success_visible_ms: 1500,

    // What a cell without a value displays, matching the no_value_indicator template filter
    no_value_html: '<span class="form_hint">---</span>',

    // The links in a row that outcomes are reported beside
    create_link_selector: 'a[href*="on_prem_gateway.create"]',
    edit_link_text: 'Edit',
    enrollment_token_link_text: 'Enrollment token',
    reset_key_link_text: 'Reset key',

    format_error: '`{0}` is not in the host:port format',
    host_error: '`{0}` does not specify a host',
    port_error: '`{0}` does not specify a numeric port',
    port_range_error: '`{0}` specifies a port outside the {1}-{2} range',
    duplicate_error: '`{0}` is listed more than once'
};

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.OnPremGateway;
    $.fn.zato.data_table.new_row_func = $.fn.zato.on_prem_gateway.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name']);
    $.fn.zato.data_table.before_submit_hook = $.fn.zato.on_prem_gateway.before_submit_hook;
    $.fn.zato.data_table._on_submit_complete = $.fn.zato.on_prem_gateway.on_submit_complete;

    $('#enrollment_token-div').dialog({
        autoOpen: false,
        width: '40em'
    });

    $('#enrollment-token-copy').on('click', function() {
        $.fn.zato.ui_helpers.copy_to_clipboard(this, $('#enrollment-token-value').val());
    });

    // A message left behind by a rejected attempt does not outlive the dialog it was shown in
    $.each({'#create-div':'', '#edit-div':'edit-'}, function(divId, prefix) {
        $(divId).on('dialogclose', function() {
            $.fn.zato.on_prem_gateway.clear_field_error($('#id_' + prefix + 'hosts'));
        });
    });

    var uniqueConstraints = [
        {field: 'name', entity_type: 'on_prem_gateway', attr_name: 'name'}
    ];

    $.each(uniqueConstraints, function(constraintIndex, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.field_descriptions = {
    'id_name': 'The unique name of the gateway. Enrollment tokens are issued per gateway name ' +
        'and each instance enrolled under this name serves the same set of addresses.',
    'id_is_active': 'Determines whether the environment accepts connections from this gateway. ' +
        'An inactive gateway is disconnected and its addresses cease to resolve.',
    'id_is_key_reset_required': 'Determines whether an enrolled gateway enrolls again only after its key ' +
        'has been reset. When disabled, a new enrollment token replaces the key on file, for instance ' +
        'when the gateway is reinstalled or moved to another host.',
    'id_hosts': 'The on-premises addresses served by this gateway, one host:port entry per line, ' +
        'for example erp-db.corp.local:5432. Each entry is resolvable within the Zato environment, ' +
        'so an outgoing connection configured with the same host and port is transported over the ' +
        'gateway connection. The list also constitutes an allowlist and connections to addresses ' +
        'outside it are refused.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.how_it_works_placement = 'left';

// /////////////////////////////////////////////////////////////////////////////

// Applies to the list of addresses the same rules as the server, so that an invalid
// entry is reported in the form instead of by a rejected request. Returns an empty
// string when the list is valid.
$.fn.zato.on_prem_gateway.get_hosts_error = function(value) {

    var config = $.fn.zato.on_prem_gateway.config;
    var lines = value.split('\n');
    var seen = {};

    for(var lineIndex = 0; lineIndex < lines.length; lineIndex++) {

        var item = lines[lineIndex].trim();

        if(!item) {
            continue;
        }

        var separator = item.lastIndexOf(':');

        if(separator === -1) {
            return String.format(config.format_error, item);
        }

        var host = item.substring(0, separator).trim();
        var port = item.substring(separator + 1).trim();

        if(!host) {
            return String.format(config.host_error, item);
        }

        if(!/^\d+$/.test(port)) {
            return String.format(config.port_error, item);
        }

        var portNumber = parseInt(port, 10);

        if(portNumber < config.port_min || portNumber > config.port_max) {
            return String.format(config.port_range_error, item, config.port_min, config.port_max);
        }

        var address = host + ':' + portNumber;

        if(seen[address]) {
            return String.format(config.duplicate_error, item);
        }

        seen[address] = true;
    }

    return '';
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.show_field_error = function(field, message) {

    var element = field.get(0);

    // A message from a previous attempt is replaced rather than stacked upon
    if(element._tippy) {
        element._tippy.destroy();
    }

    $.fn.zato.draw_attention_to(field);
    $.fn.zato.show_tooltip_common($.fn.zato.on_prem_gateway.config.error_placement, '#' + element.id, message, false);

    // The message concerns the value as it was, so editing it withdraws the message
    field.off('input.on_prem_gateway').on('input.on_prem_gateway', function() {
        $.fn.zato.on_prem_gateway.clear_field_error(field);
    });

    field.focus();
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.clear_field_error = function(field) {

    var element = field.get(0);

    if(element._tippy) {
        element._tippy.destroy();
    }

    // Only the highlight is withdrawn here, the field keeps the placeholder it was rendered with
    $.fn.zato.remove_css_attention(field);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.before_submit_hook = function(form) {

    var prefix = $(form).attr('id').indexOf('edit') === -1 ? '' : 'edit-';
    var field = $('#id_' + prefix + 'hosts');

    $.fn.zato.on_prem_gateway.clear_field_error(field);

    var error = $.fn.zato.on_prem_gateway.get_hosts_error(field.val());

    if(error) {
        $.fn.zato.on_prem_gateway.show_field_error(field, error);
        return false;
    }

    return true;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new on-premises gateway', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        placement: $.fn.zato.on_prem_gateway.how_it_works_placement,
        descriptions: $.fn.zato.on_prem_gateway.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the on-premises gateway', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        placement: $.fn.zato.on_prem_gateway.how_it_works_placement,
        descriptions: $.fn.zato.on_prem_gateway.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var isActive = item.is_active == true;

    // A row constructed here reflects the configuration only, the runtime state is
    // reported by the hub on the next read of the list.
    var hostCount = item.hosts ? item.hosts.split('\n').length : 0;

    // Enrollment requires a token, which is therefore issued immediately after creation.
    // The identifier is available only once the server has responded, so the callback
    // is registered here rather than in the create function.
    if(include_tr) {
        $.fn.zato.data_table.on_submit_complete_callback = $.fn.zato.on_prem_gateway.enrollment_token;
        $.fn.zato.data_table.on_submit_complete_callback_args = item.id;
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', isActive ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', $.fn.zato.on_prem_gateway.status.notEnrolled);
    row += String.format('<td>{0}</td>', hostCount);
    row += String.format('<td>{0}</td>', $.fn.zato.on_prem_gateway.config.no_value_html);
    row += String.format('<td>{0}</td>', $.fn.zato.on_prem_gateway.config.no_value_html);
    row += String.format('<td>{0}</td>', $.fn.zato.on_prem_gateway.config.no_value_html);
    row += String.format('<td>{0}</td>', $.fn.zato.on_prem_gateway.config.no_value_html);

    // 2
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.on_prem_gateway.enrollment_token('{0}')\">Enrollment token</a>", item.id));
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.on_prem_gateway.reset_key('{0}')\">Reset key</a>", item.id));
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.on_prem_gateway.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.on_prem_gateway.delete_('{0}');\">Delete</a>", item.id));

    // 3
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.hosts);
    row += String.format("<td class='ignore'>{0}</td>", item.is_key_reset_required);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

// Reports the outcome of an action in a tooltip beside the link that invoked it. A failure
// remains visible until dismissed, a success is withdrawn on its own.
$.fn.zato.on_prem_gateway.show_message = function(anchor, message, isSuccess) {

    var config = $.fn.zato.on_prem_gateway.config;
    var element = anchor.get(0);

    if(element._tippy) {
        element._tippy.destroy();
    }

    var instance = tippy(element, {
        content: message,
        allowHTML: false,
        theme: 'dark',
        trigger: 'manual',
        placement: config.message_placement,
        arrow: true,
        interactive: false,
        inertia: true,

        // A confirmation of success is not cut short by a click elsewhere on the page
        hideOnClick: !isSuccess,

        // The visible period is counted from the end of the show animation, not its start
        onShown: function(instance) {
            if(isSuccess) {
                setTimeout(function() {
                    instance.hide();
                }, config.success_visible_ms);
            }
        },
        onHidden: function(instance) {
            instance.destroy();
        }
    });

    instance.show();
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.get_row_link = function(id, text) {

    var links = $('#tr_' + id + ' a').filter(function() {
        return $(this).text() === text;
    });

    return links.first();
}

// /////////////////////////////////////////////////////////////////////////////

// Replaces the page-wide message area for the create and edit forms. A rejection is
// reported beside the link that opened the form, which is what remains once the form closes.
$.fn.zato.on_prem_gateway.on_submit_complete = function(data, status) {

    $.fn.zato.hide_action_overlay();

    if(status == 'success') {
        return;
    }

    var config = $.fn.zato.on_prem_gateway.config;
    var anchor;

    if($('#edit-div').dialog('isOpen')) {
        anchor = $.fn.zato.on_prem_gateway.get_row_link($('#id_edit-id').val(), config.edit_link_text);
    }
    else {
        anchor = $(config.create_link_selector);
    }

    $.fn.zato.on_prem_gateway.show_message(anchor, data.responseText, false);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.enrollment_token = function(id) {

    var url = String.format('./enrollment-token/{0}/cluster/{1}/', id, $(document).getUrlParam('cluster'));
    var link = $.fn.zato.on_prem_gateway.get_row_link(id, $.fn.zato.on_prem_gateway.config.enrollment_token_link_text);

    var callback = function(data, status) {

        if(status != 'success') {
            $.fn.zato.on_prem_gateway.show_message(link, data.responseText, false);
            return;
        }

        // The token is issued once and is not retained, so this dialog is the only
        // opportunity to record it ..
        var response = $.parseJSON(data.responseText);

        $('#enrollment-token-value').val(response.token);

        // .. and its expiration is stated in the dialog title, in the browser's time zone.
        var div = $('#enrollment_token-div');
        var expiresAt = $.fn.zato.time_ago.format_timestamp(new Date(response.expires_at), false);
        var timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        var title = String.format('Enrollment token, valid until {0} ({1})', expiresAt, timezone);

        $.fn.zato.data_table.set_dialog_title(div, title);
        div.dialog('open');
    }

    $.fn.zato.post(url, callback, {});
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.reset_key = function(id) {

    var link = $.fn.zato.on_prem_gateway.get_row_link(id, $.fn.zato.on_prem_gateway.config.reset_key_link_text);

    var callback = function(data, status) {

        if(status != 'success') {
            $.fn.zato.on_prem_gateway.show_message(link, data.responseText, false);
            return;
        }

        // Enrollment is required again, which the Status column now reports.
        var response = $.parseJSON(data.responseText);
        var statusCell = $.fn.zato.data_table.get_cell(id, '_status');

        statusCell.text($.fn.zato.on_prem_gateway.status.notEnrolled);

        $.fn.zato.data_table.row_updated(id);
        $.fn.zato.on_prem_gateway.show_message(link, response.message, true);
    }

    var url = String.format('./reset-key/{0}/cluster/{1}/', id, $(document).getUrlParam('cluster'));
    $.fn.zato.post(url, callback, {});
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'On-premises gateway `{0}` deleted',
        'Are you sure you want to delete the on-premises gateway `{0}`?',
        true);
}
