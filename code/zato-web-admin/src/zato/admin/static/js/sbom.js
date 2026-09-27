$(document).ready(function() {

    var config = {};
    config.textareaId = 'sbom';

    var textarea = document.getElementById(config.textareaId);
    $.fn.zato.highlight.attach(textarea, $.fn.zato.highlight.json_to_html);

    $('#copy-button').on('click', function(event) {
        var text = $('#' + config.textareaId).val();
        $.fn.zato.settings.copyToClipboard(text, event);
    });
});
