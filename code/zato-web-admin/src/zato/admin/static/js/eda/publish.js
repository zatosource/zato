
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }
$.fn.zato.eda.publish = {};

$.fn.zato.eda.publish.init = function(topics) {
    var $select = $('#publish-topic');
    $select.empty();
    if (topics && topics.length > 0) {
        for (var i = 0; i < topics.length; i++) {
            $select.append('<option value="' + topics[i].name + '">' + topics[i].name + '</option>');
        }
    } else {
        $select.append('<option value="">No topics available</option>');
    }
};

$.fn.zato.eda.publish.submit = function() {
    var topic = $('#publish-topic').val();
    var data = $('#publish-data').val();
    var priority = $('#publish-priority').val();
    var expiration = $('#publish-expiration').val() || '86400';

    if (!topic) {
        alert('Please select a topic');
        return;
    }
    if (!data) {
        alert('Please enter message data');
        return;
    }

    $.ajax({
        url: '/zato/eda/publish/submit/',
        type: 'POST',
        data: {
            topic_name: topic,
            data: data,
            priority: priority,
            expiration: expiration
        },
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(resp) {
            var msg_id = resp.msg_id || '';
            var $suc = $('#publish-success');
            $suc.html('Message published - ID: <a href="/zato/eda/messages/' + encodeURIComponent(topic) + '/' + encodeURIComponent(msg_id) + '/?cluster=1">' + msg_id + '</a>');
            $suc.show();
            setTimeout(function() { $suc.fadeOut(); }, 5000);
            $('#publish-data').val('');
        },
        error: function(xhr) {
            var err = 'Error publishing message';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                err = xhr.responseJSON.error;
            }
            alert(err);
        }
    });
};
