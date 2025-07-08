// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubSubscription = new Class({
    toString: function() {
        var s = '<PubSubSubscription id:{0} sub_key:{1} topic_name:{2} sec_name:{3} pattern_matched:{4}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.sub_key ? this.sub_key : '(none)',
                                this.topic_name ? this.topic_name : '(none)',
                                this.sec_name ? this.sec_name : '(none)',
                                this.pattern_matched ? this.pattern_matched : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubSubscription;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.subscription.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([]);
})

$.fn.zato.pubsub.subscription.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true
    var created_date = new Date(item.created);
    var created_formatted = created_date.getFullYear() + '-' + 
                           String(created_date.getMonth() + 1).padStart(2, '0') + '-' + 
                           String(created_date.getDate()).padStart(2, '0') + ' ' +
                           String(created_date.getHours()).padStart(2, '0') + ':' + 
                           String(created_date.getMinutes()).padStart(2, '0') + ':' + 
                           String(created_date.getSeconds()).padStart(2, '0');

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.sub_key);
    row += String.format('<td>{0}</td>', item.topic_name);
    row += String.format('<td>{0}</td>', item.sec_name);
    row += String.format('<td style="text-align:center">{0}</td>', created_formatted);
    row += String.format('<td style="text-align:center">{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.pubsub.subscription.edit({0});'>Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.pubsub.subscription.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.created || "");

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.subscription.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new pub/sub subscription', null);
    // Populate security definitions after form opens
    setTimeout(function() {
        $.fn.zato.common.security.populateSecurityDefinitions('create', null, '/zato/pubsub/subscription/get-security-definitions/', '#id_sec_base_id');
    }, 100);
}

$.fn.zato.pubsub.subscription.edit = function(id) {
    $.fn.zato.data_table.edit('edit', 'Update the pub/sub subscription', id);
    // Populate security definitions after form opens with current selection
    setTimeout(function() {
        var currentSecId = $('#id_edit-sec_base_id').val();
        $.fn.zato.common.security.populateSecurityDefinitions('edit', currentSecId, '/zato/pubsub/subscription/get-security-definitions/', '#id_edit-sec_base_id');
    }, 100);
}

$.fn.zato.pubsub.subscription.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/sub subscription `{0}` deleted',
        'Are you sure you want to delete pub/sub subscription `{0}`?',
        true);
}
