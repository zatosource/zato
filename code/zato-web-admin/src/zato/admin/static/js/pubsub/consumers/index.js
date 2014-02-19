
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Consumer = new Class({
    toString: function() {
        var s = '<Consumer id:{0} is_active:{1}>';
        return String.format(
            s,
            this.id ? this.id : '(none)',
            this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Consumer;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.consumers.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['client_id', 'max_backlog']);
})

$.fn.zato.pubsub.consumers.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new consumer', null);
}

$.fn.zato.pubsub.consumers.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the consumer', id);
}

$.fn.zato.pubsub.consumers.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    $.fn.zato.data_table.data[data.id].name = data.name;
    $.fn.zato.data_table.data[data.id].is_active = data.is_active == true;

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", data.id);
    }

    var is_active = data.is_active == true;

    var last_seen = data.last_seen ? data.last_seen : "(Never)";
    var last_seen_css_class = data.last_seen ? "" : "form_hint";

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', data.topic_name);
    row += String.format('<td>{0}</td>', data.name);
    row += String.format('<td>{0}</td>', data.sub_key);
    row += String.format('<td>{0}</td>', is_active ? "Yes": "No");
    row += String.format('<td>{0}</td>', item.max_backlog);
    row += String.format('<td><span class="{0}">{1}</span></td>', last_seen_css_class, last_seen);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.pubsub.consumers.edit('{0}')\">Edit</a>", data.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.pubsub.consumers.delete_('{0}')\">Delete</a>", data.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.consumers.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Consumer [{0}] deleted',
        'Are you sure you want to delete the consumer [{0}]?',
        true, false, '/zato/pubsub/consumers/delete/{0}/');
}
