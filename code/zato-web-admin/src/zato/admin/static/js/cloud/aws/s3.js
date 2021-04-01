
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.AWSS3 = new Class({
    toString: function() {
        var s = '<AWSS3 id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)'
                                );
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.AWSS3;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cloud.aws.s3.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'pool_size', 'debug_level', 'content_type', 'security_id', 'address', 'storage_class']);
})

$.fn.zato.cloud.aws.s3.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new AWS S3 connection', null);
}

$.fn.zato.cloud.aws.s3.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the AWS S3 connection', id);
}

$.fn.zato.cloud.aws.s3.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var suppr_cons_slashes = item.suppr_cons_slashes == true;

    var bucket = "<span class='form_hint'>---</span>";
    if(item.bucket) {
        bucket = item.bucket;
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.pool_size);
    row += String.format('<td>{0}</td>', item.debug_level);
    row += String.format('<td>{0}</td>', bucket);
    row += String.format('<td>{0}</td>', item.content_type);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cloud.aws.s3.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.cloud.aws.s3.delete_({0});'>Delete</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    row += String.format("<td class='ignore'>{0}</td>", item.security_id);
    row += String.format("<td class='ignore'>{0}</td>", suppr_cons_slashes);
    row += String.format("<td class='ignore'>{0}</td>", item.address);
    row += String.format("<td class='ignore'>{0}</td>", item.metadata_);
    row += String.format("<td class='ignore'>{0}</td>", item.bucket);
    row += String.format("<td class='ignore'>{0}</td>", item.encrypt_at_rest);
    row += String.format("<td class='ignore'>{0}</td>", item.storage_class);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.cloud.aws.s3.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'AWS S3 connection `{0}` deleted',
        'Are you sure you want to delete the AWS S3 connection `{0}`?',
        true);
}
