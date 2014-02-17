
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Topics = new Class({
    toString: function() {
        var s = '<Topics id:{0} name:{1} max_depth:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.max_depth ? this.max_depth : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Topics;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.topics.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'max_depth']);
})

$.fn.zato.pubsub.topics.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new topic', null);
}

$.fn.zato.pubsub.topics.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the topic', id);
}

$.fn.zato.pubsub.topics.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    var consumers_suffix = (data.consumers_count == 0 || data.consumers_count > 2) ? "s" : "";
    var producers_suffix = (data.producers_count == 0 || data.producers_count > 2) ? "s" : "";

    var last_pub_time = data.last_pub_time ? data.last_pub_time : "(Never)";

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', data.current_depth);
    row += String.format('<td>{0}</td>', item.max_depth);
    row += String.format('<td><span class="form_hint">{0}</span></td>', last_pub_time);

    row += String.format(
        "<td><a href=\'../consumers/cluster/{0}/{1}\'>{2} consumer{3}</a></td>",
            data.cluster_id, data.name, data.consumers_count, consumers_suffix);

    row += String.format(
        "<td><a href=\'../producers/cluster/{0}/{1}\'>{2} producer{3}</a></td>",
            data.cluster_id, data.name, data.producers_count, producers_suffix);

    row += String.format('<td>{0}</td>', "<a href='publish'>Publish a message</a>");
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.pubsub.topics.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.pubsub.topics.delete_('{0}')\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.topics.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Topic [{0}] deleted',
        'Are you sure you want to delete the topic [{0}]?',
        true);
}
