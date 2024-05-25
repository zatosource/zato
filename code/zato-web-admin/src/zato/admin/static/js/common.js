//
// Namespaces
//

(function($){
if ({}.__proto__){
    // mozilla  & webkit expose the prototype chain directly
    $.namespace = function(n){
        var names=n.split('.');
        var f=$.fn;
        for(var i=0;i<names.length;i++) {
            var name=names[i];
            if(!f[name]) {
                f[name] = function namespace() { // insert this function in the prototype chain
                    this.__proto__ = arguments.callee;
                    return this;
                };
                f[name].__proto__ = f;
            }
            f=f[name];
        }
    };
    $.fn.$ = function(){
        this.__proto__ = $.fn;
        return this;
    };
}else{
    // every other browser; need to copy methods
    $.namespace = function(n){
        var names=n.split('.');
        var f=$.fn;
        for(var i=0;i<names.length;i++) {
            var name=names[i];
            if(!f[name]) {
                f[name] = function namespace() { return this.extend(arguments.callee); };
            }
            f=f[name];
        }
    };
    $.fn.$ = function() { // slow but restores the default namespace
        var len = this.length;
        this.extend($.fn);
        this.length = len; // $.fn has length = 0, which messes everything up
        return this;
    };
}
})(jQuery);

$.namespace('zato');
$.namespace('zato.account');
$.namespace('zato.account.basic_settings');
$.namespace('zato.audit_log');
$.namespace('zato.cache');
$.namespace('zato.cache.builtin');
$.namespace('zato.cache.builtin.entries');
$.namespace('zato.cache.memcached');
$.namespace('zato.channel');
$.namespace('zato.channel.amqp');
$.namespace('zato.channel.file_transfer');
$.namespace('zato.channel.hl7');
$.namespace('zato.channel.hl7.mllp');
$.namespace('zato.channel.hl7.rest');
$.namespace('zato.channel.jms_wmq');
$.namespace('zato.channel.json_rpc');
$.namespace('zato.channel.kafka');
$.namespace('zato.channel.stomp');
$.namespace('zato.channel.wsx');
$.namespace('zato.channel.wsx.connection_list');
$.namespace('zato.channel.zmq');
$.namespace('zato.cloud');
$.namespace('zato.cloud.aws');
$.namespace('zato.cloud.aws.s3');
$.namespace('zato.cloud.confluence');
$.namespace('zato.cloud.dropbox');
$.namespace('zato.cloud.jira');
$.namespace('zato.cloud.microsoft_365');
$.namespace('zato.cloud.salesforce');
$.namespace('zato.cluster');
$.namespace('zato.cluster.servers');
$.namespace('zato.data_table');
$.namespace('zato.data_table.multirow');
$.namespace('zato.definition');
$.namespace('zato.definition.amqp');
$.namespace('zato.definition.cassandra');
$.namespace('zato.definition.kafka');
$.namespace('zato.definition.jms_wmq');
$.namespace('zato.docs');
$.namespace('zato.email');
$.namespace('zato.email.imap');
$.namespace('zato.email.smtp');
$.namespace('zato.form');
$.namespace('zato.groups');
$.namespace('zato.groups.members');
$.namespace('zato.http_soap');
$.namespace('zato.http_soap.details');
$.namespace('zato.ide');
$.namespace('zato.invoker');
$.namespace('zato.load_balancer');
$.namespace('zato.message');
$.namespace('zato.message.json_pointer');
$.namespace('zato.message.live_browser');
$.namespace('zato.message.namespace');
$.namespace('zato.message.xpath');
$.namespace('zato.notif');
$.namespace('zato.notif.sql');
$.namespace('zato.outgoing');
$.namespace('zato.outgoing.amqp');
$.namespace('zato.outgoing.ftp');
$.namespace('zato.outgoing.hl7');
$.namespace('zato.outgoing.hl7.fhir');
$.namespace('zato.outgoing.hl7.mllp');
$.namespace('zato.outgoing.im');
$.namespace('zato.outgoing.im.slack');
$.namespace('zato.outgoing.im.telegram');
$.namespace('zato.outgoing.jms_wmq');
$.namespace('zato.outgoing.mongodb');
$.namespace('zato.outgoing.kafka');
$.namespace('zato.outgoing.ldap');
$.namespace('zato.outgoing.odoo');
$.namespace('zato.outgoing.redis');
$.namespace('zato.outgoing.redis.data_dict');
$.namespace('zato.outgoing.redis.data_dict.dictionary');
$.namespace('zato.outgoing.redis.data_dict.translation');
$.namespace('zato.outgoing.redis.data_dict.system');
$.namespace('zato.outgoing.sql');
$.namespace('zato.outgoing.stomp');
$.namespace('zato.outgoing.sap');
$.namespace('zato.outgoing.sftp');
$.namespace('zato.outgoing.wsx');
$.namespace('zato.outgoing.zmq');
$.namespace('zato.pattern.delivery');
$.namespace('zato.pattern.delivery.in_doubt');
$.namespace('zato.pubsub.endpoint');
$.namespace('zato.pubsub.endpoint_queue');
$.namespace('zato.pubsub.message');
$.namespace('zato.pubsub.message.details');
$.namespace('zato.pubsub.message.publish');
$.namespace('zato.pubsub.message.queue');
$.namespace('zato.pubsub.subscription');
$.namespace('zato.pubsub.task');
$.namespace('zato.pubsub.task.delivery');
$.namespace('zato.pubsub.topic');
$.namespace('zato.query');
$.namespace('zato.query.cassandra');
$.namespace('zato.scheduler');
$.namespace('zato.security');
$.namespace('zato.security.apikey');
$.namespace('zato.security.aws');
$.namespace('zato.security.basic_auth');
$.namespace('zato.security.jwt');
$.namespace('zato.security.ntlm');
$.namespace('zato.security.oauth');
$.namespace('zato.security.rbac');
$.namespace('zato.security.rbac.client_role');
$.namespace('zato.security.rbac.permission');
$.namespace('zato.security.rbac.role');
$.namespace('zato.security.rbac.role_permission');
$.namespace('zato.security.tls');
$.namespace('zato.security.tls.ca_cert');
$.namespace('zato.security.tls.channel');
$.namespace('zato.security.tls.key_cert');
$.namespace('zato.security.wss');
$.namespace('zato.security.vault.connection');
$.namespace('zato.security.vault.policy');
$.namespace('zato.security.xpath');
$.namespace('zato.search');
$.namespace('zato.search.es');
$.namespace('zato.search.solr');
$.namespace('zato.service');
$.namespace('zato.sms');
$.namespace('zato.sms.twilio');
$.namespace('zato.stats');
$.namespace('zato.stats.custom');
$.namespace('zato.stats.top_n');
$.namespace('zato.vendors');
$.namespace('zato.vendors.keysight');
$.namespace('zato.vendors.keysight.vision');

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.post = function(url, callback, data, data_type, suppress_user_message, context) {
    if(!data) {
        data = '';
    }

    if(!data_type) {
        data_type = 'json';
    }

    if(!suppress_user_message) {
        $.fn.zato.user_message(false, '', true);
    }

    if(!context) {
        context = {};
    }

    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        complete: callback,
        dataType: data_type,
        context: context
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.user_message = function(is_success, msg, loading) {
    var pre = $('#user-message');
    var new_css_class = ''

    if(!loading) {
        if(is_success) {
            css_class = 'user-message-success';
        }
        else {
            css_class = 'user-message-failure';
        }
    }
    else {
        css_class = 'loading';
    }

    pre.removeClass('user-message-success').
        removeClass('user-message-failure').
        removeClass('loading').
        addClass(css_class);
    pre.text(msg);

    var div = $('#user-message-div');
    div.fadeOut(100, function() {
        div.fadeIn(250);
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.post_with_user_message = function(url, on_callback_done) {

    var callback = function(data, status) {
        var success = status == 'success';
        $.fn.zato.user_message(success, data.responseText);

        if(on_callback_done) {
            on_callback_done(success);
        }
    }

    $.fn.zato.post(url, callback, '', 'text');
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Forms
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/* Unlike jQuery's serializeArray, the function below simply returns all the
    fields, regardless of whether they're disabled, checked or not etc. */
$.fn.zato.form.serialize = function(form) {

    var out = {}
    var name = '';
    var value = '';

    var fields = $(':input, textarea', form);
    $.each(fields, function(idx, elem) {
        elem = $(elem);
        name = elem.attr('name');
        if(name) {
            value = elem.val();
            if(elem.attr('type') == 'checkbox') {
                value = $.fn.zato.to_bool(value);
            }
            out[name] = value;
        }
    });
    return out;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

/* Takes a form (ID or a jQuery object), a business object and populates the
    form with values read from the object. The 'name' and 'id' attributes of the
    form's fields may use custom prefixes that will be taken into account accordingly.
*/
$.fn.zato.form.populate = function(form, instance, name_prefix, id_prefix) {

    console.log('Populating form with `'+ instance +'`');

    if(!name_prefix) {
        name_prefix = '';
    }

    if(_.isUndefined(id_prefix)) {
        id_prefix = '';
    }

    // Remove any previously selected options from this form
    $("option:selected").each(function() {
        $(this).removeAttr('selected');
    });

    var name = '';
    var value = '';
    var form_elem_name = null;
    var form_elem = null;
    var fields = $.fn.zato.form.serialize(form);
    var skip_boolean = ['in_lb']; // A list of boolean fields that should be treated as though they were regular text

    /*
    for(item_attr in instance) {
        console.log('Item attr -> `'+ item_attr +'`');
    }

    for(field_name in fields) {
        console.log('Field -> `'+ field_name +'`');
    }
    */

    for(field_name in fields) {
        // console.log('Field -> `'+ field_name +'`');
        if(field_name.indexOf(name_prefix) === 0 || field_name == 'id') {
            field_name = field_name.replace(name_prefix, '');
            for(item_attr in instance) {
                // console.log('Item attr -> `'+ item_attr +'`');
                if(item_attr == field_name) {
                    value = instance[item_attr];
                    // console.log('Field/value: `'+ item_attr + '` `'+ value +'`');
                    form_elem_name = id_prefix + field_name;
                    form_elem = $(form_elem_name);
                    if($.fn.zato.like_bool(value)) {
                        if(_.include(skip_boolean, field_name)) {
                            form_elem.val(value);
                        }
                        else {
                            if($.fn.zato.to_bool(value)) {
                                form_elem.attr('checked', 'checked');
                            }
                            else {
                                form_elem.removeAttr('checked');
                            }
                        }
                    }
                    else if(form_elem.is('select')) {
                        // Set the value only if it exists in SELECT, otherwise reset the field
                        // so it doesn't get automatically populated with previous instance's value
                        var option_value = $(String.format("{0} option[value='{1}']", form_elem_name, value));
                        if($.fn.zato.data_table.select_has_value(option_value)) {
                            option_value.attr('selected', 'selected');
                        }
                        else {
                            $(String.format("{0} option:first", form_elem_name)).prop('selected',true);
                        }
                    }
                    else {
                        form_elem.val(value);
                    }
                }
            }
        }
    }

    if($.fn.zato.data_table.after_populate) {
        $.fn.zato.data_table.after_populate();
    }

}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Data table begin
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.data = {}
$.fn.zato.data_table.on_submit_complete_callback = null;
$.fn.zato.data_table.on_submit_complete_callback_args = null;

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.row_updated = function(id) {
    var tr = $('#tr_'+ id)
    tr.addClass('updated');

    return tr;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.parse = function() {

    var rows = $('#data-table tr').not('[class="ignore"]');
    var columns = $.fn.zato.data_table.get_columns();

    $.each(rows, function(row_idx, row) {
        var instance = new $.fn.zato.data_table.class_()
        var tds = $(row).find('td');

        // console.info('columns = ' + columns);

        $.each(tds, function(td_idx, td) {

            var attr_name = columns[td_idx];
            var attr_value = $(td).text().trim();

            // console.log('td_idx:`'+ td_idx +'`, attr_name:`'+ attr_name +'`, attr_value:`'+ attr_value + '`');

            // Don't bother with ignored attributes.
            if(attr_name[0] != '_') {
                instance[attr_name] = attr_value;
            }
        });
        console.log('Found instance in data_table ' + instance);
        $.fn.zato.data_table.data[instance.id] = instance;

    });

    if(_.size($.fn.zato.data_table.data) < 1) {
        $('#data-table').data('is_empty', true);
    }
    else {
        // Highlight the items specified in the query string to be highlighted
        var highlight = $(document).getUrlParam('highlight');
        if(highlight) {
            var tr = $('#tr_'+ highlight);
            tr.addClass('updated');
        }
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.reset_form = function(form_id) {
    var form = $(form_id);

    form.each(function() {
        this.reset();
    });

    if(!($.fn.zato.startswith(form_id, '#create'))) {
        $(':checkbox', form).each(function(idx, elem) {
            $(elem).removeAttr('checked');
        });
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.cleanup = function(form_id) {

    /* Clear out the values and close the dialog.
    */

    $.fn.zato.data_table.reset_form(form_id);
    var div_id = '';
    var parts = form_id.split('form-');

    if(parts == form_id) {
        parts = form_id.split('form');
        div_id = parts[0].replace('-', '') + '-div';
    }
    else {
        div_id = parts[0] + parts[1];
    }
    $(div_id).dialog('close');
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.form_info = function(button) {
    var form = $(button).closest('form');
    var form_id = form.attr('id');
    return {
        'form': form,
        'form_id': '#' + form_id,
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.close = function(button) {
    var form_info = $.fn.zato.data_table.form_info(button);
    $.fn.zato.data_table.cleanup(form_info['form_id']);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table._on_submit_complete = function(data, status) {

    var msg = '';
    var success = status == 'success';

    if(success) {
        var response = $.parseJSON(data.responseText);
        msg = response.message || response.msg;
    }
    else {
        msg = data.responseText;
    }
    $.fn.zato.user_message(success, msg);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table._on_submit = function(form, callback) {
    let serialized = form.serialize();
    console.log('Serialized -> '+ serialized);
    $.fn.zato.post(form.attr('action'), callback, serialized);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.remove_row = function(td_prefix, instance_id) {
    $(td_prefix + instance_id).parent().remove();
    $.fn.zato.data_table.data[instance_id] = null;

    if($('#data-table tr').length == 1) {
        var row = '<tr><td colspan="100">No results</td></tr>';
        $('#data-table > tbody:last').prepend(row);
        $('#data-table').data('is_empty', true);
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.delete_ = function(id, td_prefix, success_pattern, confirm_pattern,
    append_cluster, confirm_challenge, url_pattern, post_data, remove_tr,
    on_success_callback) {

    // 99% of callers will not provide remove_tr in which case we default to True
    var _remove_tr = remove_tr == null ? true : remove_tr;

    var instance = $.fn.zato.data_table.data[id];
    var name = '';

    if('get_name' in instance) {
        name = instance.get_name();
    }
    else {
        name = instance.name;
    }

    console.log('Instance to delete: ' + instance);

    var _callback = function(data, status) {
        var success = (status == 'success' || status == 'parsererror');

        if(success) {
            if(_remove_tr) {
                $.fn.zato.data_table.remove_row(td_prefix, instance.id);
            }

            if(on_success_callback) {
                on_success_callback();
            }

            msg = String.format(success_pattern, name);
        }
        else {
            msg = data.responseText;
        }
        $.fn.zato.user_message(success, msg);
    }

    var callback = function(ok) {
        if(ok) {
            if(url_pattern) {
                var url = String.format(url_pattern, id);
            }
            else {
                var url = String.format('./delete/{0}/', id);
            }
            if(append_cluster) {
                url = url + String.format('cluster/{0}/', $('#cluster_id').val());
            }
            if(!post_data) {
                post_data = {};
            }
            $.fn.zato.post(url, _callback, post_data);
            return false;
        }
    }
    if(confirm_challenge) {
        var q = String.format(confirm_pattern, name, confirm_challenge);
        jPrompt(q, "I'd rather not to", 'Please confirm', function(r) {
            var ok = r == confirm_challenge;
            callback(ok);
        });
    }
    else {
        var q = String.format(confirm_pattern, name);
        jConfirm(q, 'Please confirm', callback);
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.on_change_password_submit = function() {

    var form = $('#change_password-form');
    if($.fn.zato.is_form_valid(form)) {
        var _callback = function(data, status) {
            $.fn.zato.data_table.row_updated($('#id_change_password-id').val());
            $.fn.zato.data_table._on_submit_complete(data, status);
        }

        $.fn.zato.data_table._on_submit(form, _callback);
        $('#change_password-div').dialog('close');

        return false;
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.change_password = function(id, title, label, _label_lower) {

    // Local variables
    var form_id = '#change_password-form';

    // Cleanup comes first
    $.fn.zato.cleanup_form_css_attention(form_id);

    var _title = title;
    var _label = label;
    var _label_lower = _label_lower;
    var name = $.fn.zato.data_table.data[id].name

    if(!_title) {
        _title = 'Change password ';
    }

    if(!_label) {
        _label = 'Password';
        _label_lower = 'password';
    }

    $('#secret_type_id').val(_label_lower);
    $('#secret_label1').text(_label);
    $('#secret_label2').text(_label_lower);

    $('#change-password-name').text(name);
    $('#id_change_password-id').val(id);

    var div = $('#change_password-div');

    div.prev().text(_title); // prev() is a .ui-dialog-titlebar
    div.dialog('open');
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.setup_change_password = function() {

    // Local variables
    var form_id = '#change_password-form';

    // Cleanup comes first
    $.fn.zato.cleanup_form_css_attention(form_id);

    $('#change_password-div').dialog({
        autoOpen: false,
        width: '40em',
        close: function(e, ui) {
            $.fn.zato.data_table.reset_form(form_id);
        }
    });

    var change_password_form = $('#change_password-form');

    change_password_form.submit(function(e) {
        e.preventDefault();
        $.fn.zato.data_table.on_change_password_submit();
        return false;
    });

    if($.fn.zato.data_table.password_required) {
        $("#id_password1").attr($.fn.zato.validate_required_attr, "required");
        $("#id_password2").attr($.fn.zato.validate_required_attr, "required");

        $('#id_password1').attr($.fn.zato.validate_required_msg_attr, $.fn.zato.validate_required_msg);
        $('#id_password2').attr($.fn.zato.validate_required_msg_attr, $.fn.zato.validate_required_msg);
    }

    else {
        $("#id_password1").attr($.fn.zato.validate_equals_attr, "equals-id_password2");
        $("#id_password1").attr($.fn.zato.validate_equals_msg_attr, "Passwords" + $.fn.zato.validate_equals_msg_suffix);

        $("#id_password2").attr($.fn.zato.validate_equals_attr, "equals-id_password1");
        $("#id_password2").attr($.fn.zato.validate_equals_msg_attr, "Passwords" + $.fn.zato.validate_equals_msg_suffix);
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table._create_edit = function(action, title, id, remove_multirow) {

    // Local variables
    var form_id = String.format('#{0}-form', action)

    // Cleanup comes first
    $.fn.zato.cleanup_form_css_attention(form_id);

    let _remove_multirow = remove_multirow === undefined ? true : remove_multirow;

    var div_id = String.format('#{0}-div', action)
    var div = $(div_id);

    $.fn.zato.cleanup_chosen(div_id);

    // Clean up all the multirow elements that were possibly
    // automatically generated for that form.
    if(_remove_multirow) {
        $.fn.zato.data_table.multirow.remove_multirow_added();
    }

    if(action == 'edit') {

        var form = $(form_id);
        var name_prefix = action + '-';
        var id_prefix = String.format('#id_{0}', name_prefix);
        var instance = $.fn.zato.data_table.data[id];

        $.fn.zato.form.populate(form, instance, name_prefix, id_prefix);
    }

    div.prev().text(title); // prev() is a .ui-dialog-titlebar
    div.dialog('open');

    $.fn.zato.turn_selects_into_chosen(div_id);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.edit = function(action, title, id, remove_multirow) {
    $.fn.zato.data_table._create_edit(action, title, id, remove_multirow);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.add_row = function(data, action, new_row_func, include_tr) {

    let instance = new $.fn.zato.data_table.class_();
    let form = $(String.format('#{0}-form', action));

    let prefix;
    if(action == 'edit') {
        prefix = action + '-';
    }
    else {
        prefix = '';
    }

    let name = '';
    let id = '';
    let tag_name = '';
    let html_elem;
    let value = '';
    let multirow_visited = new Map();

    $.each(form.serializeArray(), function(idx, elem) {
        name = elem.name.replace(prefix, '');
        html_elem = $('#id_' + prefix + $.fn.zato.slugify(name));
        tag_name = html_elem.prop('tagName');

        if(tag_name && html_elem.prop('type') == 'checkbox') {
            value = html_elem.is(':checked');
        }

        else if(html_elem.attr('class') == 'multirow') {
            let _name_prefixed = prefix+name;

            if(!multirow_visited.get(_name_prefixed)) {

                let _rows = form.find('[name="'+ _name_prefixed +'"]');
                let _value = [];

                for(var idx=0; idx<_rows.length; idx++) {
                    let _row = _rows[idx];
                    let _row_value = $(_row).val()
                    if(!_value.includes(_row_value)) {
                        _value.push(_row_value);
                    }
                }
                value = _value;
            }
            multirow_visited.set(_name_prefixed, true);

        }

        else {
            value = elem.value;
        }

        console.log('Creating elem from: `'+ name +'` and `'+ value +'`');

        instance[name] = value

        if(tag_name && tag_name.toLowerCase() == 'select') {
            instance[name + '_select'] = $('#id_' + prefix + name + ' :selected').text();
        }

        if($.fn.zato.data_table.add_row_hook) {
            $.fn.zato.data_table.add_row_hook(instance, name, html_elem, data);
        }

    })

    if(!instance.id) {
        instance.id = data.id;
    }

    console.log('Instance created: ' + instance);

    $.fn.zato.data_table.data[instance.id] = instance;

    return new_row_func(instance, data, include_tr);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.set_field_required = function(field_id) {
    $(field_id).attr($.fn.zato.validate_required_attr, 'required');
    $(field_id).attr($.fn.zato.validate_required_msg_attr, $.fn.zato.validate_required_msg);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.remove_field_required = function(field_id) {
    $(field_id).removeAttr($.fn.zato.validate_required_attr);
    $(field_id).removeAttr($.fn.zato.validate_required_msg_attr, $.fn.zato.validate_required_msg);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.setup_forms = function(attrs) {
    var actions = ['create', 'edit'];

    /* Dynamically prepare pop-up windows.
    */
    $.each(actions, function(ignored, action) {
        var form_id = String.format('#{0}-form', action);
        var div_id = String.format('#{0}-div', action);

        // Pop-up
        $(div_id).dialog({
            autoOpen: false,
            width: '40em',
            height: '10em',
            resizable: false,
            close: function(e, ui) {
                $.fn.zato.data_table.reset_form(form_id);
            }
        });
    });

    // Change password pop-up
    $.fn.zato.data_table.setup_change_password();

    var field_id = '';
    var form_id = '';

    $.each(['', 'edit'], function(ignored, action) {
        $.each(attrs, function(ignored, attr) {
            if(!action) {
                field_id = String.format('#id_{0}', attr);
            }
            else {
                field_id = String.format('#id_{0}-{1}', action, attr);
            }

            $.fn.zato.data_table.set_field_required(field_id);

        });

        // Hm, not exactly the cleanest approach.
        if(action) {
            form_id = '#edit-form';
        }
        else {
            form_id = '#create-form';
        }

    });

    /* Assign form submition handlers.
    */

    $.each(actions, function(ignored, action) {
        $('#'+ action +'-form').submit(function() {
            $.fn.zato.data_table.on_submit(action);
            return false;
        });
    });

    /* Find all multi-row elements and make it possible to add or remove new ones.
    */
    let multirow_elems = $('[class~="multirow"]');

    for(let row_idx=0; row_idx < multirow_elems.length; row_idx++) {

        let elem = $(multirow_elems[row_idx]);
        let parent = elem.parent()

        let elem_id = elem.attr('id')
        let row_id = elem_id + '_0';
        let div_id = 'div_' + row_id;

        console.log('Multirow elem found: '+ elem_id + ' ' + div_id);

        // Create a new div and reattach the element found to it,
        // attaching the div to the parent afterwards.

        // Create the div first ..
        let div = $('<div/>');
        div.attr('id', div_id);

        // .. detach the element ..
        elem.detach();

        // .. attach the element to the new div ..
        elem.appendTo(div)

        // .. and now append the new div to the elem's previous parent.
        div.appendTo(parent);

        // Now, create add / remove buttons
        // (note that we use $.insertAfter which is why the order of addition of buttons is reversed)

        let button_remove = $.fn.zato.data_table.multirow.get_button(row_id, elem_id, '-', false);
        button_remove.insertAfter(elem);

        let button_add = $.fn.zato.data_table.multirow.get_button(row_id, elem_id, '+', true);
        button_add.insertAfter(elem);
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.multirow.get_button = function(row_id, elem_id, text, is_add) {
    let button = $('<button/>');
    let action = is_add ? 'add' : 'remove';

    let button_id = 'button_' + action + '_' + row_id;
    let on_click = `javascript:$.fn.zato.data_table.multirow.add_row("${row_id}", "${elem_id}", ${is_add})`;

    button.attr('id', button_id);
    button.prop('type', 'button');
    button.attr('class', 'multirow-button');
    button.attr('onclick', on_click);
    button.text(text);

    return button
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.multirow.add_row = function(row_id, elem_id, is_add) {

    //console.log(`row_id=${row_id}, elem_id=${elem_id}, is_add=${is_add}`)

    // Find all divs for such an element ID along with the last one in the list
    let existing = $(`div[id^="div_${elem_id}"]`);
    let existing_size = existing.length;
    let last = existing[existing_size-1];

    if(is_add) {

        // Generate a random ID for the new row
        let new_row_id = elem_id + '_' + $.fn.zato.get_random_string();

        // Find the element to be cloned, e.g. a form select element ..
        let div = $('#div_' + row_id);
        let child_selector = `[id=${elem_id}]`;

        // console.log('CHILD '+ child_selector);

        let child = div.children(child_selector)

        // .. clone it ..
        let cloned = $(child).clone(true, true);

        // .. create a new div for the newly cloned element ..
        let new_div = $('<div/>');
        let new_div_id = 'div_' + new_row_id;
        new_div.attr('id', new_div_id);
        new_div.attr('class', 'multirow-added');

        new_div.insertAfter(last);
        cloned.appendTo(new_div);

        // Remove the selected option because there may be some already
        // picked for the first select option.
        cloned.find('option:selected').removeAttr('selected');

        return cloned;

    }
    else {

        // If there is only one such element, it will be the first one, so we cannot remove it,
        // instead, we need to clear it out.
        if(existing_size == 1) {
            let first = $(existing[0]);
            first.find('option:selected').removeAttr('selected');
            return;
        }

        // .. otherwise, remove the last element found.
        last.remove();
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.multirow.remove_multirow_added = function() {
    $('div[class="multirow-added"]').remove();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.multirow.populate_field = function(field_name, source) {

    let _source = null;

    if(typeof(source) === "object") {
        _source = source;
    }
    else {
        _source = JSON.parse(source);
    }

    // console.log('SOURCE 1 '+ source);
    // console.log('SOURCE 2 '+ _source);

    let row_id = 'id_edit-'+ field_name +'_0';
    let elem_id = 'id_edit-'+ field_name;
    let elem = $('#' + elem_id);

    // The very first element needs no cloning ..
    if(_source[0]) {
        elem.val(_source[0]);
    };

    // .. but the rest requires new rows (clones), hence iterating from idx=1;
    for(var idx=1; idx<_source.length; idx++) {
        let item = _source[idx];
        if(item) {
            let cloned = $.fn.zato.data_table.multirow.add_row(row_id, elem_id, true);
            cloned.val(item);
        }
    };
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.on_submit = function(action) {
    var form = $('#' + action +'-form');
    var callback = function(data, status) {
            return $.fn.zato.data_table.on_submit_complete(data, status, action);
        }

    if($.fn.zato.data_table.before_submit_hook) {
        if(!$.fn.zato.data_table.before_submit_hook(form)) {
            return false;
        }
    }

    if($.fn.zato.is_form_valid(form)) {
        return $.fn.zato.data_table._on_submit(form, callback);
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.on_submit_complete = function(data, status, action) {

    if(status == 'success') {

        var json = $.parseJSON(data.responseText);
        var include_tr = true ? action == 'create' : false;
        var row = $.fn.zato.data_table.add_row(json, action, $.fn.zato.data_table.new_row_func, include_tr);

        // There are forms (like the one for subscriptions) where create action does create an object
        // but it is not displayed in current data_table so we treat it as an update actually,
        // and new_row_func_update_in_place is the flag to enable this behaviour.
        var needs_create = action == 'create' && (!$.fn.zato.data_table.new_row_func_update_in_place);

        if(!$.fn.zato.data_table.new_row_func_update_in_place) {
            if($('#data-table').data('is_empty')) {
                $('#data-table tr:last').remove();
            }
        }

        if(needs_create) {
            $('#data-table').data('is_empty', false);
            $('#data-table > tbody:last').prepend(row);
        }
        else {
            var tr = $('#tr_'+ json.id).html(row);
            tr.addClass('updated');
        }
    }

    $.fn.zato.data_table._on_submit_complete(data, status);
    $.fn.zato.data_table.cleanup('#'+ action +'-form');

    if($.fn.zato.data_table.on_submit_complete_callback) {
        $.fn.zato.data_table.on_submit_complete_callback($.fn.zato.data_table.on_submit_complete_callback_args);

        $.fn.zato.data_table.on_submit_complete_callback = null;
        $.fn.zato.data_table.on_submit_complete_callback_args = null;
    }

}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.service_text = function(service, cluster_id) {
    return String.format('<a href="/zato/service/overview/{0}/?cluster={1}">{0}</a>', service, cluster_id);
}

$.fn.zato.data_table.topic_text = function(topic, cluster_id) {
    return String.format('<a href="/zato/pubsub/topic/?cluster={1}&amp;query={0}">{0}</a>', topic, cluster_id);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.ping = function(id) {

    var callback = function(data, status) {
        var success = status == 'success';
        $.fn.zato.user_message(success, data.responseText);
    }

    var url = String.format('./ping/{0}/cluster/{1}/', id, $(document).getUrlParam('cluster'));
    $.fn.zato.post(url, callback, '', 'text');

}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.select_has_value = function(select_option) {
    return select_option.length > 0;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Data table end
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


//
// Misc
//
$.fn.zato.get_random_string = function() {
    var elems = '1234567890qwertyuiopasdfghjklzxcvbnm'.split('');
    var s = "";
    var length = 32;

    for(var i = 0; i < length; i++) {
        s += elems[Math.floor(Math.random() * elems.length)];
    }
    return s;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.to_bool = function(item) {
    var s = new String(item).toLowerCase();
    return(s == "true" || s == 'on'); // 'on' too because it may be a form's field
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.like_bool = function(item) {
    var s = new String(item).toLowerCase();
    return(s == "false" || s == "true" || s == "on" || _.isBoolean(item));
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function(suffix) {
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.dir = function(item) {
    out = [];
    for(attr in item) {
        out.push(attr);
    }
    out.sort();
    return out;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.startswith = function(s, prefix) {
    return s.indexOf(prefix) === 0;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.toggle_css_class = function(elem, remove_class, add_class) {
    $(elem).removeClass(remove_class).addClass(add_class);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.toggle_visible_hidden = function(elem, is_visible) {
    var elem = $(elem);
    var remove_class = '';
    var add_class = '';

    if(is_visible) {
        remove_class = 'hidden';
        add_class = 'visible options-expanded';
        $(elem).prev().addClass("options-expanded", 50);
    }
    else {
        remove_class = 'visible options-expanded';
        add_class = 'hidden';
        $(elem).prev().removeClass("options-expanded", 50);
    }
    $.fn.zato.toggle_css_class(elem, remove_class, add_class);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.toggle_visibility = function(selector) {
    var elems = $(selector);
    $.each(elems, function(idx, elem) {
        elem = $(elem)
        let is_visible = $(elem).hasClass('visible')
        $.fn.zato.toggle_visible_hidden(elem, !is_visible);
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Taken from https://stackoverflow.com/a/901144
$.fn.zato.get_url_param = function(name, url) {
    if (!url) {
        url = window.location.href;
    }
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"), results=regex.exec(url);

    if (!results) {
        return null;
    }

    if (!results[2]) {
        return ''
    };
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.toggle_time = function(link_name, current_value, new_value) {
    var elem = $('#a_' + link_name);
    var href_format = "javascript:$.fn.zato.toggle_time('{0}', '{1}', '{2}')"
    var href_value = String.format(href_format, link_name, new_value, current_value);

    elem.attr('href', href_value);
    elem.html(new_value);

}

$.fn.zato.slugify = function(text) {
    return text.toLowerCase().replace(/ /g,'-').replace(/[^\w-]+/g,'');
}

$.fn.zato.to_json = function(item) {
    return JSON.stringify(item);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.blink_elem = function(elem) {
    var elem = $(elem);
    //elem.fadeTo(300, 0.3, function(){$(this).fadeTo(100, 1.0);});
    elem.removeClass("zato-blinking");
    elem.addClass("zato-blinking", 1);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.add_css_attention = function(elem) {
    $(elem).addClass("zato-validator-attention");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.remove_css_attention = function(elem) {
    elem = $(elem);
    elem.removeClass("zato-validator-attention");
    elem.removeClass("zato-blinking");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.draw_attention_to = function(elem) {
    $.fn.zato.blink_elem(elem);
    $.fn.zato.add_css_attention(elem)
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.cleanup_elem_css_attention = function(elem) {

    $.fn.zato.remove_css_attention(elem);
    $.fn.zato.remove_elem_placeholder(elem);

    let chosen_elems = $.fn.zato.get_chosen_elems_by_elem(elem);
    $.fn.zato.remove_css_attention(chosen_elems);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.cleanup_form_css_attention = function(parent_id) {

    let parent = $(parent_id);

    let to_cleanup_patterns = [
        $.fn.zato.jquery_pattern_required,
        $.fn.zato.jquery_pattern_equals,
        "input[name$='weeks']",
        "input[name$='days']",
        "input[name$='hours']",
        "input[name$='minutes']",
        "input[name$='seconds']",
    ];

    $.each(to_cleanup_patterns, function(idx, pattern) {
        parent.find(pattern).each(function(idx, elem) {
            $.fn.zato.cleanup_elem_css_attention(elem);
        });
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.get_chosen_elems_by_elem = function(elem) {
    let elem_id = $(elem).attr("id");
    let chosen_elem_id = elem_id.replaceAll("-", "_") + "_chosen";
    let chosen_elems = $("#" + chosen_elem_id + " .chosen-single");
    return chosen_elems;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.add_elem_placeholder = function(elem, msg) {
    $(elem).attr("placeholder", msg);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.remove_elem_placeholder = function(elem) {
    $(elem).attr("placeholder", "");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.turn_selects_into_chosen = function(parent_id) {

    var chosen_options = {
        "allow_single_deselect": true,
        "search_contains": true,
    }

    // If a select has an ID beginning with one of this, it will be turned into a chosen element.
    var prefix_list = [
        "service",
        "security",
        "id_out_rest_http_soap_id",
        "id_edit-out_rest_http_soap_id",
        "endpoint_id",
    ]

    $.each(prefix_list, function(ignored, prefix) {
        $(parent_id + ' select[id*="'+ prefix +'"]').chosen(chosen_options);
    })
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.cleanup_chosen = function(parent_id) {

    $(parent_id + ' select[id*="service"]').chosen('destroy');
    $(parent_id + ' select[id*="security"]').chosen('destroy');

}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.show_native_tooltip = function(elem, msg) {
    var elem = $(elem);
    elem.get(0).setCustomValidity(msg);
    elem.get(0).reportValidity();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.is_form_valid = function(form) {

    // Local variables
    var form = $(form);

    // Assume the form is valid by default
    var is_valid = true;

    $.fn.zato.cleanup_form_css_attention("");

    // Confirm that all the elements required to be equal to other elements indeed are
    form.find($.fn.zato.jquery_pattern_equals).each(function(idx, elem) {

        var elem = $(elem)
        let elem_value = elem.val()
        var elem_equals_attr = elem.attr($.fn.zato.validate_equals_attr);

        if(elem_equals_attr) {

            should_be_equal_to_id = elem_equals_attr.replace("equals-", "");
            should_be_equal_to = $("#" + should_be_equal_to_id);
            should_be_equal_to_msg = should_be_equal_to.attr($.fn.zato.validate_equals_msg_attr);

            if(should_be_equal_to) {
                var should_be_equal_to_value = should_be_equal_to.val();
                if(elem_value != should_be_equal_to_value) {

                    should_be_equal_to.get(0).setCustomValidity(should_be_equal_to_msg);
                    form.get(0).reportValidity();

                    $.fn.zato.blink_elem(elem);
                    $.fn.zato.add_css_attention(elem);

                    is_valid = false;
                }
            }
        }
    });

    // Confirm that all the required elements are provided
    form.find($.fn.zato.jquery_pattern_required).each(function(idx, elem) {

        var elem = $(elem)
        let elem_value = elem.val()

        if(!elem_value) {

            let msg = elem.attr($.fn.zato.validate_required_msg_attr);
            let chosen_elems = $.fn.zato.get_chosen_elems_by_elem(elem);

            if(!chosen_elems.length) {
                $.fn.zato.blink_elem(elem);
            }
            else {
                $.fn.zato.blink_elem(chosen_elems);
            }

            $.fn.zato.add_css_attention(elem);
            $.fn.zato.add_css_attention(chosen_elems);

            $.fn.zato.add_elem_placeholder(elem, msg);

            // If we are here, it means that the form is not valid
            is_valid = false;
        }
        else {
            $.fn.zato.cleanup_elem_css_attention(elem);
        }
    })

    // Now, we can return the result to our caller
    return is_valid;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.toggle_tr_blocks = function(is_create, current_value, needs_blink) {

    if(is_create) {
        var prefix = "";
        var suffix = "";
    }
    else {
        var prefix = "edit-";
        var suffix = "-edit";
    }

    // Local variables
    var class_name_main = "zato-toggle"+ suffix;
    var class_name_visible = "zato-toggle-visible"+ suffix;
    var class_name_hidden = "zato-toggle-hidden"+ suffix;
    var class_to_make_visible = "zato-toggle-"+ current_value + suffix;

    // First, hide everything
    $("." + class_name_main).each(function() {
        let elem = $(this);
        elem.removeClass(class_name_visible);
        elem.addClass(class_name_hidden);
        //$.fn.zato.cleanup_elem_css_attention(elem);

        elem.find("select").each(function(idx, elem) {
            $.fn.zato.remove_css_attention(elem);
        });
    });

    // Now, make visible what ought to be enabled
    $("." + class_to_make_visible).each(function() {
        let elem = $(this);
        elem.removeClass(class_name_hidden);
        elem.addClass(class_name_visible);
        if(needs_blink) {
            $.fn.zato.blink_elem(elem);
        };
    });

}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.make_field_required_on_change = function(required_map, current_value) {

    // All the IDs that we are aware of
    var all_ids = [];

    $.each(required_map, function(ignored, values) {
        $.each(values, function(ignored, value) {
            all_ids.push(value);
        });
    });

    // Clean up all the fields first
    $.each(all_ids, function(ignored, elem_id) {
        $.fn.zato.data_table.remove_field_required(elem_id);
    });

    // .. now, make the input one required.
    let field_list = required_map[current_value];
    $.each(field_list, function(ignored, field_id) {
        $.fn.zato.data_table.set_field_required(field_id);
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.set_select_values_on_source_change = function(source_id, target_id, target_items, needs_blink) {

    var target = $("#" + target_id);
    var current_value = $('#' + source_id).val();
    var items_for_target = target_items[target_id];
    var items_for_current_value = items_for_target[current_value];

    // First, remove all the options from the select ..
    target.find("option").remove();

    // .. now, add the newest ones ..
    $(items_for_current_value).each(function() {
        let option = $("<option>");
        option.attr("value", this.id);
        option.text(this.name);
        target.append(option);
    });

    // .. let chosen know that it needs to rebuild its elements ..
    target.trigger('chosen:updated');

    // .. optionally, let the user know that the element changed.
    if(needs_blink) {
        let chosen_elems = $.fn.zato.get_chosen_elems_by_elem(target);
        $.fn.zato.blink_elem(chosen_elems);
    };
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.validate_required_attr     = "data-zato-validator-required";
$.fn.zato.validate_required_msg_attr = "data-zato-validator-required-msg";
$.fn.zato.validate_required_msg      = "This is a required field";

$.fn.zato.validate_equals_attr       = "data-zato-validator-equals";
$.fn.zato.validate_equals_msg_attr   = "data-zato-validator-equals-msg";
$.fn.zato.validate_equals_msg_suffix = " need to be the same";

$.fn.zato.jquery_pattern_required = "*[data-zato-validator-required='required'";
$.fn.zato.jquery_pattern_equals   = "*[data-zato-validator-equals^='equals'";

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.populate_multi_checkbox = function(
    item_list,
    item_html_prefix,
    id_field,
    name_field,
    is_taken_field,
    url_template,
    html_table_id,
    html_elem_id_selector,
    checkbox_field_name,
    disable_if_is_taken
) {
    var table = $("<table/>", {
        "id": html_table_id,
        "class": "multi-select-table"
    })

    for(var idx=0; idx < item_list.length; idx++) {
        var item = item_list[idx];

        var tr = $("<tr/>");
        var td_checkbox = $("<td style='white-space: nowrap'/>");
        var td_toggle = $("<td style='white-space: nowrap'/>");
        var td_item = $("<td style='white-space: nowrap'/>");
        var td_description = $("<td style='white-space: nowrap'/>");
        var td_filler = $("<td style='width:99%'/>");

        var checkbox_id = item_html_prefix + item[id_field];
        var checkbox_name = item_html_prefix + item[name_field];

        if(checkbox_field_name == "id") {
            checkbox_name_field = checkbox_id;
        }
        else {
            checkbox_name_field = checkbox_name
        }

        var checkbox = $("<input/>", {
            "type": "checkbox",
            "id": checkbox_id,
            "name": checkbox_name_field,
        });

        var toggle = $("<label/>", {
            "text": "Toggle",
        });

        if(item[is_taken_field]) {
            checkbox.attr("checked", "checked");
            if(disable_if_is_taken) {
                checkbox.attr("disabled", "disabled");
                toggle.attr("class", "disabled");
            }
            else {
                toggle.attr("for", checkbox_id);
                toggle.attr("class", "toggle");
            }
        }
        else {
            toggle.attr("for", checkbox_id);
            toggle.attr("class", "toggle");
        }

        var item_link = $("<a/>", {
            "href": String.format(url_template, item["cluster_id"], item[name_field], item[id_field]),
            "target": "_blank",
            "text": item[name_field],
        });

        var item_description = $("<span/>", {
            "text": item["description"],
        });

        td_checkbox.append(checkbox);
        td_toggle.append(toggle);
        td_item.append(item_link);
        td_description.append(item_description);

        tr.append(td_checkbox);
        tr.append(td_toggle);
        tr.append(td_item);
        tr.append(td_description);
        tr.append(td_filler);

        table.append(tr);

    }

    $(html_elem_id_selector).html(table);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */


$.fn.zato.pubsub.subscription.before_submit_hook = function(form) {

    var is_valid = true;
    var form = $(form);
    var is_edit = form.attr('id').includes('edit');
    var prefix = is_edit ? 'edit-' : '';

    // Clear anything potentially left over from the previous run
    var rest_chosen_pattern = "#id_" + prefix.replace("-", "_") + "out_rest_http_soap_id_chosen a";
    $.fn.zato.remove_css_attention(rest_chosen_pattern);

    if(!$.fn.zato.is_form_valid(form)) {
        is_valid = false;
    }
    var endpoint_type = $('#id_' + prefix + 'endpoint_type').val();

    var server_id       = $('#id_' + prefix + 'server_id');
    var delivery_method = $('#id_' + prefix + 'delivery_method');
    var out_http_method = $('#id_' + prefix + 'out_http_method');
    var out_rest_http_soap_id = $('#id_' + prefix + 'out_rest_http_soap_id');

    if(endpoint_type == 'rest') {

        if(!delivery_method.val()) {
            $.fn.zato.draw_attention_to(delivery_method);
            is_valid = false;
        }

        if(!out_http_method.val()) {
            $.fn.zato.draw_attention_to(out_http_method);
            is_valid = false;
        }

        if(delivery_method.val() == 'notify') {
            if(!out_rest_http_soap_id.val()) {
                $.fn.zato.draw_attention_to(rest_chosen_pattern);
                is_valid = false;
            }
        }
    }

    var disabled_input = $('#multi-select-input');
    if(disabled_input && disabled_input.length) {
        $.fn.zato.draw_attention_to(disabled_input);
        is_valid = false;
    }
    return is_valid;
}


/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.to_dict = function(item) {
    let out = "{" + Object.entries(item)
        .filter(([k, v]) => v !== undefined && v !== null)
        .map(([k, v]) => `${k}: ${JSON.stringify(v)}`)
        .join(", ") +
    "}";
    return out;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.is_object = function(item) {
    return Object.prototype.toString.call(item) === '[object Object]';
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.slugify = function(data) {
    return data
      .toString()
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^\w\-]+/g, "")
      .replace(/\-\-+/g, "-")
      .replace(/^-+/, "")
      .replace(/-+$/, "");
  }

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.show_tooltip_common = function(placement, elem_id_selector, text, should_draw_attention) {
    if(should_draw_attention) {
        var role = "tooltip-draw-attention";
    }
    else {
        var role = "tooltip";
    }
    let _tooltip = tippy(elem_id_selector, {
        content: text,
        allowHTML: false,
        theme: "dark",
        trigger: "manual",
        placement: placement,
        arrow: true,
        interactive: false,
        inertia: true,
        role: role,
    });
    // It's possible it won't exist, e.g. someone closed it manually.
    if(_tooltip) {
        _tooltip[0].show();
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.show_bottom_tooltip = function(elem_id_selector, text, should_draw_attention) {
    $.fn.zato.show_tooltip_common("bottom", elem_id_selector, text, should_draw_attention);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.show_left_tooltip = function(elem_id_selector, text, should_draw_attention) {
    $.fn.zato.show_tooltip_common("left", elem_id_selector, text, should_draw_attention);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.empty_value = '<span class="form_hint">---</span>';
$.fn.zato.empty_table_cell = String.format('<td>{0}</td>', $.fn.zato.empty_value);

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
