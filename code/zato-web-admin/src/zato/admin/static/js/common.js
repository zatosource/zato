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
$.namespace('zato.cache');
$.namespace('zato.cache.builtin');
$.namespace('zato.cache.builtin.entries');
$.namespace('zato.cache.memcached');
$.namespace('zato.channel');
$.namespace('zato.channel.amqp');
$.namespace('zato.channel.file_transfer');
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
$.namespace('zato.cloud.dropbox');
$.namespace('zato.cloud.openstack');
$.namespace('zato.cloud.openstack.swift');
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
$.namespace('zato.kvdb');
$.namespace('zato.kvdb.data_dict');
$.namespace('zato.kvdb.data_dict.dictionary');
$.namespace('zato.kvdb.data_dict.translation');
$.namespace('zato.kvdb.data_dict.system');
$.namespace('zato.http_soap');
$.namespace('zato.http_soap.details');
$.namespace('zato.load_balancer');
$.namespace('zato.message');
$.namespace('zato.message.json_pointer');
$.namespace('zato.message.live_browser');
$.namespace('zato.message.namespace');
$.namespace('zato.message.xpath');
$.namespace('zato.notif');
$.namespace('zato.notif.cloud');
$.namespace('zato.notif.cloud.openstack');
$.namespace('zato.notif.cloud.openstack.swift');
$.namespace('zato.notif.sql');
$.namespace('zato.outgoing');
$.namespace('zato.outgoing.amqp');
$.namespace('zato.outgoing.ftp');
$.namespace('zato.outgoing.im');
$.namespace('zato.outgoing.im.slack');
$.namespace('zato.outgoing.im.telegram');
$.namespace('zato.outgoing.jms_wmq');
$.namespace('zato.outgoing.mongodb');
$.namespace('zato.outgoing.kafka');
$.namespace('zato.outgoing.ldap');
$.namespace('zato.outgoing.odoo');
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
$.namespace('zato.security.openstack');
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
$.namespace('zato.stats.top_n');

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
    $.fn.zato.post(form.attr('action'), callback, form.serialize());
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
        var success = status == 'success';

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
    if(form.data('bValidator').isValid()) {
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

$.fn.zato.data_table.change_password = function(id, title) {

    var _title = title;
    var name = $.fn.zato.data_table.data[id].name

    if(!_title) {
        _title = 'Change password ';
    }

    $('#change-password-name').text(name);
    $('#id_change_password-id').val(id);

    var div = $('#change_password-div');

    div.prev().text(_title); // prev() is a .ui-dialog-titlebar
    div.dialog('open');
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.setup_change_password = function() {

    var form_id = '#change_password-form';

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
        $('#id_password1').attr('data-bvalidator', 'required,equalto[id_password2]');
        $('#id_password1').attr('data-bvalidator-msg', 'Both fields are required and need to be equal');

        $('#id_password2').attr('data-bvalidator', 'required');
        $('#id_password2').attr('data-bvalidator-msg', 'This is a required field');
    }
    else {
        $('#id_password1').attr('data-bvalidator', 'equalto[id_password2],valempty');
        $('#id_password1').attr('data-bvalidator-msg', 'Fields need to be equal');
    }

    change_password_form.bValidator();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table._create_edit = function(action, title, id, remove_multirow) {

    let _remove_multirow = remove_multirow === undefined ? true : remove_multirow;

    // Clean up all the multirow elements that were possibly
    // automatically generated for that form.
    if(_remove_multirow) {
        $.fn.zato.data_table.multirow.remove_multirow_added();
    }

    if(action == 'edit') {

        var form = $(String.format('#{0}-form', action));
        var name_prefix = action + '-';
        var id_prefix = String.format('#id_{0}', name_prefix);
        var instance = $.fn.zato.data_table.data[id];
        $.fn.zato.form.populate(form, instance, name_prefix, id_prefix);
    }

    var div = $(String.format('#{0}-div', action));
    div.prev().text(title); // prev() is a .ui-dialog-titlebar
    div.dialog('open');
}

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
        html_elem = $('#id_' + prefix + name);
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
    $(field_id).attr('data-bvalidator', 'required');
    $(field_id).attr('data-bvalidator-msg', 'This is a required field');
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
            close: function(e, ui) {
                $.fn.zato.data_table.reset_form(form_id);
            }
        });
    });

    // Change password pop-up
    $.fn.zato.data_table.setup_change_password();

    /* Prepare the validators here so that it's all still a valid HTML
    from the http://users.skynet.be/mgueury/mozilla/ point of view
    even with bValidator's custom attributes.
    */

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

        var options = {};
        if($.fn.zato.data_table.on_before_element_validation) {
            options['onBeforeElementValidation'] = $.fn.zato.data_table.on_before_element_validation;
        }

        $(form_id).bValidator(options);

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
    let existing_size = existing.size();
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

    return $.fn.zato.data_table._on_submit(form, callback);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.on_submit_complete = function(data, status, action) {

    if(status == 'success') {

        console.log('CCC '+ data.responseText);

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

$.fn.zato.toggle_visible_hidden = function(elem, is_visible) {
    var elem = $(elem);
    var remove_class = '';
    var add_class = '';

    if(is_visible) {
        remove_class = 'hidden';
        add_class = 'visible';
    }
    else {
        remove_class = 'visible';
        add_class = 'hidden';
    }
    $(elem).removeClass(remove_class).addClass(add_class);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.toggle_visibility = function(selector) {
    var elems = $(selector);
    $.each(elems, function(idx, elem) {
        $.fn.zato.toggle_visible_hidden(elem, !$(elem).hasClass('visible'));
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

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.empty_value = '<span class="form_hint">---</span>';
$.fn.zato.empty_table_cell = String.format('<td>{0}</td>', $.fn.zato.empty_value);

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// For Brython

window.zato_select_data_target = null;
window.zato_select_data_target_items = {};
window.zato_dyn_form_skip_edit = null;
window.zato_dyn_form_skip_clear_field = [];

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
