$(document).ready(function() {

    $.fn.zato.account.basic_settings.set_totp_key_qr_code();

    $('#id_totp_key').keyup(function() {
        $.fn.zato.account.basic_settings.set_totp_key_qr_code();
    });

    $('#id_totp_key_label').keyup(function() {
        $.fn.zato.account.basic_settings.set_totp_key_qr_code();
    });

    $('input[id^="color_"]').each(function(idx, input) {
        $(input).ColorPicker({
            color: '#0000ff',
            onShow: function(picker) {
                $(picker).fadeIn(100);
                return false;
            },
            onHide: function(picker) {
                $(picker).fadeOut(100);
                var id = $(input).attr('id').replace('color_', '');
                var span = $('#color_picker_span_' + id);

                $('#previev_a_'+id).remove();
                span.append(String.format('<a id="previev_a_{0}" href="javascript:$.fn.zato.account.basic_settings.preview({0})">(preview)</a>', id));
                return false;
            },
            onChange: function(hsb, hex, rgb) {
                _.each(['color', 'backgroundColor'], function(attr_name) {
                    _.each([input, '#cluster_color_div'], function(elem) {
                        $(elem).css(attr_name, '#' + hex);
                        $(elem).val(hex); // Works on the 'input' element only
                    });
                });
            }
        });
    });

    $('input[id^="checkbox_"]').change(function(e) {
        var id = $(this).attr('id').replace('checkbox_', '');
        var span = $('#color_picker_span_' + id);
        if(this.checked) {
            span.removeClass('hidden').addClass('visible');
        }
        else {
            span.removeClass('visible').addClass('hidden');
        };
    });

});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.account.basic_settings.preview = function(id) {
    var div = $('#cluster_color_div');
    div.removeClass('hidden').addClass('visible');
    div.css('backgroundColor', $('#color_'+id).css('backgroundColor'));
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


$.fn.zato.account.basic_settings.set_totp_key_qr_code = function() {

    // Clear out any old QR code
    $('#totp_key_qr_code').replaceWith('<div id="totp_key_qr_code" style="width:100px; height:100px; margin-top:25px;margin-bottom:25px"></div>');

    // otpauth://totp/Zato%20web-admin:admin?secret=I6YADI55V27JQTVN&amp;issuer=Zato%20web-admin
    // otpauth://totp/{0}:{1}?secret={2}&amp;issuer={0}

    // Populate the element for the QR to be based on. Note that we build the QR using the key's provisioning
    // address rather than from the key directly.
    var issuer = document.getElementById('id_totp_key_label').value || 'Zato';
    issuer = encodeURIComponent(issuer);

    var username = document.getElementById('id_username').value;
    var secret = document.getElementById('id_totp_key').value;

    token_provsion_elem = document.getElementById('id_totp_key_provision_uri');
    token_provsion_elem.value = String.format('otpauth://totp/{0}:{1}?secret={2}&amp;issuer={0}',
        issuer, username, secret);

    var qr_code_elem = document.getElementById('totp_key_qr_code');
    var qr_code = new QRCode(qr_code_elem, {
        width : 100,
        height : 100
    });

    qr_code.clear();
    qr_code.makeCode(token_provsion_elem.value);

}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.account.basic_settings.generate_new_totp_key = function() {

    var totp_elem = document.getElementById('id_totp_key');

    var http_callback = function(data, status) {
        var success = status == 'success';
        if(success) {
            totp_elem.value = data.responseText;
            $.fn.zato.account.basic_settings.set_totp_key_qr_code();
        }
        else {
            $.fn.zato.user_message(success, data.responseText);
        }
    }

    $.fn.zato.post('./generate-totp-key', http_callback, null, 'text', true);

}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
