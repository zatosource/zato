
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }
$.fn.zato.eda.publish = {};

$.fn.zato.eda.publish._file_data = null;
$.fn.zato.eda.publish._file_name = null;

$.fn.zato.eda.publish.init = function(topics, initial_topic_name) {
    var $select = $('#publish-topic');
    $select.empty();
    $select.append('<option value=""></option>');
    if (topics && topics.length > 0) {
        for (var topic_idx = 0; topic_idx < topics.length; topic_idx++) {
            $select.append('<option value="' + topics[topic_idx].name + '">' + topics[topic_idx].name + '</option>');
        }
    }

    if (initial_topic_name) {
        $select.val(initial_topic_name);
    }

    $select.chosen({
        width: '100%',
        search_contains: true,
        no_results_text: 'No matching topic'
    });

    var $file_input = $('#publish-file-input');
    var $drop_area = $('#publish-file-drop');
    var $browse_link = $('#publish-file-browse');

    $browse_link.on('click', function(e) {
        e.preventDefault();
        $file_input.click();
    });

    $file_input.on('change', function() {
        if (this.files && this.files[0]) {
            $.fn.zato.eda.publish._handle_file(this.files[0]);
        }
    });

    $drop_area.on('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass('has-file');
    });

    $drop_area.on('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (!$.fn.zato.eda.publish._file_name) {
            $(this).removeClass('has-file');
        }
    });

    $drop_area.on('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        var files = e.originalEvent.dataTransfer.files;
        if (files && files[0]) {
            $.fn.zato.eda.publish._handle_file(files[0]);
        }
    });
};

$.fn.zato.eda.publish._handle_file = function(file) {
    var reader = new FileReader();
    reader.onload = function(e) {
        var content = e.target.result;
        $('#publish-data').val(content);
        $.fn.zato.eda.publish._file_name = file.name;
        $.fn.zato.eda.publish._file_data = content;
        $('#publish-file-drop').addClass('has-file').text('File loaded: ' + file.name + ' (' + file.size + ' bytes)');
    };
    reader.readAsText(file);
};

$.fn.zato.eda.publish.submit = function() {
    var topic = $('#publish-topic').val();
    var data = $('#publish-data').val() || '';

    if (!topic) {
        alert('Please select a topic');
        return;
    }

    var $btn = $('#publish-button');
    var $spinner = $('#publish-spinner');
    var $status = $('#publish-status');

    $btn.prop('disabled', true);
    $spinner.addClass('active');
    $status.removeClass('show');

    $.ajax({
        url: '/zato/eda/publish/submit/',
        type: 'POST',
        data: {
            topic_name: topic,
            data: data,
            priority: '5',
            expiration: '86400'
        },
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(resp) {
            var msg_id = resp.msg_id || '';
            $spinner.removeClass('active');
            $btn.prop('disabled', false);
            $status.html('Published message: <span class="detail-copy-target" data-copy-value="' + msg_id + '">' + msg_id + '</span>');
            $status.addClass('show');
            $.fn.zato.eda.bind_copy_targets();
        },
        error: function(xhr) {
            $spinner.removeClass('active');
            $btn.prop('disabled', false);
            var err = 'Error publishing message';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                err = xhr.responseJSON.error;
            }
            alert(err);
        }
    });
};
