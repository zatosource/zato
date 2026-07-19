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
$.namespace('zato.as2_keystore');
$.namespace('zato.audit_log');
$.namespace('zato.b2b');
$.namespace('zato.b2b.control_numbers');
$.namespace('zato.b2b.reports');
$.namespace('zato.channel');
$.namespace('zato.channel.amqp');
$.namespace('zato.channel.as4');
$.namespace('zato.channel.as4.data_table');
$.namespace('zato.channel.ibm_mq');
$.namespace('zato.channel.ibm_mq.data_table');
$.namespace('zato.channel.kafka');
$.namespace('zato.channel.kafka.data_table');
$.namespace('zato.channel.hl7');
$.namespace('zato.channel.hl7.mllp');
$.namespace('zato.channel.hl7.mllp.data_table');
$.namespace('zato.channel.hl7.mllp.editor');
$.namespace('zato.channel.hl7.mllp.wizard');
$.namespace('zato.channel.hl7.mllp.wizard.forms');
$.namespace('zato.channel.hl7.mllp.wizard.destinations');
$.namespace('zato.channel.hl7.mllp.wizard.review');
$.namespace('zato.channel.hl7.rest');
$.namespace('zato.channel.hl7.rest.data_table');
$.namespace('zato.channel.openapi');
$.namespace('zato.channel.openapi.data_table');
$.namespace('zato.cloud');
$.namespace('zato.cloud.aws');
$.namespace('zato.cloud.confluence');
$.namespace('zato.cloud.jira');
$.namespace('zato.cloud.microsoft_365');
$.namespace('zato.cloud.microsoft_fabric');
$.namespace('zato.cloud.microsoft_power_automate');
$.namespace('zato.cloud.salesforce');
$.namespace('zato.cluster');
$.namespace('zato.cluster.servers');
$.namespace('zato.common');
$.namespace('zato.common.security');
$.namespace('zato.dashboard_kit');
$.namespace('zato.data_table');
$.namespace('zato.data_table.multirow');
$.namespace('zato.definition');
$.namespace('zato.definition.amqp');
$.namespace('zato.destinations');
$.namespace('zato.docs');
$.namespace('zato.email');
$.namespace('zato.email.imap');
$.namespace('zato.email.smtp');
$.namespace('zato.form');
$.namespace('zato.form_highlight');
$.namespace('zato.form_tabs');
$.namespace('zato.gateway');
$.namespace('zato.gateway.mcp');
$.namespace('zato.gateway.mcp.data_table');
$.namespace('zato.groups');
$.namespace('zato.groups.data_table');
$.namespace('zato.groups.members');
$.namespace('zato.health_check');
$.namespace('zato.how_it_works');
$.namespace('zato.http_soap');
$.namespace('zato.http_soap.details');
$.namespace('zato.http_soap.openapi');
$.namespace('zato.live_form_updates');
$.namespace('zato.logging');
$.namespace('zato.logging.levels');
$.namespace('zato.logging.destinations');
$.namespace('zato.data_table_widget');
$.namespace('zato.ide');
$.namespace('zato.invoker');
$.namespace('zato.message');
$.namespace('zato.monitoring');
$.namespace('zato.monitoring.wizard');
$.namespace('zato.outgoing');
$.namespace('zato.outgoing.amqp');
$.namespace('zato.outgoing.as2');
$.namespace('zato.outgoing.as2.data_table');
$.namespace('zato.outgoing.as4');
$.namespace('zato.outgoing.as4.data_table');
$.namespace('zato.outgoing.es');
$.namespace('zato.outgoing.ftp');
$.namespace('zato.outgoing.hl7');
$.namespace('zato.outgoing.hl7.fhir');
$.namespace('zato.outgoing.hl7.fhir.data_table');
$.namespace('zato.outgoing.hl7.mllp');
$.namespace('zato.outgoing.hl7.mllp.data_table');
$.namespace('zato.outgoing.mongodb');
$.namespace('zato.outgoing.graphql');
$.namespace('zato.outgoing.graphql.data_table');
$.namespace('zato.outgoing.ibm_mq');
$.namespace('zato.outgoing.ibm_mq.data_table');
$.namespace('zato.outgoing.kafka');
$.namespace('zato.outgoing.kafka.data_table');
$.namespace('zato.outgoing.ldap');
$.namespace('zato.outgoing.odata');
$.namespace('zato.outgoing.odata.data_table');
$.namespace('zato.outgoing.odoo');
$.namespace('zato.outgoing.redis');
$.namespace('zato.outgoing.sftp');
$.namespace('zato.outgoing.sftp.data_table');
$.namespace('zato.outgoing.smb');
$.namespace('zato.outgoing.smb.data_table');
$.namespace('zato.outgoing.soap');
$.namespace('zato.outgoing.soap.data_table');
$.namespace('zato.outgoing.sql');
$.namespace('zato.pubsub');
$.namespace('zato.pubsub.topic');
$.namespace('zato.pubsub.subscription');
$.namespace('zato.pubsub.subscription.data_table');
$.namespace('zato.query');
$.namespace('zato.rate_limiting');
$.namespace('zato.response_caching');
$.namespace('zato.scheduler');
$.namespace('zato.security');
$.namespace('zato.security.apikey');
$.namespace('zato.security.basic_auth');
$.namespace('zato.security.jwt');
$.namespace('zato.security.ntlm');
$.namespace('zato.security.oauth');
$.namespace('zato.security.posture');
$.namespace('zato.security.tier');
$.namespace('zato.security.wss');
$.namespace('zato.security.wss.data_table');
$.namespace('zato.service');
$.namespace('zato.settings');
$.namespace('zato.sms');
$.namespace('zato.stats');
$.namespace('zato.stats.custom');
$.namespace('zato.system');
$.namespace('zato.updates');
$.namespace('zato.vendors');
$.namespace('zato.vendors.keysight');
$.namespace('zato.vendors.keysight.vision');

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.post = function(url, callback, data, data_type, context) {
    if(!data) {
        data = '';
    }

    if(!data_type) {
        data_type = 'json';
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

$.fn.zato.user_message = function(is_success, msg) {

    // Style the message according to its outcome ..
    var messageContainer = $('#user-message');
    var cssClass = is_success ? 'user-message-success' : 'user-message-failure';

    messageContainer.removeClass('user-message-success user-message-failure').addClass(cssClass);
    messageContainer.text(msg);

    // .. and make it visible on the page.
    $('#user-message-div').show();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table._submitting = false;

$.fn.zato.show_action_overlay = function(label) {
    console.log('[DEBUG] show_action_overlay: label=' + label + ', _submitting was=' + $.fn.zato.data_table._submitting);
    $.fn.zato.data_table._submitting = true;
    $('#create-form input[type="submit"], #edit-form input[type="submit"]').prop('disabled', true);
}

$.fn.zato.hide_action_overlay = function() {
    console.log('[DEBUG] hide_action_overlay: _submitting was=' + $.fn.zato.data_table._submitting);
    $.fn.zato.data_table._submitting = false;
    $('#create-form input[type="submit"], #edit-form input[type="submit"]').prop('disabled', false);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

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
    var skip_boolean = ['in_lb', 'validate_tls']; // A list of boolean fields that should be treated as though they were regular text

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
                        if(name_prefix) {
                            form_elem.data('zato-original-value', value);
                        }
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

// Returns the cell of a given logical column in a row - the index comes from the page's
// get_columns list, so callers survive any reordering of the table's cells.
$.fn.zato.data_table.get_cell = function(id, column_name) {
    var columns = $.fn.zato.data_table.get_columns();
    var cell_index = columns.indexOf(column_name);
    return $('#tr_' + id).find('td').eq(cell_index);
}

$.fn.zato.data_table.row_updated = function(id) {

    // Only one row carries the highlight at a time - marking this row takes it away
    // from whichever row was highlighted before.
    $('#data-table tr.updated').removeClass('updated');

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
            var name_value_elem = $(td).find('.name-value');
            var attr_value = name_value_elem.length ? name_value_elem.text().trim() : $(td).text().trim();

            // console.log('td_idx:`'+ td_idx +'`, attr_name:`'+ attr_name +'`, attr_value:`'+ attr_value + '`');

            // Don't bother with ignored attributes.
            if(attr_name[0] != '_') {
                if(attr_name === 'sec_base_id') {
                    console.log('DEBUG common.js: sec_base_id attr_value=' + JSON.stringify(attr_value) + ', td text=' + JSON.stringify($(td).text()));
                }
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

// A tablesorter textExtraction function - cells that carry a data-sort-value attribute
// sort by that value instead of their visible text, e.g. "time ago" cells sort by their numeric age.
$.fn.zato.data_table.text_extraction = function(node) {
    var sort_value = node.getAttribute('data-sort-value');
    if(sort_value !== null) {
        return sort_value;
    }
    return node.textContent;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.reset_form = function(form_id) {
    var form = $(form_id);

    form.find('.zato-unique-indicator').remove();
    form.find('input[type="text"]').removeData('zato-original-value');

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
        $('#user-message-div').hide();
    }
    else {
        msg = data.responseText;
        $.fn.zato.user_message(false, msg);
    }

    $.fn.zato.hide_action_overlay();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table._on_submit = function(form, callback) {
    console.log('[DEBUG] _on_submit: Form submission starting');
    console.log('[DEBUG] _on_submit: Form element:', form);
    console.log('[DEBUG] _on_submit: Form action:', form.attr('action'));

    // Check if this is a subscription form and validate topics
    var formAction = form.attr('action');
    if (formAction && formAction.includes('/pubsub/subscription/')) {
        var topicSelect = form.find('select[name="topic_id"], select[name="edit-topic_id"]');
        if (topicSelect.length > 0) {
            var selectedTopics = topicSelect.val();
            console.log('[DEBUG] _on_submit: Topic validation - selected topics:', JSON.stringify(selectedTopics));

            if (!selectedTopics || selectedTopics.length === 0) {
                alert('Please select at least one topic before submitting.');
                console.log('[DEBUG] _on_submit: Form submission blocked - no topics selected');
                return;
            }
        }
    }

    // Trim all text inputs before serialization
    form.find('input[type="text"], textarea').each(function() {
        $(this).val($(this).val().trim());
    });

    // Log all form inputs before serialization
    form.find(':input').each(function() {
        var $this = $(this);
        console.log('[DEBUG] _on_submit: Input name=' + $this.attr('name') + ', type=' + $this.attr('type') + ', value=' + JSON.stringify($this.val()));
    });

    let serialized = form.serialize();
    console.log('[DEBUG] _on_submit: Serialized form data:', serialized);

    // Parse serialized data to show structure
    var formData = {};
    serialized.split('&').forEach(function(pair) {
        var parts = pair.split('=');
        var key = decodeURIComponent(parts[0]);
        var value = decodeURIComponent(parts[1] || '');
        if (formData[key]) {
            if (!Array.isArray(formData[key])) {
                formData[key] = [formData[key]];
            }
            formData[key].push(value);
        } else {
            formData[key] = value;
        }
    });
    console.log('[DEBUG] _on_submit: Parsed form data:', JSON.stringify(formData, null, 2));

    $.fn.zato.post(form.attr('action'), callback, serialized);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.remove_row = function(td_prefix, instance_id) {
    var td = $(td_prefix + instance_id);
    var tr = td.length ? td.parent() : $(document.getElementById('tr_' + instance_id));
    tr.animate({opacity: 0}, 200, function() {
        tr.remove();
        $.fn.zato.data_table.data[instance_id] = null;
        if($('#data-table tr').length == 1) {
            var row = '<tr><td colspan="100">No results</td></tr>';
            $('#data-table > tbody:last').prepend(row);
            $('#data-table').data('is_empty', true);
        }
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// One-shot overrides for _bounce_row - inline editing sets them so the confirmation
// appears next to the link that was actually clicked instead of the row's Edit link.
$.fn.zato.data_table.bounce_target_finder = null;
$.fn.zato.data_table.bounce_placement = null;

$.fn.zato.data_table._bounce_row = function(tr, action) {
    if(action === 'edit') {
        var target = null;
        var placement = 'top';

        var finder = $.fn.zato.data_table.bounce_target_finder;
        if(finder) {
            $.fn.zato.data_table.bounce_target_finder = null;
            target = finder(tr);
        }

        var custom_placement = $.fn.zato.data_table.bounce_placement;
        if(custom_placement) {
            $.fn.zato.data_table.bounce_placement = null;
            placement = custom_placement;
        }

        if(!target) {
            var edit_link = tr.find('a[href*="edit"]')[0];
            target = edit_link ? edit_link : tr.find('td:visible').last()[0];
        }
        var instance = tippy(target, {
            content: 'OK, saved',
            placement: placement,
            trigger: 'manual',
            hideOnClick: false,
            theme: 'dark',
            allowHTML: false
        });
        instance.show();
        setTimeout(function() {
            instance.hide();
            setTimeout(function() {
                instance.destroy();
            }, 200);
        }, 600);
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

        $.fn.zato.hide_action_overlay();

        if(success) {
            if(_remove_tr) {
                $.fn.zato.data_table.remove_row(td_prefix, instance.id);
            }

            if(on_success_callback) {
                on_success_callback();
            }
        }
    }

    var callback = function(ok) {
        if(ok) {
            $.fn.zato.show_action_overlay('Deleting ...');
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

        var _id = $('#id_change_password-id').val();
        var _secret_type = $('#change_password-form').data('secret-type') || $('#secret_type_id').val() || 'password';

        var _callback = function(data, status) {
            var tr = $.fn.zato.data_table.row_updated(_id);
            $.fn.zato.data_table._on_submit_complete(data, status);

            var link = tr.find('a').filter(function() {
                var text = $(this).text().toLowerCase();
                return text.indexOf('change') !== -1 && (text.indexOf('password') !== -1 || text.indexOf('key') !== -1 || text.indexOf('secret') !== -1);
            }).first();

            if(link.length) {
                var tooltip_text = 'OK, ' + _secret_type + ' changed';
                var _tooltip = tippy(link[0], {
                    content: tooltip_text,
                    allowHTML: false,
                    theme: 'dark',
                    trigger: 'manual',
                    placement: 'top',
                    arrow: true,
                    interactive: false,
                    inertia: true,
                });
                var instance = Array.isArray(_tooltip) ? _tooltip[0] : _tooltip;
                if(instance) {
                    instance.show();
                    setTimeout(function() {
                        instance.hide();
                        setTimeout(function() { instance.destroy(); }, 300);
                    }, 1200);
                }
            }
        }

        $.fn.zato.post(form.attr('action'), _callback, form.serialize());
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
    $('#change_password-form').data('secret-type', _label_lower);

    $('#change-password-name').text(name);
    $('#id_change_password-id').val(id);

    var div = $('#change_password-div');

    div.prev().css('cursor', 'move');
    div.prev().html('<span class="ui-dialog-title-text" style="user-select: text; cursor: text;">' + _title + '</span>');
    div.prev().find('.ui-dialog-title-text').on('mousedown selectstart dblclick', function(e) { e.stopPropagation(); });
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
        $("#id_password").attr($.fn.zato.validate_required_attr, "required");
        $('#id_password').attr($.fn.zato.validate_required_msg_attr, $.fn.zato.validate_required_msg);
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table._create_edit = function(action, title, id, remove_multirow, needs_populate) {

    // Local variables
    var form_id = String.format('#{0}-form', action)
    var needs_populate = needs_populate !== false;

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

        if(needs_populate) {
            $.fn.zato.form.populate(form, instance, name_prefix, id_prefix);
        }
    }

    div.prev().css('cursor', 'move');
    div.prev().html('<span class="ui-dialog-title-text" style="user-select: text; cursor: text;">' + title + '</span>');
    div.prev().find('.ui-dialog-title-text').on('mousedown selectstart dblclick', function(e) { e.stopPropagation(); });
    div.dialog('open');

    // Auto-focus the name field if one exists, placing the cursor at position 0
    var name_field_id = (action == 'edit') ? '#id_edit-name' : '#id_name';
    var name_field = div.find(name_field_id);
    if(name_field.length) {
        name_field.trigger('focus');
        if(name_field[0].setSelectionRange) {
            name_field[0].setSelectionRange(0, 0);
        }
    }

    $.fn.zato.turn_selects_into_chosen(div_id);

    // Start live form updates polling if any configs are registered for this action,
    // but skip if all configs use badge_picker handler (those start polling after their async load)
    var _lfu_configs = $.fn.zato.live_form_updates._get_configs(action);
    var _all_badge_picker = _lfu_configs.length > 0;
    for(var _i = 0; _i < _lfu_configs.length; _i++) {
        if(_lfu_configs[_i].handler !== 'badge_picker') {
            _all_badge_picker = false;
            break;
        }
    }
    if(_all_badge_picker) {
        console.log('[live_form_updates] _create_edit: skipping auto-start for action=' + action + ' (all configs are badge_picker, will start after load)');
    } else {
        console.log('[live_form_updates] _create_edit: calling start for action=' + action);
        $.fn.zato.live_form_updates.start(action);
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.edit = function(action, title, id, remove_multirow) {
    $.fn.zato.data_table._create_edit(action, title, id, remove_multirow);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Opens the page's create form when the URL carries create=1, e.g. when another page
// links here so that a missing definition can be created right away.
$.fn.zato.data_table.maybe_open_create_form = function(create_func) {

    // Only act when the URL explicitly asks for it ..
    var should_create = $(document).getUrlParam('create');

    if(should_create != '1') {
        return;
    }

    // .. and open the create form.
    create_func();
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

    // For edit and create actions, use server response data when available
    if((action == 'edit' || action == 'create') && data) {
        // Start with server response data
        Object.keys(data).forEach(function(key) {
            if(key !== 'message' && data[key] !== undefined && data[key] !== null) {
                instance[key] = data[key];
            }
        });
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

    if(!instance.name && data.name) {
        instance.name = data.name;
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
            close: function(e, ui) {
                $.fn.zato.data_table.reset_form(form_id);
                $.fn.zato.live_form_updates.stop(action);
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

    if($.fn.zato.data_table._submitting) {
        return false;
    }

    var form = $('#' + action +'-form');

    var callback = function(data, status) {
            return $.fn.zato.data_table.on_submit_complete(data, status, action);
        }

    if($.fn.zato.data_table.before_submit_hook) {
        var hook_result = $.fn.zato.data_table.before_submit_hook(form);
        if(!hook_result) {
            return false;
        }
    }

    var form_valid = $.fn.zato.is_form_valid(form);

    if(form_valid) {

        var unique_ok = $.fn.zato.validate_unique_on_submit(form);

        if(!unique_ok) {
            return false;
        }

        var label = action === 'create' ? 'Creating ...' : 'Saving ...';
        $.fn.zato.show_action_overlay(label);
        return $.fn.zato.data_table._on_submit(form, callback);
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.on_submit_complete = function(data, status, action) {
    console.log('[DEBUG] on_submit_complete: Starting with status=' + JSON.stringify(status) + ', action=' + JSON.stringify(action));

    if(status == 'success') {
        console.log('[DEBUG] on_submit_complete: Raw response data=' + JSON.stringify(data.responseText));

        var json = $.parseJSON(data.responseText);
        console.log('[DEBUG] on_submit_complete: Parsed JSON=' + JSON.stringify(json));

        var include_tr = true ? action == 'create' : false;
        var row = $.fn.zato.data_table.add_row(json, action, $.fn.zato.data_table.new_row_func, include_tr);
        console.log('[DEBUG] on_submit_complete: Generated row HTML=' + JSON.stringify(row));

        // Special handling for subscription - make sure we're using the actual UUID sub_key from the server response
        if (json.sub_key && json.sub_key.indexOf('-') > -1 && $.fn.zato.data_table.data[json.id]) {
            console.log('[DEBUG] on_submit_complete: Setting UUID sub_key on data object:', json.sub_key);
            $.fn.zato.data_table.data[json.id].sub_key = json.sub_key;
        }

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
            // The new row takes over the highlight from any previously updated one.
            $('#data-table tr.updated').removeClass('updated');
            $('#data-table').data('is_empty', false);
            $('#data-table > tbody:last').prepend(row);
        }
        else {
            var tr = $(document.getElementById('tr_'+ json.id));
            tr.html(row);
            $.fn.zato.data_table.row_updated(json.id);
            $.fn.zato.data_table._bounce_row(tr, 'edit');
        }
    }

    $.fn.zato.data_table._on_submit_complete(data, status);
    $.fn.zato.data_table.cleanup('#'+ action +'-form');

    if($.fn.zato.data_table.on_submit_complete_callback) {
        $.fn.zato.data_table.on_submit_complete_callback($.fn.zato.data_table.on_submit_complete_callback_args);

        $.fn.zato.data_table.on_submit_complete_callback = null;
        $.fn.zato.data_table.on_submit_complete_callback_args = null;
    }

    $.fn.zato.hide_action_overlay();

}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.service_text = function(service, cluster_id) {
    return String.format('<a href="/zato/service/ide/service/{0}/?cluster={1}">{0}</a>', service, cluster_id);
}

$.fn.zato.data_table.topic_text = function(topic, cluster_id) {
    return String.format('<a href="/zato/pubsub/topic/?cluster={1}&amp;query={0}">{0}</a>', topic, cluster_id);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.data_table.ping = function(id, link_elem) {
    var url = String.format('./ping/{0}/cluster/{1}/', id, $(document).getUrlParam('cluster'));
    $.fn.zato.action_runner.run({
        link_elem: link_elem,
        url: url,
        details_modal_title: 'Ping response'
    });
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
    if (s == "true" || s == "on" || s == "false") {
        return true;
    }
    return _.isBoolean(item);
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

    // Elements without an ID, e.g. inputs in inline edit forms, have no chosen counterpart.
    if(elem_id === undefined) {
        return $();
    }

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
        $(parent_id + ' select[id*="'+ prefix +'"]').not('.noChosen').chosen(chosen_options);
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

    var form = $(form);

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

    var first_invalid = null;

    form.find($.fn.zato.jquery_pattern_required).each(function(idx, elem) {

        var elem = $(elem)
        let elem_value = elem.val()

        if(!elem_value || !elem_value.trim()) {

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

            // Track the first invalid field so we can focus it later
            if (!first_invalid) {
                first_invalid = elem;
            }

            // If we are here, it means that the form is not valid
            is_valid = false;
        }
        else {
            $.fn.zato.cleanup_elem_css_attention(elem);
        }
    })

    // If the first invalid field is inside a hidden tab panel, switch to that tab first
    if (first_invalid) {
        var hidden_panel = first_invalid.closest('.dashboard-tab-panel[hidden]');
        if (hidden_panel.length) {
            var panel_id = hidden_panel.attr('id');
            var tab_container = hidden_panel.closest('.ui-dialog-content, form').first();
            var tab_buttons = tab_container.find('.dashboard-tab');
            tab_buttons.each(function() {
                var panel_suffix = $(this).data('tab');
                if (panel_id && panel_id.endsWith(panel_suffix)) {
                    $(this).trigger('click');
                    return false;
                }
            });
        }
        first_invalid.focus();
    }

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
            "data-id": item[id_field],
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

// Reusable "time ago" cells - each element with the .zato-time-ago class and a data-time-utc attribute
// is turned into a humanized link, e.g. "3 minutes ago", with a click-triggered tippy that shows
// the full timestamp both in the browser's timezone and in UTC.
$.fn.zato.time_ago = {};

// A click on the countdown text flips this - while it is true the ticker stands still
// and no refresh requests go out.
$.fn.zato.time_ago.paused = false;

$.fn.zato.time_ago.config = {
    'never_label': 'Never',
    'never_sort_value': '99999999999',
    'just_now_label': 'Just now',
    'ago_label': 'ago',
    'ago_row_label': 'Ago',
    'duration_row_label': 'Duration',
    'duration_ms_label': 'ms',
    'tooltip_title': 'Last run',

    // The logical column whose cell wears the highlight badge while the tooltip is open -
    // set to an empty string on pages that have no such column.
    'highlight_column': 'name',
    'utc_label': 'UTC',
    'tippy_placement': 'top',
    'refresh_interval_ms': 5000,
    'spinner_min_visible_ms': 350,
    'value_fade_ms': 250,

    // How dim a changing value gets mid-fade - 1 is fully opaque, 0 is invisible.
    // A subtle dip is enough to signal the change without drawing the eye.
    'value_fade_opacity': 0.5,
    'countdown_prefix': 'Refreshes in ',
    'countdown_suffix': 's',
    'paused_label': 'Refresh paused',

    // Only one of these is meant to be active at a time - either the textual
    // countdown next to the column name or the draining progress bar under it.
    'countdown_enabled': true,
    'progress_enabled': false,
    'units': [
        {'name': 'week',   'seconds': 604800},
        {'name': 'day',    'seconds': 86400},
        {'name': 'hour',   'seconds': 3600},
        {'name': 'minute', 'seconds': 60},
        {'name': 'second', 'seconds': 1},
    ]
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.time_ago.humanize = function(age_seconds) {
    var config = $.fn.zato.time_ago.config;

    // Anything below one second reads better as a fixed label than as "0 seconds ago".
    if(age_seconds < 1) {
        return config.just_now_label;
    }

    var units = config.units;
    var out = '';

    // Find the largest unit that fits, e.g. 3700 seconds turn into "1 hour ago".
    for(var unit_idx = 0; unit_idx < units.length; unit_idx++) {
        var unit = units[unit_idx];
        if(age_seconds >= unit.seconds) {
            var count = Math.floor(age_seconds / unit.seconds);
            var suffix = count == 1 ? '' : 's';
            out = count + ' ' + unit.name + suffix + ' ' + config.ago_label;
            break;
        }
    }

    return out;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Like humanize but exact - every non-zero unit is included,
// e.g. "1 hour 12 minutes 5 seconds", with the same singular/plural handling.
// There is no trailing "ago" - the tooltip's row label already says that.
$.fn.zato.time_ago.humanize_detailed = function(age_seconds) {
    var config = $.fn.zato.time_ago.config;

    // Anything below one second reads better as a fixed label than as "0 seconds ago".
    if(age_seconds < 1) {
        return config.just_now_label;
    }

    var units = config.units;
    var remaining = Math.floor(age_seconds);
    var parts = [];

    for(var unit_idx = 0; unit_idx < units.length; unit_idx++) {
        var unit = units[unit_idx];
        var count = Math.floor(remaining / unit.seconds);
        if(count) {
            var suffix = count == 1 ? '' : 's';
            parts.push(count + ' ' + unit.name + suffix);
            remaining -= count * unit.seconds;
        }
    }

    var out = parts.join(' ');
    return out;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Turns a millisecond duration into readable text - "450 ms", "10.8 seconds"
// or "1 minute 5 seconds" for anything longer.
$.fn.zato.time_ago.humanize_duration = function(duration_ms) {
    var config = $.fn.zato.time_ago.config;

    if(duration_ms < 1000) {
        return duration_ms + ' ' + config.duration_ms_label;
    }

    var seconds = duration_ms / 1000;

    if(seconds < 60) {
        var rounded = Math.round(seconds * 10) / 10;
        var unit = rounded === 1 ? 'second' : 'seconds';
        return rounded + ' ' + unit;
    }

    var out = $.fn.zato.time_ago.humanize_detailed(Math.floor(seconds));
    return out;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.time_ago.format_timestamp = function(when, use_utc) {

    var pad_two = function(value) {
        return String(value).padStart(2, '0');
    };

    var year, month, day, hours, minutes, seconds;

    if(use_utc) {
        year    = when.getUTCFullYear();
        month   = when.getUTCMonth() + 1;
        day     = when.getUTCDate();
        hours   = when.getUTCHours();
        minutes = when.getUTCMinutes();
        seconds = when.getUTCSeconds();
    }
    else {
        year    = when.getFullYear();
        month   = when.getMonth() + 1;
        day     = when.getDate();
        hours   = when.getHours();
        minutes = when.getMinutes();
        seconds = when.getSeconds();
    }

    var date_part = year + '-' + pad_two(month) + '-' + pad_two(day);
    var time_part = pad_two(hours) + ':' + pad_two(minutes) + ':' + pad_two(seconds);

    var out = date_part + ' ' + time_part;
    return out;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.time_ago.build_tooltip_html = function(iso_utc, duration_ms) {
    var config = $.fn.zato.time_ago.config;
    var when = new Date(iso_utc);

    // The browser knows best what timezone the user is in.
    var browser_timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    var local_text = $.fn.zato.time_ago.format_timestamp(when, false);
    var utc_text = $.fn.zato.time_ago.format_timestamp(when, true);

    // The exact age, e.g. "1 hour 12 minutes 5 seconds" - the link keeps the coarse form.
    var age_seconds = Math.floor((Date.now() - when.getTime()) / 1000);
    if(age_seconds < 0) {
        age_seconds = 0;
    }
    var ago_text = $.fn.zato.time_ago.humanize_detailed(age_seconds);

    var out = '<div class="zato-time-ago-tooltip-title">' + config.tooltip_title + '</div>';
    out += '<table class="zato-time-ago-tooltip">';
    out += '<tr><th>' + config.ago_row_label + '</th><td>' + ago_text + '</td></tr>';

    // The duration is only known once at least one run has completed.
    if(duration_ms !== null) {
        var duration_text = $.fn.zato.time_ago.humanize_duration(duration_ms);
        out += '<tr><th>' + config.duration_row_label + '</th><td>' + duration_text + '</td></tr>';
    }

    out += '<tr><th>' + browser_timezone + '</th><td>' + local_text + '</td></tr>';
    out += '<tr><th>' + config.utc_label + '</th><td>' + utc_text + '</td></tr>';
    out += '</table>';

    return out;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Updates one cell in place - existing link and tippy instances are reused
// so that periodic refreshes never make the cell flicker.
$.fn.zato.time_ago.update_cell = function(cell, iso_utc, duration_ms) {
    var config = $.fn.zato.time_ago.config;

    // The duration arrives as a number, a string from a data attribute or not at all -
    // anything that is not a number means no run has completed yet.
    duration_ms = parseInt(duration_ms);
    if(isNaN(duration_ms)) {
        duration_ms = null;
    }

    cell.attr('data-time-utc', iso_utc);
    if(duration_ms === null) {
        cell.removeAttr('data-duration-ms');
    }
    else {
        cell.attr('data-duration-ms', duration_ms);
    }

    // Make sure the cell has its value element - the fade duration comes from the config
    // so that the CSS transition and the swap timer below always use the same number ..
    var value_element = cell.find('.zato-time-ago-value');
    if(!value_element.length) {
        value_element = $('<span class="zato-time-ago-value"></span>');
        value_element[0].style.setProperty('--zato-time-ago-value-fade-ms', config.value_fade_ms + 'ms');
        value_element[0].style.setProperty('--zato-time-ago-value-fade-opacity', config.value_fade_opacity);
        cell.empty();
        cell.append(value_element);
    }

    // .. work out the new text and sort value - no timestamp means the underlying item
    // .. has not run yet and such cells sort after all the others ..
    var new_text;
    var tooltip_html = '';

    if(!iso_utc) {
        cell.attr('data-sort-value', config.never_sort_value);
        new_text = config.never_label;
    }
    else {
        var when = new Date(iso_utc);
        var now = new Date();
        var age_seconds = Math.floor((now.getTime() - when.getTime()) / 1000);

        // .. the source clock and the browser may disagree by a moment - never show a negative age ..
        if(age_seconds < 0) {
            age_seconds = 0;
        }

        // .. the numeric age is what table sorting uses, which is why ascending order
        // .. puts "4 seconds ago" before "1 hour ago" regardless of the humanized text ..
        cell.attr('data-sort-value', age_seconds);

        new_text = $.fn.zato.time_ago.humanize(age_seconds);
        tooltip_html = $.fn.zato.time_ago.build_tooltip_html(iso_utc, duration_ms);
    }

    // .. this is what actually writes the new content out ..
    var apply_text = function() {

        // A cell without a timestamp shows a plain label only.
        if(!iso_utc) {
            value_element.text(new_text);
            return;
        }

        // Build the link and its tippy on the first update only. The tippy anchors
        // to the fixed-width value element rather than the link itself, so the tooltip
        // never shifts around when the link text changes width mid-refresh.
        var link = value_element.find('a');
        if(!link.length) {
            value_element.empty();
            link = $('<a href="javascript:void(0)"></a>');
            value_element.append(link);

            tippy(value_element[0], {
                allowHTML: true,
                trigger: 'click',
                placement: config.tippy_placement,
                arrow: true,
                interactive: true,

                // Keep the tooltip out of the table, otherwise the table's own th/td styles leak into it.
                appendTo: document.body,

                // Let the Escape key close the tooltip while it is shown.
                onShow: function(instance) {
                    var handle_escape = function(event) {
                        if(event.key === 'Escape') {
                            instance.hide();
                        }
                    };
                    instance.handle_escape = handle_escape;
                    document.addEventListener('keydown', handle_escape);

                    // The row's name cell wears the same badge the inline forms use,
                    // so it is clear which row the tooltip belongs to.
                    if(config.highlight_column) {
                        var row_id = cell.closest('tr').attr('id').replace('tr_', '');
                        var highlight = $.fn.zato.data_table.get_cell(row_id, config.highlight_column);
                        instance.badge_elem = $.fn.zato.inline_edit.badge_on(highlight);
                    }
                },
                onHide: function(instance) {
                    document.removeEventListener('keydown', instance.handle_escape);

                    if(instance.badge_elem) {
                        $.fn.zato.inline_edit.badge_off(instance.badge_elem);
                        instance.badge_elem = null;
                    }
                },
            });
        }

        link.text(new_text);
        value_element[0]._tippy.setContent(tooltip_html);
    };

    // .. changed values fade out gently, swap once invisible and fade back in,
    // .. while unchanged cells are updated silently so nothing pulses without a reason.
    var current_text = value_element.text();

    // A previous fade may still be pending, e.g. after a background tab was throttled -
    // in that case the update is applied directly so no cell ever gets stuck.
    if(value_element.hasClass('zato-time-ago-fading')) {
        value_element.removeClass('zato-time-ago-fading');
        apply_text();
    }
    else if(current_text && current_text !== new_text) {
        value_element.addClass('zato-time-ago-fading');
        setTimeout(function() {
            apply_text();
            value_element.removeClass('zato-time-ago-fading');
        }, config.value_fade_ms);
    }
    else {
        apply_text();
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Marks one row's time-ago cell as having run right now - instant feedback after
// a manual trigger. The next refresh pass replaces it with the server-side timestamp.
$.fn.zato.time_ago.mark_just_run = function(id) {
    var cell = $('#tr_' + id + ' td.zato-time-ago');
    $.fn.zato.time_ago.update_cell(cell, new Date().toISOString(), cell.attr('data-duration-ms'));
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.time_ago.init = function(container_selector) {

    // The column header carries one shared indicator slot for all the cells below it - the countdown
    // and the spinner live in that one slot and swap places, so the spinner shows up exactly
    // where the countdown text was, never next to it ..
    var config = $.fn.zato.time_ago.config;
    var headers = $(container_selector).find('.zato-time-ago-header');
    headers.each(function() {
        var header = $(this);

        if(!header.find('.zato-time-ago-indicator').length) {
            var indicator = $('<span class="zato-time-ago-indicator"></span>');

            if(config.countdown_enabled) {
                var countdown = $('<span class="zato-soft-hint zato-time-ago-countdown is-visible"></span>');

                // A click on the countdown pauses the auto-refresh and another click resumes it.
                // Both events stop here so the table sorter bound to the header never sees them.
                countdown.on('mousedown', function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                });
                countdown.on('click', function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                    $.fn.zato.time_ago.toggle_paused(container_selector);
                });

                indicator.append(countdown);
            }
            if(config.progress_enabled) {
                header.append($('<span class="zato-time-ago-progress is-visible"></span>'));
            }

            indicator.append($('<span class="zato-time-ago-spinner"></span>'));
            header.append(indicator);

            // The slot reserves the width of the wider of its two texts up front,
            // so flipping between the countdown and the paused label never resizes the column.
            if(config.countdown_enabled) {
                var interval_seconds = config.refresh_interval_ms / 1000;
                var countdown_text = config.countdown_prefix + interval_seconds + config.countdown_suffix;

                countdown.text(countdown_text);
                var countdown_width = countdown.outerWidth();

                countdown.text(config.paused_label);
                var paused_width = countdown.outerWidth();

                countdown.text('');
                countdown.css('min-width', Math.max(countdown_width, paused_width) + 'px');
            }
        }
    });

    // .. and each cell gets its humanized value.
    var cells = $(container_selector).find('.zato-time-ago');
    cells.each(function() {
        var cell = $(this);
        $.fn.zato.time_ago.update_cell(cell, cell.attr('data-time-utc'), cell.attr('data-duration-ms'));
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// While the spinner is visible the countdown and the progress bar are not, and the other
// way around - everything keeps occupying its space, so nothing ever shifts the layout.
$.fn.zato.time_ago.show_spinners = function(container_selector) {
    var headers = $(container_selector).find('.zato-time-ago-header');
    headers.find('.zato-time-ago-spinner').addClass('is-visible');
    headers.find('.zato-time-ago-countdown').removeClass('is-visible');
    headers.find('.zato-time-ago-progress').removeClass('is-visible');
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.time_ago.hide_spinners = function(container_selector) {
    var headers = $(container_selector).find('.zato-time-ago-header');
    headers.find('.zato-time-ago-spinner').removeClass('is-visible');
    headers.find('.zato-time-ago-countdown').addClass('is-visible');

    // The bar refills only now, once the refresh is over and the spinner is gone.
    $.fn.zato.time_ago.restart_progress(container_selector);
    headers.find('.zato-time-ago-progress').addClass('is-visible');
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.time_ago.update_countdowns = function(container_selector) {
    var config = $.fn.zato.time_ago.config;

    var text;
    if($.fn.zato.time_ago.paused) {
        text = config.paused_label;
    }
    else {
        text = config.countdown_prefix + $.fn.zato.time_ago.seconds_left + config.countdown_suffix;
    }

    $(container_selector).find('.zato-time-ago-header .zato-time-ago-countdown').text(text);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Flips between a running and a paused auto-refresh - invoked by clicking the countdown text.
$.fn.zato.time_ago.toggle_paused = function(container_selector) {
    var config = $.fn.zato.time_ago.config;
    $.fn.zato.time_ago.paused = !$.fn.zato.time_ago.paused;

    var bars = $(container_selector).find('.zato-time-ago-header .zato-time-ago-progress');

    if($.fn.zato.time_ago.paused) {
        // The bar freezes mid-drain so it is clear nothing is moving.
        bars.css('animation-play-state', 'paused');
    }
    else {
        // Resuming starts a fresh cycle rather than continuing a stale one.
        $.fn.zato.time_ago.seconds_left = config.refresh_interval_ms / 1000;
        bars.css('animation-play-state', 'running');
        $.fn.zato.time_ago.restart_progress(container_selector);
    }

    $.fn.zato.time_ago.update_countdowns(container_selector);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Refills the progress bar and lets it drain again over the full refresh interval.
$.fn.zato.time_ago.restart_progress = function(container_selector) {
    var config = $.fn.zato.time_ago.config;
    var bars = $(container_selector).find('.zato-time-ago-header .zato-time-ago-progress');

    bars.each(function() {
        var bar = this;

        // Clearing the animation and forcing a reflow makes the browser restart it from scratch.
        bar.style.animation = 'none';
        var _ = bar.offsetWidth;

        bar.style.animation = 'zato-time-ago-drain ' + config.refresh_interval_ms + 'ms linear forwards';
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Runs one refresh cycle - the IDs of the rows currently shown go out in a single request
// and the response maps each ID to its new timestamp. Cells keep their current content
// while the request is in flight, only a tiny spinner appears next to each of them.
$.fn.zato.time_ago.refresh = function(container_selector, url) {
    var config = $.fn.zato.time_ago.config;

    // Collect the IDs of the rows currently shown - each data-table row's DOM ID is tr_{id} ..
    var id_list = [];
    $(container_selector).find('td.zato-time-ago').each(function() {
        var row_id = $(this).closest('tr').attr('id');
        id_list.push(row_id.replace('tr_', ''));
    });

    // .. an empty table means there is nothing to ask about ..
    if(!id_list.length) {
        return;
    }

    var started_at = Date.now();
    $.fn.zato.time_ago.show_spinners(container_selector);

    $.ajax({
        url: url,
        type: 'POST',
        data: {'id_list': id_list.join(',')},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            if(typeof data === 'string') {
                data = JSON.parse(data);
            }

            var apply_update = function() {
                $(container_selector).find('td.zato-time-ago').each(function() {
                    var cell = $(this);
                    var row_id = cell.closest('tr').attr('id');
                    var item_id = row_id.replace('tr_', '');
                    if(item_id in data) {
                        var entry = data[item_id];
                        $.fn.zato.time_ago.update_cell(cell, entry.last_run_utc, entry.last_duration_ms);
                    }
                });
                $.fn.zato.time_ago.hide_spinners(container_selector);

                // Refreshed sort values need to reach the sorter's cache.
                $(container_selector).trigger('update');
            };

            // The spinner stays up for at least its minimum visibility time so it never just blinks.
            var elapsed = Date.now() - started_at;
            var remaining = config.spinner_min_visible_ms - elapsed;
            if(remaining > 0) {
                setTimeout(apply_update, remaining);
            }
            else {
                apply_update();
            }
        },
        error: function() {
            $.fn.zato.time_ago.hide_spinners(container_selector);
        }
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// One ticker drives both the countdown and the refresh itself so the two can never drift apart -
// the counter goes 5s, 4s, .. 1s and once it reaches zero the refresh fires and the counter starts over.
$.fn.zato.time_ago.start_auto_refresh = function(container_selector, url) {
    var config = $.fn.zato.time_ago.config;
    var interval_seconds = config.refresh_interval_ms / 1000;

    $.fn.zato.time_ago.seconds_left = interval_seconds;
    $.fn.zato.time_ago.update_countdowns(container_selector);
    $.fn.zato.time_ago.restart_progress(container_selector);

    setInterval(function() {

        // A paused ticker stands still - the countdown text already says why.
        if($.fn.zato.time_ago.paused) {
            return;
        }

        $.fn.zato.time_ago.seconds_left -= 1;

        if($.fn.zato.time_ago.seconds_left <= 0) {
            $.fn.zato.time_ago.seconds_left = interval_seconds;
            $.fn.zato.time_ago.refresh(container_selector, url);
        }

        $.fn.zato.time_ago.update_countdowns(container_selector);
    }, 1000);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Inline editing - a reusable way to change one or a few fields of a data-table row
// without opening the edit dialog. The hidden edit form is populated exactly the way
// the dialog populates it, selected fields are overridden and the form is submitted,
// so the backend sees the same request an ordinary edit would produce.

$.fn.zato.inline_edit = {};

$.fn.zato.inline_edit.config = {

    // The defaults below match the standard pattern used by most pages -
    // one edit form with the edit- field prefix. Pages that deviate from it,
    // like the scheduler, pass their own values instead.
    'form_selector': '#edit-form',
    'name_prefix': 'edit-',

    'saving_label': 'Saving ..',
    'saved_label': 'OK, saved',
    'saved_hide_ms': 1200,
    'error_label': 'Save failed',
    'details_modal_title': 'Response',

    // The saving tippy gets the same lead-in as the last-run spinner,
    // so saves that complete quickly never flash it at all.
    'saving_lead_in_ms': $.fn.zato.time_ago.config.spinner_min_visible_ms,

    'ok_label': 'OK',
    'cancel_label': 'Cancel',
    'tippy_placement': 'top',

    // The saved confirmation shows to the left of the edited link,
    // so it never covers the value that has just changed.
    'confirmation_placement': 'left',
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Replays the edit action for one row with selected fields changed. Options:
//
//   link_elem     - the link that was clicked, the spinner and the outcome show on it
//   id            - the row's ID in $.fn.zato.data_table.data
//   overrides     - field name to new value, applied after the form is populated
//   on_success    - called with the jqXHR so the page can rebuild the row,
//                   defaults to the standard $.fn.zato.data_table.on_submit_complete path
//   form_selector - the hidden edit form to replay, defaults to #edit-form
//   name_prefix   - the form's field name prefix, defaults to edit-
//
$.fn.zato.inline_edit.submit = function(opts) {

    var config = $.fn.zato.inline_edit.config;

    var form_selector = opts.form_selector;
    if(form_selector === undefined) {
        form_selector = config.form_selector;
    }

    var name_prefix = opts.name_prefix;
    if(name_prefix === undefined) {
        name_prefix = config.name_prefix;
    }

    var on_success = opts.on_success;
    if(on_success === undefined) {
        on_success = function(jqXHR) {
            $.fn.zato.data_table.on_submit_complete(jqXHR, 'success', 'edit');
        };
    }

    var form = $(form_selector);
    var id_prefix = '#id_' + name_prefix;
    var instance = $.fn.zato.data_table.data[opts.id];
    var link_elem = opts.link_elem;

    // Fill the hidden edit form exactly the way the edit dialog does, so submitting it
    // equals opening Edit and clicking OK without touching anything ..
    $.fn.zato.form.populate(form, instance, name_prefix, id_prefix);

    // .. then change only the fields this action is about ..
    for(var field_name in opts.overrides) {
        var field = form.find('[name="' + name_prefix + field_name + '"]');
        var value = opts.overrides[field_name];
        if(field.is(':checkbox')) {
            field.prop('checked', value);
        }
        else {
            field.val(value);
        }
    }

    // .. and make sure every select carries the row's actual value. A select resets
    // to its first option when populate hands it a value missing from its choices,
    // e.g. internal zato.* services are never on the service list - such values get
    // a temporary option injected so the request carries what the row really uses ..
    form.find('option.zato-inline-edit-injected').remove();
    form.find('select').each(function() {
        var select = $(this);
        var select_name = select.attr('name');

        // Only prefixed fields map back to instance attributes.
        if(select_name.indexOf(name_prefix) !== 0) {
            return;
        }

        var field_name = select_name.substring(name_prefix.length);

        // Overridden fields already carry the value this action wants.
        if(field_name in opts.overrides) {
            return;
        }

        var instance_value = instance[field_name];
        if(instance_value && select.val() !== instance_value) {
            var option = $('<option class="zato-inline-edit-injected"></option>');
            option.attr('value', instance_value);
            option.text(instance_value);
            select.append(option);
            select.val(instance_value);
        }
    });

    var remove_injected = function() {
        form.find('option.zato-inline-edit-injected').remove();
    };

    // .. and submit it, with the spinner and the outcome shown on the clicked link.
    // The form is left populated on purpose - the on_success path reads it back
    // to rebuild the row and cleans it up afterwards.
    $.fn.zato.action_runner.run({
        link_elem: link_elem,
        url: form.attr('action'),
        data: form.serialize(),
        spinner_label: config.saving_label,
        details_modal_title: config.details_modal_title,
        show_delay_ms: config.saving_lead_in_ms,

        // The edit views reply with HTTP 200 and a JSON document on success and with
        // an error page otherwise - there is no is_success field to look at.
        parse: function(jqXHR, textStatus) {
            var is_http_ok = (jqXHR.status >= 200 && jqXHR.status < 300);

            // On error the row is not rebuilt, so the injected options can go right away.
            if(!is_http_ok) {
                remove_injected();
            }

            return {
                is_success: is_http_ok,
                label: is_http_ok ? config.saved_label : config.error_label,
                details_title: config.error_label,
                details_body: jqXHR.responseText,
                jqXHR: jqXHR
            };
        },

        on_success: function(tippy_instance, result) {

            // The row rebuild replaces the clicked link, so remember which cell it sits in -
            // _bounce_row then shows its confirmation on the link that takes its place,
            // placed so that it does not cover the value that has just changed.
            var cell_index = $(link_elem).closest('td').index();
            $.fn.zato.data_table.bounce_target_finder = function(tr) {
                return tr.find('td').eq(cell_index).find('a')[0];
            };
            $.fn.zato.data_table.bounce_placement = config.confirmation_placement;

            // The saving tippy must not survive the rebuild - _bounce_row shows
            // the confirmation, there is no second tippy here.
            tippy_instance.hide();
            tippy_instance.destroy();

            on_success(result.jqXHR);

            // The rebuild has read the form back by now, the temporary options can go.
            remove_injected();
        }
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Flips the is_active flag of one row - a thin wrapper over submit. On pages following
// the standard edit-form pattern it needs no options at all.
$.fn.zato.inline_edit.toggle_active = function(id, link_elem, opts) {

    if(opts === undefined) {
        opts = {};
    }

    var instance = $.fn.zato.data_table.data[id];
    var is_active = $.fn.zato.to_bool(instance.is_active);

    $.fn.zato.inline_edit.submit({
        link_elem: link_elem,
        id: id,
        overrides: {'is_active': !is_active},
        form_selector: opts.form_selector,
        name_prefix: opts.name_prefix,
        on_success: opts.on_success
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// A small form inside a tippy shown above a link. Options:
//
//   link_elem      - the link the tippy points at
//   title          - a heading above the rows
//   rows           - a list of {name, label, value} - one table row per entry,
//                    each with a label and an input prefilled with value
//   input_type     - optional, the type of all the inputs, e.g. number, defaults to text
//   input_min      - optional, the minimum value of all the inputs, for number inputs
//   validate       - called with a map of trimmed input values, returns an error
//                    message when the form must not be submitted or an empty string
//   on_submit      - called with the map of values once they validate
//   highlight_elem - optional, an element whose text wears a badge while the form is open
//
// The Enter key anywhere in the inputs submits the form, Escape closes it.
// Wraps an element's contents in the highlight badge - the honey background that marks
// which row an open form or tooltip belongs to. Returns the element for later cleanup.
$.fn.zato.inline_edit.badge_on = function(elem) {
    var highlight = $(elem);
    highlight.wrapInner('<span class="zato-inline-form-badge"></span>');
    return highlight;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.inline_edit.badge_off = function(elem) {
    var badge = $(elem).find('.zato-inline-form-badge');
    badge.contents().unwrap();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.inline_edit.form_tippy = function(opts) {

    var config = $.fn.zato.inline_edit.config;
    var link_elem = opts.link_elem;

    // Each click starts from scratch - any previous tippy on this link goes away first.
    if(link_elem._tippy) {
        link_elem._tippy.hide();
        link_elem._tippy.destroy();
    }

    // Build the form ..
    var container = $('<div class="zato-inline-form"></div>');

    if(opts.title) {
        container.append($('<div class="zato-inline-form-title"></div>').text(opts.title));
    }

    var input_type = opts.input_type;
    if(input_type === undefined) {
        input_type = 'text';
    }

    var table = $('<table></table>');
    $.each(opts.rows, function(ignored, row) {
        var tr = $('<tr></tr>');
        tr.append($('<th></th>').text(row.label));

        var input = $('<input />');
        input.attr('type', input_type);
        if(opts.input_min !== undefined) {
            input.attr('min', opts.input_min);
        }

        // Text fields like names need more room than the default numeric width.
        if(opts.input_width !== undefined) {
            input.css('width', opts.input_width);
        }

        input.attr('name', row.name);
        input.val(row.value);
        tr.append($('<td></td>').append(input));

        table.append(tr);
    });
    container.append(table);

    // .. with its OK and Cancel buttons ..
    var buttons = $('<div class="zato-inline-form-buttons"></div>');
    var ok_button = $('<button type="button"></button>').text(config.ok_label);
    var cancel_button = $('<button type="button"></button>').text(config.cancel_label);
    buttons.append(ok_button);
    buttons.append(cancel_button);
    container.append(buttons);

    // .. shown in an interactive tippy above the link ..
    var instance = tippy(link_elem, {
        content: container[0],
        allowHTML: true,
        placement: config.tippy_placement,
        trigger: 'manual',
        arrow: true,
        animation: 'fade',
        duration: [50, 50],
        hideOnClick: false,
        interactive: true,

        // Keep the form out of the table, otherwise the table's own th/td styles leak into it.
        appendTo: document.body,
        zIndex: 100001,

        // Let the Escape key and clicks outside the form close it while it is shown.
        onShow: function(tippy_instance) {
            var handle_escape = function(event) {
                if(event.key === 'Escape') {
                    tippy_instance.hide();
                }
            };
            tippy_instance.handle_escape = handle_escape;
            document.addEventListener('keydown', handle_escape);

            var handle_outside_mousedown = function(event) {
                var is_in_popper = tippy_instance.popper.contains(event.target);
                var is_on_link = link_elem.contains(event.target);
                if(!is_in_popper && !is_on_link) {
                    tippy_instance.hide();
                }
            };
            tippy_instance.handle_outside_mousedown = handle_outside_mousedown;
            document.addEventListener('mousedown', handle_outside_mousedown);

            // While the form is open, the related element wears a badge
            // so it is clear which row the form belongs to.
            if(opts.highlight_elem) {
                tippy_instance.badge_elem = $.fn.zato.inline_edit.badge_on(opts.highlight_elem);
            }
        },
        onHide: function(tippy_instance) {
            document.removeEventListener('keydown', tippy_instance.handle_escape);
            document.removeEventListener('mousedown', tippy_instance.handle_outside_mousedown);

            if(tippy_instance.badge_elem) {
                $.fn.zato.inline_edit.badge_off(tippy_instance.badge_elem);
                tippy_instance.badge_elem = null;
            }
        },
    });

    cancel_button.on('click', function() {
        instance.hide();
    });

    // Enter anywhere in the inputs submits the form.
    table.find('input').on('keydown', function(event) {
        if(event.key === 'Enter') {
            event.preventDefault();
            ok_button.trigger('click');
        }
    });

    // .. OK collects the inputs and refuses to go on until they validate.
    ok_button.on('click', function() {

        var inputs = table.find('input');
        var values = {};

        inputs.each(function() {
            var input = $(this);
            values[input.attr('name')] = input.val().trim();
        });

        var error = opts.validate(values);
        if(error) {
            inputs.each(function() {
                $.fn.zato.draw_attention_to($(this));
            });
            $.fn.zato.show_native_tooltip(inputs.first(), error);
            return;
        }

        inputs.each(function() {
            $.fn.zato.cleanup_elem_css_attention($(this));
        });

        instance.hide();
        opts.on_submit(values);
    });

    instance.show();

    // Typing starts in the first field that already has a value - only when all
    // of them are empty does the focus land on the first one.
    var all_inputs = table.find('input');
    var focus_target = all_inputs.filter(function() {
        return $(this).val() !== '';
    }).first();

    if(!focus_target.length) {
        focus_target = all_inputs.first();
    }

    focus_target.trigger('focus');
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.empty_value = '<span class="form_hint">---</span>';
$.fn.zato.empty_table_cell = String.format('<td>{0}</td>', $.fn.zato.empty_value);

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.service.export_config = function() {
    var cluster_id = $(document).getUrlParam('cluster') || '1';
    var export_url = '/zato/service/enmasse-export?cluster=' + cluster_id;

    var spinner_html = '<div id="export-spinner" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border: 2px solid #ccc; border-radius: 5px; z-index: 9999;"><div style="display: inline-block; width: 16px; height: 16px; border: 2px solid #ccc; border-top: 2px solid #333; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; vertical-align: middle;"></div>Exporting ...</div><style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>';
    $('body').append(spinner_html);

    $.ajax({
        url: export_url,
        method: 'GET',
        success: function(data) {
            $('#export-spinner').remove();

            var blob = new Blob([data], { type: 'application/x-yaml' });
            var url = window.URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = 'enmasse.yaml';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        },
        error: function() {
            $('#export-spinner').remove();
            alert('Export failed. Check server logs.');
        }
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.service.import_config = function() {
    var cluster_id = $(document).getUrlParam('cluster') || '1';

    var input = document.createElement('input');
    input.type = 'file';
    input.accept = '*';

    input.onchange = function(e) {
        var file = e.target.files[0];
        if (!file) {
            return;
        }

        var reader = new FileReader();
        reader.onload = function(event) {
            var fileContent = event.target.result;

            var spinner_html = '<div id="import-spinner" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border: 2px solid #ccc; border-radius: 5px; z-index: 9999;"><div style="display: inline-block; width: 16px; height: 16px; border: 2px solid #ccc; border-top: 2px solid #333; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; vertical-align: middle;"></div>Importing config ...</div><style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>';
            $('body').append(spinner_html);

            $.ajax({
                url: '/zato/service/enmasse-import?cluster=' + cluster_id,
                method: 'POST',
                data: {
                    file_content: fileContent,
                    file_name: file.name
                },
                headers: {'X-CSRFToken': $.cookie('csrftoken')},
                success: function(data) {
                    $('#import-spinner').remove();

                    var result;
                    if (typeof data === 'object') {
                        result = data;
                    } else {
                        try {
                            result = JSON.parse(data);
                        } catch (e) {
                            result = {
                                is_ok: false,
                                exit_code: -1,
                                stdout: '',
                                stderr: String(data),
                                is_timeout: false,
                                timeout_msg: '',
                                total_time: '',
                                len_stdout_human: '',
                                len_stderr_human: ''
                            };
                        }
                    }

                    if (result.is_ok) {
                        $.fn.zato.show_import_result_popup(result, true, file);
                    } else {
                        $.fn.zato.show_import_result_popup(result, false, file);
                    }
                },
                error: function(xhr, status, error) {
                    $('#import-spinner').remove();
                    $.fn.zato.show_import_result_popup({
                        is_ok: false,
                        exit_code: -1,
                        stdout: '',
                        stderr: xhr.responseText || error,
                        is_timeout: false,
                        timeout_msg: '',
                        total_time: '',
                        len_stdout_human: '',
                        len_stderr_human: ''
                    }, false, file);
                }
            });
        };
        reader.readAsText(file);
    };

    input.click();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.show_import_result_popup = function(result, is_success, file) {
    var overlay = $('<div/>', {
        id: 'import-result-overlay',
        css: {
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            zIndex: 10000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
        }
    });

    var popup = $('<div/>', {
        css: {
            backgroundColor: '#1e1e1e',
            color: '#d4d4d4',
            borderRadius: '8px',
            padding: '0',
            maxWidth: '800px',
            width: '90%',
            maxHeight: '80vh',
            overflow: 'hidden',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
            fontFamily: 'monospace'
        }
    });

    var header = $('<div/>', {
        css: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '16px 24px',
            borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
            background: '#1f1f1f'
        }
    });

    var title = $('<h2/>', {
        text: 'Import result',
        css: {
            margin: '0',
            fontSize: '18px',
            fontWeight: '600',
            color: '#ffffff',
            letterSpacing: '0.3px'
        }
    });

    var closeButton = $('<button/>', {
        text: '\u2715',
        css: {
            background: 'transparent',
            border: 'none',
            color: '#999',
            fontSize: '24px',
            cursor: 'pointer',
            padding: '0',
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '6px',
            transition: 'all 0.2s ease'
        }
    });

    closeButton.hover(
        function() { $(this).css({background: 'rgba(255, 255, 255, 0.1)', color: '#fff'}); },
        function() { $(this).css({background: 'transparent', color: '#999'}); }
    );

    closeButton.click(function() {
        overlay.remove();
        $(document).off('keydown.import-overlay');
        if (is_success) {
            var currentPath = window.location.pathname;
            if (currentPath !== '/zato/' && currentPath.indexOf('service/ide') === -1) {
                window.location.reload();
            }
        }
    });

    header.append(title);
    header.append(closeButton);
    popup.append(header);

    var contentArea = $('<div/>', {
        css: {
            padding: '24px',
            maxHeight: 'calc(80vh - 60px)',
            overflow: 'auto'
        }
    });

    if (result.stderr && String(result.stderr).trim() && !result.is_ok) {
        var stderrArea = $('<textarea/>', {
            val: String(result.stderr),
            readonly: true,
            css: {
                width: '100%',
                minHeight: '150px',
                backgroundColor: '#2d2d2d',
                color: '#f48771',
                border: '1px solid #3e3e3e',
                borderRadius: '4px',
                padding: '8px',
                fontFamily: 'monospace',
                fontSize: '12px',
                resize: 'vertical'
            }
        });
        contentArea.append(stderrArea);

        var fileSize = file ? file.size : 0;
        var fileSizeHuman = fileSize < 1024 ? fileSize + ' B' :
                            fileSize < 1048576 ? (fileSize / 1024).toFixed(1) + ' KB' :
                            (fileSize / 1048576).toFixed(1) + ' MB';
        var fileName = file ? file.name : 'unknown';
        var mimeType = file ? (file.type || 'unknown') : 'unknown';

        var errorMsg = $('<div/>', {
            text: 'File ' + fileName + ' (' + fileSizeHuman + '; ' + mimeType + ') could not be imported',
            css: {
                marginTop: '12px',
                color: '#f48771',
                fontSize: '16px',
                fontWeight: 'bold'
            }
        });
        contentArea.append(errorMsg);
    } else if (result.stdout && String(result.stdout).trim()) {
        var stdoutArea = $('<textarea/>', {
            val: String(result.stdout),
            readonly: true,
            css: {
                width: '100%',
                minHeight: '150px',
                backgroundColor: '#2d2d2d',
                color: '#d4d4d4',
                border: '1px solid #3e3e3e',
                borderRadius: '4px',
                padding: '8px',
                fontFamily: 'monospace',
                fontSize: '12px',
                resize: 'vertical'
            }
        });
        contentArea.append(stdoutArea);

        if (String(result.stdout).indexOf('⭐ Enmasse OK') !== -1) {
            var successMsg = $('<div/>', {
                text: '⭐ Config imported OK',
                css: {
                    marginTop: '24px',
                    color: '#4ec9b0',
                    fontSize: '16px',
                    fontWeight: 'bold'
                }
            });
            contentArea.append(successMsg);
        }
    }

    popup.append(contentArea);
    overlay.append(popup);
    $('body').append(overlay);

    overlay.click(function(e) {
        if (e.target === overlay[0]) {
            overlay.remove();
            $(document).off('keydown.import-overlay');
        }
    });

    $(document).on('keydown.import-overlay', function(e) {
        if (e.key === 'Escape' || e.keyCode === 27) {
            overlay.remove();
            $(document).off('keydown.import-overlay');
            if (is_success) {
                var currentPath = window.location.pathname;
                if (currentPath !== '/zato/' && currentPath.indexOf('service/ide') === -1) {
                    window.location.reload();
                }
            }
        }
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.system.show_version = function() {
    var version = $('meta[name="generator"]').attr('content') || 'Unknown';

    var overlay = $('<div/>', {
        id: 'version-overlay',
        css: {
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            zIndex: 10000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
        }
    });

    var popup = $('<div/>', {
        css: {
            backgroundColor: '#1e1e1e',
            color: '#d4d4d4',
            borderRadius: '8px',
            padding: '0',
            maxWidth: '800px',
            width: '90%',
            maxHeight: '80vh',
            overflow: 'hidden',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
            fontFamily: 'monospace'
        }
    });

    var header = $('<div/>', {
        css: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '16px 24px',
            borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
            background: '#1f1f1f'
        }
    });

    var title = $('<h2/>', {
        text: 'Version',
        css: {
            margin: '0',
            fontSize: '18px',
            fontWeight: '600',
            color: '#ffffff',
            letterSpacing: '0.3px'
        }
    });

    var closeButton = $('<button/>', {
        text: '\u2715',
        css: {
            background: 'transparent',
            border: 'none',
            color: '#999',
            fontSize: '24px',
            cursor: 'pointer',
            padding: '0',
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '6px',
            transition: 'all 0.2s ease'
        }
    });

    closeButton.hover(
        function() { $(this).css({background: 'rgba(255, 255, 255, 0.1)', color: '#fff'}); },
        function() { $(this).css({background: 'transparent', color: '#999'}); }
    );

    closeButton.click(function() {
        overlay.remove();
        $(document).off('keydown.version-overlay');
    });

    header.append(title);
    header.append(closeButton);
    popup.append(header);

    var contentArea = $('<div/>', {
        css: {
            padding: '24px'
        }
    });

    var versionText = $('<div/>', {
        text: version,
        css: {
            fontSize: '18px',
            fontWeight: 'bold',
            color: '#4ec9b0'
        }
    });

    contentArea.append(versionText);
    popup.append(contentArea);
    overlay.append(popup);
    $('body').append(overlay);

    overlay.click(function(e) {
        if (e.target === overlay[0]) {
            overlay.remove();
            $(document).off('keydown.version-overlay');
        }
    });

    $(document).on('keydown.version-overlay', function(e) {
        if (e.key === 'Escape' || e.keyCode === 27) {
            overlay.remove();
            $(document).off('keydown.version-overlay');
        }
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.pubsub.download_openapi = function() {
    var cluster_id = $(document).getUrlParam('cluster') || '1';
    var download_url = '/zato/pubsub/download-openapi?cluster=' + cluster_id;

    var spinner_html = '<div id="download-spinner" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border: 2px solid #ccc; border-radius: 5px; z-index: 9999;"><div style="display: inline-block; width: 16px; height: 16px; border: 2px solid #ccc; border-top: 2px solid #333; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; vertical-align: middle;"></div>Downloading ...</div><style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>';
    $('body').append(spinner_html);

    $.ajax({
        url: download_url,
        method: 'GET',
        success: function(data) {
            $('#download-spinner').remove();

            var blob = new Blob([data], { type: 'application/x-yaml' });
            var url = window.URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = 'openapi.yaml';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        },
        error: function() {
            $('#download-spinner').remove();
            alert('Download failed. Check server logs.');
        }
    });
}

$.fn.zato.pubsub.import_demo_config = function() {
    var import_url = '/zato/pubsub/import-demo-config';

    var spinner_html = '<div id="import-spinner" class="zato-spinner-overlay">' +
        '<span class="zato-spinner-overlay-icon"></span>Importing ...</div>';
    $('body').append(spinner_html);

    $.ajax({
        url: import_url,
        method: 'GET',
        success: function() {
            $('#import-spinner').remove();
            window.location.reload();
        },
        error: function() {
            $('#import-spinner').remove();
            jAlert('Import failed. Check server logs.', 'Error');
        }
    });
};

// A registry of every field that has live uniqueness validation attached, keyed by field id.
// It lets the submit handler re-check each such field synchronously when OK is clicked.
$.fn.zato.data_table._unique_checks = {};

// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Builds the POST payload for a uniqueness check of a single field.
$.fn.zato.build_unique_check_data = function(entity_type, attr_name, value, filter) {

    // The base payload always carries the entity, attribute and value being checked ..
    var data = {
        'entity_type': entity_type,
        'attr_name': attr_name,
        'value': value
    };

    // .. when the filter is a function, call it at check time so the payload carries
    // .. the current values of related form fields ..
    if(typeof filter === 'function') {
        $.extend(data, filter());
    }

    // .. and, when a scoping filter object is supplied, narrow the check down to that sub-group
    // .. (e.g. a username is unique per sec_type rather than globally).
    else if(filter) {
        data['filter_name'] = filter.filter_name;
        data['filter_value'] = filter.filter_value;
    }

    return data;
}

// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Renders the taken/available indicator next to a field, positioned right after its current text.
$.fn.zato.render_unique_indicator = function(field, value, exists) {

    field.siblings('.zato-unique-indicator').remove();

    var wrapper = field.parent();
    if(!wrapper.hasClass('zato-unique-wrapper')) {
        wrapper.css('position', 'relative');
        wrapper.addClass('zato-unique-wrapper');
    }

    var html;
    if(exists) {
        html = '<span class="zato-unique-indicator zato-unique-taken">Already taken</span>';
    }
    else {
        html = '<span class="zato-unique-indicator zato-unique-ok">&#10003;</span>';
    }
    field.after(html);

    var indicator = field.next('.zato-unique-indicator');
    var measure_span = $('<span>').css({
        'font': field.css('font'),
        'font-size': field.css('font-size'),
        'font-family': field.css('font-family'),
        'letter-spacing': field.css('letter-spacing'),
        'visibility': 'hidden',
        'position': 'absolute',
        'white-space': 'pre'
    }).text(value).appendTo('body');
    var text_width = measure_span.width();
    measure_span.remove();
    var field_left = field.position().left;
    var input_padding_left = parseInt(field.css('padding-left'), 10) || 2;
    indicator.css('left', (field_left + input_padding_left + text_width + 7) + 'px');
}

// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Returns the value of a field that should be checked, or an empty string when the check should be
// skipped (empty value, or an edit form whose value has not changed from the original).
$.fn.zato.get_unique_check_value = function(field, is_edit) {

    var value = field.val().trim();
    if(!value) {
        return '';
    }

    if(is_edit) {
        var original = field.data('zato-original-value');
        if(original !== undefined && value === original) {
            return '';
        }
    }

    return value;
}

// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Attaches live uniqueness validation to a field. The optional on_result
// callback is invoked with the outcome of each completed check.
$.fn.zato.validate_unique = function(field_id, entity_type, attr_name, filter, on_result) {
    var field = $(field_id);
    if(!field.length) {
        return;
    }

    var timer = null;
    var is_edit = field_id.indexOf('edit-') !== -1;

    // Remember this field so the submit handler can re-check it synchronously on OK.
    $.fn.zato.data_table._unique_checks[field_id] = {
        'entity_type': entity_type,
        'attr_name': attr_name,
        'filter': filter,
        'is_edit': is_edit
    };

    field.on('input', function() {
        field.siblings('.zato-unique-indicator').css('opacity', '0');
        setTimeout(function() { field.siblings('.zato-unique-indicator').remove(); }, 200);

        if(timer) {
            clearTimeout(timer);
        }

        var value = $.fn.zato.get_unique_check_value(field, is_edit);
        if(!value) {
            return;
        }

        timer = setTimeout(function() {

            var data = $.fn.zato.build_unique_check_data(entity_type, attr_name, value, filter);

            $.ajax({
                type: 'POST',
                url: '/zato/check-attr-exists/',
                data: data,
                headers: {'X-CSRFToken': $.cookie('csrftoken')},
                dataType: 'json',
                success: function(data) {
                    var current = field.val().trim();
                    if(current !== value) {
                        return;
                    }
                    $.fn.zato.render_unique_indicator(field, value, data.exists);
                    if(on_result) {
                        on_result(data.exists);
                    }
                },
                error: function(xhr, status, err) {
                    console.log('[validate_unique] Error: status=' + JSON.stringify(status) + ', err=' + JSON.stringify(err));
                }
            });
        }, 300);
    });
}

// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Re-checks every uniqueness-validated field that belongs to the given form, synchronously,
// so that clicking OK cannot submit a value that is already taken. Returns true when the form
// may be submitted and false when at least one field is taken.
$.fn.zato.validate_unique_on_submit = function(form) {

    var is_valid = true;
    var first_taken = null;

    for(var field_id in $.fn.zato.data_table._unique_checks) {

        var field = $(field_id);
        if(!field.length) {
            continue;
        }
        if(!$.contains(form.get(0), field.get(0))) {
            continue;
        }

        var check = $.fn.zato.data_table._unique_checks[field_id];

        var value = $.fn.zato.get_unique_check_value(field, check.is_edit);
        if(!value) {
            continue;
        }

        var data = $.fn.zato.build_unique_check_data(check.entity_type, check.attr_name, value, check.filter);

        var exists = false;
        $.ajax({
            type: 'POST',
            url: '/zato/check-attr-exists/',
            data: data,
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            dataType: 'json',
            async: false,
            success: function(response) {
                exists = response.exists;
            }
        });

        if(exists) {
            $.fn.zato.render_unique_indicator(field, value, true);
            $.fn.zato.blink_elem(field);
            $.fn.zato.add_css_attention(field);
            if(!first_taken) {
                first_taken = field;
            }
            is_valid = false;
        }
    }

    if(first_taken) {
        first_taken.focus();
    }

    return is_valid;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* Live Form Updates - Reusable polling mechanism for applying live data changes to open create/edit forms.                      */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

;(function() {

    // Configuration for the polling loop
    $.fn.zato.live_form_updates.config = {
        poll_interval_ms: 1000,
        url: '/zato/live-form-updates/'
    };

    // Per-action (create/edit) registry of what object types each page cares about
    var _registry = {};

    // Active polling loops, keyed by action
    var _connections = {};

    // Stop all polling loops before page unload
    $(window).on('beforeunload', function() {
        var actions = Object.keys(_connections);
        for(var actionIdx = 0; actionIdx < actions.length; actionIdx++) {
            $.fn.zato.live_form_updates.stop(actions[actionIdx]);
        }
    });

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates.register = function(action, configs) {
        if(!_registry[action]) {
            _registry[action] = [];
        }
        for(var i = 0; i < configs.length; i++) {
            _registry[action].push(configs[i]);
        }
        console.log('[live_form_updates] register: action=' + action + ', total configs=' + _registry[action].length + ', object_types=' + JSON.stringify(configs.map(function(c) { return c.object_type; })));
    };

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates.has_config = function(action) {
        return _registry[action] && _registry[action].length > 0;
    };

    $.fn.zato.live_form_updates._get_configs = function(action) {
        return _registry[action] || [];
    };

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates._snapshot_select = function(selector) {
        var items = {};
        $(selector).find('option').each(function() {
            var $opt = $(this);
            var val = $opt.val();
            if(val && val !== 'ZATO_NONE') {
                items[val] = {'name': $opt.text()};
            }
        });
        return items;
    };

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates._snapshot_badge_picker = function(action) {
        var items = {};
        $('#badge-zone-available-' + action + ' .security-badge, #badge-zone-assigned-' + action + ' .security-badge').each(function() {
            var $badge = $(this);
            var id = $badge.attr('data-id');
            if(id) {
                items[id] = {
                    'name': $badge.find('.security-badge-name').text().trim()
                };
            }
        });
        return items;
    };

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates._snapshot_multi_checkbox = function(container_selector) {
        var items = {};
        $(container_selector).find('input[type="checkbox"]').each(function() {
            var $cb = $(this);

            // The data-id attribute carries the server-side object id, which is what the server
            // keys its own list by - the DOM element id is only a page-local artifact.
            var id = $cb.attr('data-id');
            var name_cell = $cb.closest('tr').find('a');
            var label = name_cell.length ? name_cell.text() : '';
            if(id) {
                items[id] = {'name': label};
            }
        });
        return items;
    };

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates._build_request = function(action) {
        var configs = _registry[action] || [];
        var object_types = {};

        for(var i = 0; i < configs.length; i++) {
            var config = configs[i];
            var items = {};

            if(config.handler === 'badge_picker') {
                items = $.fn.zato.live_form_updates._snapshot_badge_picker(action);
            }
            else if(config.handler === 'multi_checkbox') {
                items = $.fn.zato.live_form_updates._snapshot_multi_checkbox(config.container || '');
            }
            else if(config.handler === 'callback') {
                items = config.snapshot_func();
            }
            else {
                var selector = config.target_select || '';
                if(action === 'edit' && selector && selector.indexOf('edit') === -1) {
                    selector = selector.replace('#id_', '#id_edit-');
                }
                items = $.fn.zato.live_form_updates._snapshot_select(selector);
            }

            object_types[config.object_type] = {
                'items': items
            };
        }

        return {'object_types': object_types};
    };

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates.start = function(action) {

        console.log('[live_form_updates] start: called for action=' + action);

        // Do nothing if no configs registered for this action
        if(!$.fn.zato.live_form_updates.has_config(action)) {
            console.log('[live_form_updates] start: no config registered for action=' + action + ', skipping');
            return;
        }

        // Stop any existing polling loop for this action ..
        $.fn.zato.live_form_updates.stop(action);

        // .. register the new loop ..
        var connection = {
            is_active: true,
            is_first_response: true,
            timer_id: null
        };
        _connections[action] = connection;

        // .. and run the first poll right away.
        $.fn.zato.live_form_updates._poll(action, connection);
    };

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates._poll = function(action, connection) {

        // The loop may have been stopped while a previous poll was in flight
        if(!connection.is_active) {
            return;
        }

        // Snapshot what the page displays right now - the DOM itself is the client-side state,
        // so each poll compares the server against what the user actually sees.
        var request_data = $.fn.zato.live_form_updates._build_request(action);
        var snapshot_json = JSON.stringify(request_data);

        $.ajax({
            type: 'POST',
            url: $.fn.zato.live_form_updates.config.url,
            data: snapshot_json,
            contentType: 'application/json',
            dataType: 'json',
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(diffs) {

                // Ignore a response that arrives after the loop was stopped
                if(!connection.is_active) {
                    return;
                }

                var skip_puff = connection.is_first_response;
                connection.is_first_response = false;

                if(Object.keys(diffs).length) {
                    console.log('[live_form_updates] poll: action=' + action + ', diff types=' + JSON.stringify(Object.keys(diffs)));
                    $.fn.zato.live_form_updates._apply_diffs(action, diffs, skip_puff);
                }
            },
            error: function(jqXHR, text_status) {
                console.log('[live_form_updates] poll error: action=' + action + ', status=' + text_status);
            },
            complete: function() {

                // Schedule the next poll only once this one has fully completed,
                // so polls never overlap even when the server is slow.
                if(connection.is_active) {
                    connection.timer_id = setTimeout(function() {
                        $.fn.zato.live_form_updates._poll(action, connection);
                    }, $.fn.zato.live_form_updates.config.poll_interval_ms);
                }
            }
        });
    };

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates.stop = function(action) {
        var connection = _connections[action];
        if(connection) {
            console.log('[live_form_updates] stop: stopping polling loop for action=' + action);
            connection.is_active = false;
            if(connection.timer_id) {
                clearTimeout(connection.timer_id);
            }
            delete _connections[action];
        } else {
            console.log('[live_form_updates] stop: no polling loop to stop for action=' + action);
        }
    };

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates._apply_diffs = function(action, diffs, skip_puff) {
        var configs = _registry[action] || [];
        console.log('[live_form_updates] _apply_diffs: action=' + action + ', skip_puff=' + !!skip_puff + ', object_types in diff=' + JSON.stringify(Object.keys(diffs)));

        for(var object_type in diffs) {
            if(!diffs.hasOwnProperty(object_type)) continue;

            var diff = diffs[object_type];
            console.log('[live_form_updates] _apply_diffs: object_type=' + object_type + ', created=' + (diff.created ? diff.created.length : 0) + ', deleted=' + (diff.deleted ? diff.deleted.length : 0) + ', renamed=' + (diff.renamed ? diff.renamed.length : 0));

            var config = null;
            for(var i = 0; i < configs.length; i++) {
                if(configs[i].object_type === object_type) {
                    config = configs[i];
                    break;
                }
            }
            if(!config) {
                console.log('[live_form_updates] _apply_diffs: no config found for object_type=' + object_type);
                continue;
            }

            console.log('[live_form_updates] _apply_diffs: applying diff for object_type=' + object_type + ', handler=' + (config.handler || 'select'));

            if(config.handler === 'badge_picker') {
                $.fn.zato.live_form_updates._apply_badge_picker_diff(action, config, diff, skip_puff);
            }
            else if(config.handler === 'multi_checkbox') {
                $.fn.zato.live_form_updates._apply_multi_checkbox_diff(action, config, diff, skip_puff);
            }
            else if(config.handler === 'callback') {

                // Pages that keep their list in JS state rather than in the DOM
                // apply the diff themselves through the callback they registered
                config.on_diff(diff, skip_puff);
            }
            else {
                $.fn.zato.live_form_updates._apply_select_diff(action, config, diff, skip_puff);
            }
        }
    };

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates._puff = function($elem) {
        $elem.addClass('zato-live-updated');
        setTimeout(function() {
            $elem.removeClass('zato-live-updated');
        }, 1600);
    };

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates._apply_select_diff = function(action, config, diff, skip_puff) {
        var selector = config.target_select || '';
        if(action === 'edit' && selector && selector.indexOf('edit') === -1) {
            selector = selector.replace('#id_', '#id_edit-');
        }

        var $select = $(selector);
        if(!$select.length) return;

        var changed = false;

        // Handle deletions
        if(diff.deleted && diff.deleted.length) {
            for(var i = 0; i < diff.deleted.length; i++) {
                var del_id = diff.deleted[i];
                $select.find('option[value="' + del_id + '"]').remove();
            }
            changed = true;
        }

        // Handle renames. The server formats _label exactly the way the page displays items,
        // so applying it verbatim keeps the snapshot and the server list convergent.
        if(diff.renamed && diff.renamed.length) {
            for(var i = 0; i < diff.renamed.length; i++) {
                var rename = diff.renamed[i];
                var $opt = $select.find('option[value="' + rename._id + '"]');
                if($opt.length) {
                    $opt.text(rename.item._label);
                    if(!skip_puff) {
                        $.fn.zato.live_form_updates._puff($opt);
                    }
                }
            }
            changed = true;
        }

        // Handle creations
        if(diff.created && diff.created.length) {
            for(var i = 0; i < diff.created.length; i++) {
                var item = diff.created[i];

                // The page may have populated this option itself while the poll was in flight,
                // e.g. selects filled via their own AJAX call right after a dialog opens.
                var $existing = $select.find('option[value="' + item._id + '"]');
                if($existing.length) {
                    continue;
                }

                var $new_opt = $('<option/>').val(item._id).text(item._label);
                $select.append($new_opt);
                if(!skip_puff) {
                    $.fn.zato.live_form_updates._puff($new_opt);
                }
            }
            changed = true;
        }

        // Refresh Chosen if applicable
        if(changed) {
            $select.trigger('chosen:updated');
            if(!skip_puff) {
                $.fn.zato.live_form_updates._puff($select.closest('td'));
            }
        }
    };

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates._apply_badge_picker_diff = function(action, config, diff, skip_puff) {

        console.log('[live_form_updates] _apply_badge_picker_diff: action=' + action + ', skip_puff=' + !!skip_puff + ', created=' + JSON.stringify(diff.created) + ', deleted=' + JSON.stringify(diff.deleted) + ', renamed=' + JSON.stringify(diff.renamed));

        // For badge picker, if there's a callback, call it with the full diff.
        if(config.callback) {
            config.callback(action, diff);
            return;
        }

        // Default badge picker diff handling
        var available_body = $('#badge-zone-available-' + action + ' .badge-zone-body');

        // Handle deletions - remove badges from both zones
        if(diff.deleted && diff.deleted.length) {
            for(var i = 0; i < diff.deleted.length; i++) {
                var del_id = diff.deleted[i];
                available_body.find('.security-badge[data-id="' + del_id + '"]').remove();
                $('#badge-zone-assigned-' + action + ' .badge-zone-body')
                    .find('.security-badge[data-id="' + del_id + '"]').remove();
            }
            if(typeof $.fn.zato.groups !== 'undefined' &&
               typeof $.fn.zato.groups.badge_picker !== 'undefined') {
                $.fn.zato.groups.badge_picker.renumber(action);
                $.fn.zato.groups.badge_picker.update_counts(action);
            }
        }

        // Handle renames
        if(diff.renamed && diff.renamed.length) {
            for(var i = 0; i < diff.renamed.length; i++) {
                var rename = diff.renamed[i];
                var $badge = available_body.find('.security-badge[data-id="' + rename._id + '"]');
                if(!$badge.length) {
                    $badge = $('#badge-zone-assigned-' + action + ' .badge-zone-body')
                        .find('.security-badge[data-id="' + rename._id + '"]');
                }
                if($badge.length) {
                    $badge.find('.security-badge-name').text(rename.item._label);
                    if(!skip_puff) {
                        $.fn.zato.live_form_updates._puff($badge);
                    }
                }
            }
        }

        // Handle creations - add new badges to the available zone
        if(diff.created && diff.created.length) {
            for(var i = 0; i < diff.created.length; i++) {
                var item = diff.created[i];
                if(typeof $.fn.zato.groups !== 'undefined' &&
                   typeof $.fn.zato.groups.badge_picker !== 'undefined' &&
                   typeof $.fn.zato.groups.badge_picker._make_badge === 'function') {
                    var $new_badge = $.fn.zato.groups.badge_picker._make_badge(item, 0);
                    available_body.append($new_badge);
                    if(!skip_puff) {
                        $.fn.zato.live_form_updates._puff($new_badge);
                    }
                }
            }

            // Renumber and update counts after adding
            if(typeof $.fn.zato.groups !== 'undefined' &&
               typeof $.fn.zato.groups.badge_picker !== 'undefined' &&
               typeof $.fn.zato.groups.badge_picker.renumber === 'function') {
                $.fn.zato.groups.badge_picker.renumber(action);
                $.fn.zato.groups.badge_picker.update_counts(action);
            }
        }
    };

    // ------------------------------------------------------------------------------------------------------------------------

    $.fn.zato.live_form_updates._apply_multi_checkbox_diff = function(action, config, diff, skip_puff) {

        // Re-render only when the diff differs from what the previous poll reported. Some pages
        // deliberately display a subset of the server's list (e.g. topics matching a security
        // definition's patterns), so their diff is never empty - but as long as it stays the same,
        // nothing changed on the server and there is nothing to reload.
        var diff_json = JSON.stringify(diff);
        if(diff_json === config._last_diff_json) {
            return;
        }
        config._last_diff_json = diff_json;

        config.reload_callback();
    };

    // ------------------------------------------------------------------------------------------------------------------------

})();

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Fallback Esc handling for jQuery UI dialogs. jQuery UI binds its closeOnEscape
// handler on the .ui-dialog wrapper, so it only fires while focus is inside the
// dialog. When focus has dropped to body - e.g. a tab click hid the panel that
// held the focused input - the keydown never reaches the wrapper and the dialog
// stays open. This handler closes the topmost dialog in that case. It is bound
// on window, not document, so every document-level Escape consumer (e.g. the
// topic-matches popup in pubsub/permission.js) runs first - once such a consumer
// has closed its own dialog, it is no longer visible and is not closed twice.
$(window).on('keydown.zato-dialog-esc', function(e) {

    if(e.key !== 'Escape') {
        return;
    }

    // Already handled, either by the dialog itself (focus was inside it)
    // or by another Escape consumer such as an overlay.
    if(e.isDefaultPrevented()) {
        return;
    }

    // Find the topmost visible dialog by z-index ..
    var topmost = null;
    var topmost_z = -1;
    $('.ui-dialog:visible').each(function() {
        var z = parseInt($(this).css('z-index'), 10);
        if(isNaN(z)) {
            z = 0;
        }
        if(z > topmost_z) {
            topmost_z = z;
            topmost = $(this);
        }
    });

    if(!topmost) {
        return;
    }

    // .. and close it, unless closeOnEscape is off, e.g. the how-it-works
    // help mode turns it off while active and handles Escape on its own.
    var content = topmost.find('.ui-dialog-content');
    if(content.dialog('option', 'closeOnEscape')) {
        content.dialog('close');
    }
});

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

