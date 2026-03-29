$.fn.zato.file_transfer_submit = {};

$.fn.zato.file_transfer_submit.init = function() {
    $('#file-input').on('change', $.fn.zato.file_transfer_submit.handleFileSelect);
    $('#submit-button').on('click', $.fn.zato.file_transfer_submit.handleSubmit);
    $('.copy-icon').on('click', $.fn.zato.settings.handleCopyIcon);
};

$.fn.zato.file_transfer_submit.handleFileSelect = function() {
    const fileInput = document.getElementById('file-input');
    const filenameInput = document.getElementById('filename-input');

    if (fileInput.files.length > 0) {
        filenameInput.value = fileInput.files[0].name;
    }
};

$.fn.zato.file_transfer_submit.handleSubmit = function() {
    console.log('handleSubmit called');
    const fileInput = document.getElementById('file-input');
    const button = $('#submit-button');

    if (fileInput.files.length === 0) {
        console.log('No file selected');
        alert('Please select a file');
        return;
    }

    console.log('File selected:', fileInput.files[0].name);
    button.prop('disabled', true);

    $('#progress-upload').removeClass('hidden error-state');
    $('#progress-process').addClass('hidden').removeClass('error-state');
    $('#completion-badge').removeClass('show');

    $.fn.zato.settings.updateProgress('upload', 'processing', 'Uploading file...');

    const file = fileInput.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        const base64Content = e.target.result.split(',')[1];

        const formData = new FormData();
        formData.append('file', file);
        formData.append('filename', $('#filename-input').val() || file.name);
        formData.append('source_protocol', $('#source-protocol').val());
        formData.append('source_detail', $('#source-detail').val());

        $.fn.zato.settings.updateProgress('upload', 'completed', 'File uploaded');

        $('#progress-process').removeClass('hidden');
        $.fn.zato.settings.updateProgress('process', 'processing', 'Processing file...');

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
                console.log('Submit response:', JSON.stringify(response));
                if (response.success) {
                    console.log('Transaction ID:', response.transaction_id);
                    $.fn.zato.settings.updateProgress('process', 'completed', 'Transaction created');

                    const badge = $('#completion-badge');
                    const txnId = response.transaction_id;
                    badge.html('<a href="/zato/file-transfer/transaction/' + txnId + '/" style="color: inherit; text-decoration: underline;">Transaction ' + txnId + '</a>');
                    badge.addClass('show');

                    $('#file-input').val('');
                    $('#filename-input').val('');
                } else {
                    $.fn.zato.settings.updateProgress('process', 'error', response.error || 'Processing failed');
                }
                button.prop('disabled', false);
            },
            error: function(xhr) {
                console.log('Submit error:', xhr.status, xhr.responseText);
                let errorMsg = 'Processing failed';
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMsg = response.error || errorMsg;
                } catch(e) {
                    errorMsg = xhr.responseText || errorMsg;
                }

                $.fn.zato.settings.updateProgress('process', 'error', errorMsg);
                button.prop('disabled', false);
            }
        });
    };

    reader.onerror = function() {
        $.fn.zato.settings.updateProgress('upload', 'error', 'Failed to read file');
        button.prop('disabled', false);
    };

    reader.readAsDataURL(file);
};

$(document).ready(function() {
    $.fn.zato.file_transfer_submit.init();
});
