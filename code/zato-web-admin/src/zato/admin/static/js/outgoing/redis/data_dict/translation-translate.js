
$(document).ready(function() {
    _.each(['system1', 'key1', 'value1', 'system2', 'key2'], function(name) {
        $.fn.zato.data_table.set_field_required('#id_' + name);
    });

    $('#translate-form').QQQ-zvalidator();

    var change_data = [
        ['system1', 'key1', '../get-key-list', [{'system':'system1'}]],
        ['system2', 'key2', '../get-key-list', [{'system':'system2'}]],

        ['key1', 'value1', '../get-value-list', [{'system':'system1', 'key':'key1'}]],
        ['key2', 'value2', '../get-value-list', [{'system':'system2', 'key':'key2'}]],
    ];

    $.fn.zato.kvdb.data_dict.translation.setup_selects(change_data);

    var system1 = $('#postback_system1').val();

    if(system1 != '') {

        var instance = $.fn.zato.data_table.TranslationEntry();
        instance.system1 = system1;
        instance.key1 = $('#postback_key1').val();
        instance.value1 = $('#postback_value1').val();
        instance.system2 = $('#postback_system2').val();
        instance.key2 = $('#postback_key2').val();
        instance.value2 = '';

        var populate_form = function() {
            $.fn.zato.form.populate($('#translate-form'), instance, null, '#id_');
        }

        var update_value1 = function() {
            $.fn.zato.kvdb.data_dict.translation.update_selects('value1', '../get-value-list',
                {'system':instance.system1, 'key':instance.key1}, populate_form)
        };

        var update_key2 = function() {
            $.fn.zato.kvdb.data_dict.translation.update_selects('key2', '../get-key-list', {'system':instance.system2}, update_value1)
        };

        var update_key1 = function() {
            $.fn.zato.kvdb.data_dict.translation.update_selects('key1', '../get-key-list', {'system':instance.system1}, update_key2)
        };
        update_key1();
    }
})
