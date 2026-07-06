$(document).ready(function() {

    var config = {};
    config.textareaId = 'sbom';

    $('#copy-button').on('click', function(event) {
        var text = $('#' + config.textareaId).val();
        $.fn.zato.settings.copyToClipboard(text, event);
    });
});
