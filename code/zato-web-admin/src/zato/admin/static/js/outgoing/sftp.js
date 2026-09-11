
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SFTP = new Class({
    toString: function() {
        var s = '<SFTP id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $.fn.zato.alerts_tab.init({config_id: 'out-sftp-alerts-tab-config'});
    $.fn.zato.time_ago.init_table('#data-table');
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SFTP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.sftp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'username']);
    // Generic connection names are unique per connection type,
    // so the check is scoped to this page's own type.
    var uniqueConstraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'outconn-sftp'}
    ];
    $.each(uniqueConstraints, function(constraintIndex, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sftp.field_descriptions = {
    'id_name': 'A unique name for this connection. ' +
        'Services look it up by this name and the command shell runs against it.',
    'id_is_active': 'Whether this connection can be used. Services cannot look up an inactive connection ' +
        'and pings and the command shell are rejected.',
    'id_address': 'Where the SFTP server listens, as host or host:port, e.g. sftp.example.com:22.',
    'id_username': 'Username to log in to the SFTP server as. ' +
        'Leave empty if the server takes the identity from the private key alone.',
    'id_secret': 'Password for the username above. Leave empty when logging in with a private key instead.',
    'id_private_key': 'Full path to the private key file on the server\'s filesystem, ' +
        'e.g. /opt/zato/keys/id_rsa. Used instead of a password.',
    'id_strict_host_key_checking': 'When on, the server\'s host key must already be in known_hosts ' +
        'or the connection is rejected. Turning it off accepts the keys of new hosts.',
    'id_ignore_host_key_changes': 'When on, host keys are neither checked nor recorded, ' +
        'so a server that regenerated its key still connects. This overrides strict host key checking.',
    'id_verify_how': 'How a stored file is checked against what was sent - by its remote size, ' +
        'or by reading it back and comparing checksums.',
    'id_should_store_content': 'Whether the audit log additionally keeps the bytes of the files ' +
        'this connection moves, so they can be reread and downloaded later. Off by default.',
};

// /////////////////////////////////////////////////////////////////////////////

// A dialog always opens with its More options block collapsed,
// no matter what state the previous open left it in.
$.fn.zato.outgoing.sftp.collapse_more_options = function(form_type) {
    $('.sftp-more-options-' + form_type).each(function(ignored, elem) {
        $.fn.zato.toggle_visible_hidden(elem, false);
    });
}

// /////////////////////////////////////////////////////////////////////////////

// The tabs of the create dialog - the connection itself and its alert settings
$.fn.zato.outgoing.sftp.tab_labels = function() {
    var out = {
        main:   'Main',
        alerts: $.fn.zato.alerts_tab.tab_label()
    };
    return out;
}

$.fn.zato.outgoing.sftp._reset_tabs = function(action) {
    $.fn.zato.form_tabs.reset({
        div_id:       '#' + action + '-div',
        panel_prefix: 'out-sftp-' + action + '-tab-panel-',
        default_tab:  'main',
        tab_labels:   $.fn.zato.outgoing.sftp.tab_labels()
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sftp.create = function() {
    $.fn.zato.outgoing.sftp._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing SFTP connection', null);
    $.fn.zato.outgoing.sftp.collapse_more_options('create');
    $.fn.zato.alerts_tab.bind({
        panel_id: 'out-sftp-create-tab-panel-alerts',
        field_prefix: ''
    });
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        fieldSelector: 'table.form-data tr, .decision-line',
        descriptions: $.extend({}, $.fn.zato.outgoing.sftp.field_descriptions, $.fn.zato.alerts_tab.descriptions())
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sftp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing SFTP connection', id);
    $.fn.zato.outgoing.sftp.collapse_more_options('edit');
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.sftp.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sftp.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var strict_host_key_checking = item.strict_host_key_checking == true;
    var ignore_host_key_changes = item.ignore_host_key_changes == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td class="zato-time-ago" data-time-ago-id="{0}" data-time-utc="{1}" data-duration-ms="{2}"></td>',
        data.last_run_job_ids, data.last_run_utc, data.last_duration_ms);
    row += String.format('<td>{0}</td>', item.address ? item.address : $.fn.zato.empty_value);

    // 2
    row += String.format('<td>{0}</td>', item.username ? item.username : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>',
        String.format('<a href="/zato/outgoing/file-transfer/schedules/sftp/{0}/cluster/{1}/{2}/?name={3}">{4}</a>',
        item.id, item.cluster_id, data.name_slug, item.name,
        $.fn.zato.count_text(data.scheduler_schedule_count, 'schedule', 'schedules')));
    row += String.format('<td class="action"><a href="{0}">Command shell</a></td>', data.command_shell_url);
    row += String.format('<td><a href="/zato/audit-log/?source=file-outgoing&object_name={0}&cluster={1}">Audit log</a></td>',
        encodeURIComponent(item.name), item.cluster_id);

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.sftp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.sftp.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.address);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.username ? item.username : '');
    row += String.format("<td class='ignore'>{0}</td>", item.private_key ? item.private_key : '');
    row += String.format("<td class='ignore'>{0}</td>", strict_host_key_checking ? 'True' : 'False');

    // 6
    row += String.format("<td class='ignore'>{0}</td>", ignore_host_key_changes ? 'True' : 'False');
    row += String.format("<td class='ignore'>{0}</td>", item.should_store_content == true);
    row += String.format("<td class='ignore'>{0}</td>", item.verify_how);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sftp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing SFTP connection `{0}` deleted',
        'Are you sure you want to delete outgoing SFTP connection `{0}`?',
        true);
}
