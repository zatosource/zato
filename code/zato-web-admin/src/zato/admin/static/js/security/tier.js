
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Quota tiers - the list page and the tier editor
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.tier.config = {
    url_base: '/zato/security/tier',
    saved_message: 'OK, saved',
    save_error_message: 'Could not save',
    delete_error_message: 'Could not delete',
    name_required_message: 'Name is required',
    redirect_delay_ms: 750
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.tier.save = function(container_id) {

    var config = $.fn.zato.security.tier.config;

    var tier_id = document.getElementById('tier-id').value;
    var name = document.getElementById('tier-name').value.trim();
    var description = document.getElementById('tier-description').value;
    var rules_json = $.fn.zato.rate_limiting.get_rules(container_id);

    var status = $('#rate-limiting-status');
    status.removeClass('show fade status-message-success status-message-error');

    if(!name) {
        status.text(config.name_required_message).addClass('show status-message-error');
        return;
    }

    $.ajax({
        url: config.url_base + '/save/',
        type: 'POST',
        data: {
            id: tier_id,
            name: name,
            description: description,
            rules_json: rules_json
        },
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function() {
            status.text(config.saved_message).addClass('show status-message-success');

            // A newly created tier has no id yet - go back to the list so the new row is visible
            if(!tier_id) {
                setTimeout(function() {
                    window.location.href = config.url_base + '/';
                }, config.redirect_delay_ms);
            }
        },
        error: function(jqXHR) {
            var msg = config.save_error_message;
            try {
                var response = JSON.parse(jqXHR.responseText);
                if(response.message) {
                    msg = response.message;
                }
            }
            catch(e) {
                if(jqXHR.responseText) {
                    msg = jqXHR.responseText;
                }
            }
            status.text(msg).addClass('show status-message-error');
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.tier.delete_ = function(id, name) {

    var config = $.fn.zato.security.tier.config;

    if(!confirm('Are you sure you want to delete quota tier `' + name + '`?')) {
        return;
    }

    var status = $('#tier-status');
    status.removeClass('show fade status-message-success status-message-error');

    $.ajax({
        url: config.url_base + '/delete/' + id + '/',
        type: 'POST',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function() {
            window.location.reload();
        },
        error: function(jqXHR) {
            var msg = config.delete_error_message;
            try {
                var response = JSON.parse(jqXHR.responseText);
                if(response.message) {
                    msg = response.message;
                }
            }
            catch(e) {
                if(jqXHR.responseText) {
                    msg = jqXHR.responseText;
                }
            }
            status.text(msg).addClass('show status-message-error');
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
