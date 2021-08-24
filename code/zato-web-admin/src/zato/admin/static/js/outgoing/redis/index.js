
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Redis = new Class({
    toString: function() {
        var s = '<Redis id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Redis;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.redis.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([]);
})

$.fn.zato.outgoing.redis.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing Redis connection', null);
}

$.fn.zato.outgoing.redis.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing Redis connection', id);
}

$.fn.zato.outgoing.redis.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = $.fn.zato.like_bool(item.is_active) == true;
    var use_redis_sentinels = item.use_redis_sentinels  ? 'Yes' : 'No';
    var data_dicts_link = '/zato/outgoing/redis/data-dict/dictionary/?cluster=' + item.cluster_id;
    var remote_commands_link = '/zato/outgoing/redis/remote-command/?cluster=' + item.cluster_id;

    // --
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.host || $.fn.zato.empty_value);

    // 2
    row += String.format('<td>{0}</td>', item.port || $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', item.db || $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', use_redis_sentinels);

    // 3
    row += String.format('<td class="ignore">{0}</td>', item.redis_sentinels);
    row += String.format('<td>{0}</td>', String.format("<a href=\"{0}\">Remote commands</a>", remote_commands_link));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password(\"{0}\")'>Change password</a>", item.id));

    // 4
    row += String.format('<td class="ignore">{0}</td>', item.redis_sentinels_master);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.redis.edit(\"{0}\");'>Edit</a>", item.id));

    if(item.name != 'default') {
        row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.redis.delete_(\"{0}\");'>Delete</a>", item.id));
    }
    else {
        row += String.format('<td></td>');
    }

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.use_redis_sentinels);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);

    // 6
    row += String.format('<td class="ignore">{0}</td>', item.host);
    row += String.format('<td class="ignore">{0}</td>', item.port);
    row += String.format('<td class="ignore">{0}</td>', item.db);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.redis.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Redis connection [{0}] deleted',
        'Are you sure you want to delete the outgoing Redis connection [{0}]?',
        true);
}
