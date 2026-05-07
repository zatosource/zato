
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.HL7MLLPChannel = new Class({
    toString: function() {
        var s = '<HL7MLLPChannel id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.HL7MLLPChannel;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.hl7.mllp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'service',
        'logging_level',
        'data_encoding',
        'max_msg_size',
        'read_buffer_size',
        'recv_timeout',
        'start_seq',
        'end_seq',
        'msh3_sending_app',
        'msh4_sending_facility',
        'msh5_receiving_app',
        'msh6_receiving_facility',
        'msh9_message_type',
        'msh9_trigger_event',
        'msh11_processing_id',
        'msh12_version_id',
        'dedup_ttl_value',
        'dedup_ttl_unit',
        'default_character_encoding',
    ]);

    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.tab_labels = {
    main:     'Main',
    routing:  'Routing',
    protocol: 'Protocol',
    logging:  'Logging',
    dedup:    'Deduplication'
};

$.fn.zato.channel.hl7.mllp._reset_tabs = function(action) {
    var is_edit = action === 'edit';
    $.fn.zato.form_tabs.reset({
        div_id:       is_edit ? '#edit-div' : '#create-div',
        panel_prefix: is_edit ? 'mllp-edit-tab-panel-' : 'mllp-create-tab-panel-',
        default_tab:  'main',
        tab_labels:   $.fn.zato.channel.hl7.mllp.tab_labels
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.create = function() {
    $.fn.zato.channel.hl7.mllp._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new HL7 MLLP channel', null);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.edit = function(id) {
    $.fn.zato.channel.hl7.mllp._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the HL7 MLLP channel', id);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;
    let cluster_id = $(document).getUrlParam('cluster');

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');

    row += String.format('<td>{0}</td>', $.fn.zato.data_table.service_text(item.service, cluster_id));

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.hl7.mllp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.hl7.mllp.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.service);

    row += String.format("<td class='ignore'>{0}</td>", item.should_parse_on_input);
    row += String.format("<td class='ignore'>{0}</td>", item.should_validate);

    row += String.format("<td class='ignore'>{0}</td>", item.data_encoding);
    row += String.format("<td class='ignore'>{0}</td>", item.should_return_errors);

    row += String.format("<td class='ignore'>{0}</td>", item.should_log_messages);
    row += String.format("<td class='ignore'>{0}</td>", item.logging_level);

    row += String.format("<td class='ignore'>{0}</td>", item.max_msg_size);
    row += String.format("<td class='ignore'>{0}</td>", item.read_buffer_size);
    row += String.format("<td class='ignore'>{0}</td>", item.recv_timeout);

    row += String.format("<td class='ignore'>{0}</td>", item.start_seq);
    row += String.format("<td class='ignore'>{0}</td>", item.end_seq);

    row += String.format("<td class='ignore'>{0}</td>", item.msh3_sending_app);
    row += String.format("<td class='ignore'>{0}</td>", item.msh4_sending_facility);
    row += String.format("<td class='ignore'>{0}</td>", item.msh5_receiving_app);
    row += String.format("<td class='ignore'>{0}</td>", item.msh6_receiving_facility);
    row += String.format("<td class='ignore'>{0}</td>", item.msh9_message_type);
    row += String.format("<td class='ignore'>{0}</td>", item.msh9_trigger_event);
    row += String.format("<td class='ignore'>{0}</td>", item.msh11_processing_id);
    row += String.format("<td class='ignore'>{0}</td>", item.msh12_version_id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_default);

    row += String.format("<td class='ignore'>{0}</td>", item.dedup_ttl_value);
    row += String.format("<td class='ignore'>{0}</td>", item.dedup_ttl_unit);

    row += String.format("<td class='ignore'>{0}</td>", item.default_character_encoding);

    row += String.format("<td class='ignore'>{0}</td>", item.normalize_line_endings);
    row += String.format("<td class='ignore'>{0}</td>", item.force_standard_delimiters);
    row += String.format("<td class='ignore'>{0}</td>", item.repair_truncated_msh);
    row += String.format("<td class='ignore'>{0}</td>", item.split_concatenated_messages);
    row += String.format("<td class='ignore'>{0}</td>", item.use_msh18_encoding);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'HL7 MLLP channel `{0}` deleted',
        'Are you sure you want to delete HL7 MLLP channel `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Live form updates registration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.live_form_updates.register('create', [
    {object_type: 'service', target_select: '#id_service'}
]);

$.fn.zato.live_form_updates.register('edit', [
    {object_type: 'service', target_select: '#id_edit-service'}
]);

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
