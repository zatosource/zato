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
$.namespace('zato.channel.jms_wmq');
$.namespace('zato.channel.stomp');
$.namespace('zato.channel.web_socket');
$.namespace('zato.channel.zmq');
$.namespace('zato.cloud');
$.namespace('zato.cloud.aws');
$.namespace('zato.cloud.aws.s3');
$.namespace('zato.cloud.openstack');
$.namespace('zato.cloud.openstack.swift');
$.namespace('zato.cluster');
$.namespace('zato.cluster.servers');
$.namespace('zato.data_table');
$.namespace('zato.definition');
$.namespace('zato.definition.amqp');
$.namespace('zato.definition.cassandra');
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
$.namespace('zato.http_soap.audit');
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
$.namespace('zato.outgoing.jms_wmq');
$.namespace('zato.outgoing.odoo');
$.namespace('zato.outgoing.sql');
$.namespace('zato.outgoing.stomp');
$.namespace('zato.outgoing.zmq');
$.namespace('zato.pattern.delivery');
$.namespace('zato.pattern.delivery.in_doubt');
$.namespace('zato.pubsub.endpoint');
$.namespace('zato.pubsub.endpoint_queue');
$.namespace('zato.pubsub.subscription');
$.namespace('zato.pubsub.topic');
$.namespace('zato.pubsub.message');
$.namespace('zato.pubsub.message.details');
$.namespace('zato.pubsub.message.publish');
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
$.namespace('zato.security.tech_account');
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

//
// Forms
//

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


/* Takes a form (ID or a jQuery object), a business object and populates the
form with values read off the object. The 'name' and 'id' attributes of the
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

    for(field_name in fields) {
        //console.log('Field -> `'+ field_name +'`');
        if(field_name.indexOf(name_prefix) === 0 || field_name == 'id') {
            field_name = field_name.replace(name_prefix, '');
            for(item_attr in instance) {
                //console.log('Item attr -> `'+ item_attr +'`');
                if(item_attr == field_name) {
                    value = instance[item_attr];
                    console.log('Field/value: `'+ item_attr + '` `'+ value +'`');
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

// /////////////////////////////////////////////////////////////////////////////
// Data table begin
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.data = {}
$.fn.zato.data_table.on_submit_complete_callback = null;
$.fn.zato.data_table.on_submit_complete_callback_args = null;

$.fn.zato.data_table.row_updated = function(id) {
    var tr = $('#tr_'+ id)
    tr.addClass('updated');

    return tr;
}

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

            //console.log('td_idx:`'+ td_idx +'`, attr_name:`'+ attr_name +'`, attr_value:`'+ attr_value + '`');

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

$.fn.zato.data_table.form_info = function(button) {
    var form = $(button).closest('form');
    var form_id = form.attr('id');
    return {
        'form': form,
        'form_id': '#' + form_id,
    }
}

$.fn.zato.data_table.close = function(button) {
    var form_info = $.fn.zato.data_table.form_info(button);
    $.fn.zato.data_table.cleanup(form_info['form_id']);
}

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

$.fn.zato.data_table._on_submit = function(form, callback) {
    $.fn.zato.post(form.attr('action'), callback, form.serialize());
}

$.fn.zato.data_table.remove_row = function(td_prefix, instance_id) {
    $(td_prefix + instance_id).parent().remove();
    $.fn.zato.data_table.data[instance_id] = null;

    if($('#data-table tr').length == 1) {
        var row = '<tr><td colspan="100">No results</td></tr>';
        $('#data-table > tbody:last').prepend(row);
        $('#data-table').data('is_empty', true);
    }
}

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

    console.log('Instance: ' + instance);

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

$.fn.zato.data_table._create_edit = function(action, title, id) {

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

$.fn.zato.data_table.add_row = function(data, action, new_row_func, include_tr) {

    var item = new $.fn.zato.data_table.class_();
    var form = $(String.format('#{0}-form', action));

    var prefix;
    if(action == 'edit') {
        prefix = action + '-';
    }
    else {
        prefix = '';
    }

    var name = '';
    var id = '';
    var tag_name = '';
    var html_elem;

    $.each(form.serializeArray(), function(idx, elem) {
        name = elem.name.replace(prefix, '');
        html_elem = $('#id_' + prefix + name);
        tag_name = html_elem.prop('tagName');

        if(tag_name && html_elem.prop('type') == 'checkbox') {
            item[name] = html_elem.is(':checked');
        }

        else {
            item[name] = elem.value;
        }

        if(tag_name && tag_name.toLowerCase() == 'select') {
            item[name + '_select'] = $('#id_' + prefix + name + ' :selected').text();
        }

    })

    if(!item.id) {
        item.id = data.id;
    }

    $.fn.zato.data_table.data[item.id] = item;

    return new_row_func(item, data, include_tr);
}

$.fn.zato.data_table.set_field_required = function(field_id) {
    $(field_id).attr('data-bvalidator', 'required');
    $(field_id).attr('data-bvalidator-msg', 'This is a required field');
}

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

        // Doh, not exactly the cleanest approach.
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
}

$.fn.zato.data_table.on_submit = function(action) {
    var form = $('#' + action +'-form');
    var callback = function(data, status) {
            return $.fn.zato.data_table.on_submit_complete(data,
                status, action);
        }

    if($.fn.zato.data_table.before_submit_hook) {
        if(!$.fn.zato.data_table.before_submit_hook(form)) {
            return false;
        }
    }

    return $.fn.zato.data_table._on_submit(form, callback);
}

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

$.fn.zato.data_table.service_text = function(service, cluster_id) {
    return String.format('<a href="/zato/service/overview/{0}/?cluster={1}">{0}</a>', service, cluster_id);
}

$.fn.zato.data_table.ping = function(id) {

    var callback = function(data, status) {
        var success = status == 'success';
        $.fn.zato.user_message(success, data.responseText);
    }

    var url = String.format('./ping/{0}/cluster/{1}/', id, $(document).getUrlParam('cluster'));
    $.fn.zato.post(url, callback, '', 'text');

}

$.fn.zato.data_table.select_has_value = function(select_option) {
    return select_option.length > 0;
}

// /////////////////////////////////////////////////////////////////////////////
// Data table end
// /////////////////////////////////////////////////////////////////////////////


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

$.fn.zato.to_bool = function(item) {
    var s = new String(item).toLowerCase();
    return(s == "true" || s == 'on'); // 'on' too because it may be a form's field
}

$.fn.zato.like_bool = function(item) {
    var s = new String(item).toLowerCase();

    return(s == "false" || s == "true" || s == "on" || _.isBoolean(item));
}

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}

if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function(suffix) {
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
}

$.fn.zato.dir = function(item) {
    out = [];
    for(attr in item) {
        out.push(attr);
    }
    out.sort();
    return out;
}

$.fn.zato.startswith = function(s, prefix) {
    return s.indexOf(prefix) === 0;
}

$.fn.zato.toggle_visible_hidden = function(id, is_visible) {
    var elem = $('#'+ id);
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

$.fn.zato.empty_value = '<span class="form_hint">---</span>';

// For Brython

window.zato_select_data_target = null;
window.zato_select_data_target_items = {};
window.zato_dyn_form_skip_edit = null;
