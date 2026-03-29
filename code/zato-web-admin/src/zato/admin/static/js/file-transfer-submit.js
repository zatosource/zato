$.fn.zato.file_transfer_submit = {};

$.fn.zato.file_transfer_submit.init = function() {
    $('#submit-button').on('click', $.fn.zato.file_transfer_submit.handleSubmit);
};

$.fn.zato.file_transfer_submit.handleSubmit = function() {
    var fileInput = document.getElementById('file-input');
    var button = $('#submit-button');
    var status = $('#submit-status');

    if (fileInput.files.length === 0) {
        alert('Please select a file');
        return;
    }

    button.prop('disabled', true);
    status.text('Uploading...');

    var file = fileInput.files[0];
    var formData = new FormData();
    formData.append('file', file);
    formData.append('filename', file.name);
    formData.append('source_protocol', 'Manual upload');
    formData.append('source_detail', 'Uploaded via Dashboard');

    $.ajax({
        url: '/zato/file-transfer/submit/file/',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        success: function(response) {
            if (response.success) {
                var txnId = response.transaction_id;
                status.html('Transaction created: <a href="/zato/file-transfer/transaction/' + txnId + '/">' + txnId + '</a>');
                $('#file-input').val('');
            } else {
                status.text('Error: ' + (response.error || 'Processing failed'));
            }
            button.prop('disabled', false);
        },
        error: function(xhr) {
            var errorMsg = 'Processing failed';
            try {
                var response = JSON.parse(xhr.responseText);
                errorMsg = response.error || errorMsg;
            } catch(e) {
                errorMsg = xhr.responseText || errorMsg;
            }
            status.text('Error: ' + errorMsg);
            button.prop('disabled', false);
        }
    });
};

$(document).ready(function() {
    $.fn.zato.file_transfer_submit.init();
});
