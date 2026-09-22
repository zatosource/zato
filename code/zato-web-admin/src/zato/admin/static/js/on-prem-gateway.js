$.fn.zato = $.fn.zato || {};
$.fn.zato.onPremGateway = $.fn.zato.onPremGateway || {};

(function() {

    var dashboard = $.fn.zato.onPremGateway;

    dashboard.config = {
        apiPrefix: '/zato/on-prem-gateway/',
        hostsPlaceholder: '',
        downloadUrl: '',
        refreshInterval: 10000,
        statusConnected: 'Connected',
        statusOffline: 'Enrolled, offline',
        statusNotEnrolled: 'Not enrolled',
        statusInactive: 'Not active',
        emptyLabel: 'No gateways yet',
        formTitleNew: 'New gateway',
        formTitleEdit: 'Edit gateway',
        saveLabel: 'Save',
        savingLabel: 'Saving...',
        deleteConfirm: 'Delete {name}?',
        resetKeyConfirm: 'Reset the key of {name}?',
        tokenTitle: 'Enrollment token for {name}',
        copyLabel: 'Copy',
        copiedLabel: 'Copied'
    };

    dashboard.state = {
        gateways: [],
        editId: null,
        timer: null
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.getStatus = function(gateway) {

        if (!gateway.is_active) {
            return dashboard.config.statusInactive;
        }

        if (gateway.is_connected) {
            return dashboard.config.statusConnected;
        }

        if (gateway.has_key) {
            return dashboard.config.statusOffline;
        }

        return dashboard.config.statusNotEnrolled;
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.getStatusClass = function(gateway) {

        if (gateway.is_active && gateway.is_connected) {
            return 'on-prem-gateway-status-connected';
        }

        if (gateway.is_active && gateway.has_key) {
            return 'on-prem-gateway-status-offline';
        }

        return 'on-prem-gateway-status-unknown';
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.escape = function(text) {

        var container = $('<div/>');

        return container.text(text).html();
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.buildRow = function(gateway) {

        var status = dashboard.getStatus(gateway);
        var statusClass = dashboard.getStatusClass(gateway);
        var since = gateway.is_connected ? gateway.connected_since : '';

        var out = [];

        out.push('<tr data-id="' + gateway.id + '">');
        out.push('<td class="on-prem-gateway-name">' + dashboard.escape(gateway.name) + '</td>');
        out.push('<td><span class="' + statusClass + '">' + dashboard.escape(status) + '</span></td>');
        out.push('<td>' + gateway.host_count + '</td>');
        out.push('<td>' + dashboard.escape(since) + '</td>');
        out.push('<td class="on-prem-gateway-actions">' +
            '<a href="#" class="on-prem-gateway-token-link">Enrollment token</a>' +
            '<a href="#" class="on-prem-gateway-edit-link">Edit</a>' +
            '<a href="#" class="on-prem-gateway-reset-link">Reset key</a>' +
            '<a href="#" class="on-prem-gateway-delete-link">Delete</a>' +
            '</td>');
        out.push('</tr>');

        return out.join('');
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.render = function() {

        var rows = $('#on-prem-gateway-rows');
        var gateways = dashboard.state.gateways;
        var hubError = '';

        rows.empty();

        if (!gateways.length) {
            rows.append('<tr><td colspan="5" class="on-prem-gateway-empty">' +
                dashboard.escape(dashboard.config.emptyLabel) + '</td></tr>');
        }

        for (var gatewayIndex = 0; gatewayIndex < gateways.length; gatewayIndex++) {

            var gateway = gateways[gatewayIndex];

            if (gateway.hub_error) {
                hubError = gateway.hub_error;
            }

            rows.append(dashboard.buildRow(gateway));
        }

        if (hubError) {
            $('#on-prem-gateway-hub-error').text(hubError).removeClass('hidden');
        }
        else {
            $('#on-prem-gateway-hub-error').addClass('hidden');
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.findGateway = function(id) {

        var gateways = dashboard.state.gateways;
        var wanted = String(id);

        for (var gatewayIndex = 0; gatewayIndex < gateways.length; gatewayIndex++) {

            var gateway = gateways[gatewayIndex];

            if (String(gateway.id) === wanted) {
                return gateway;
            }
        }

        return null;
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.showMessage = function(text, isError) {

        var element = $('#on-prem-gateway-message');

        element.text(text).removeClass('hidden');
        element.toggleClass('on-prem-gateway-message-error', isError === true);
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.hideMessage = function() {
        $('#on-prem-gateway-message').addClass('hidden').text('');
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.refresh = function() {

        $.ajax({
            url: dashboard.config.apiPrefix + 'get-list',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    dashboard.state.gateways = response.data;
                    dashboard.render();
                }
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.post = function(path, payload, onSuccess) {

        $.ajax({
            url: dashboard.config.apiPrefix + path,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(payload),
            dataType: 'json',

            success: function(response) {
                if (response.success) {
                    onSuccess(response.data);
                }
                else {
                    dashboard.showMessage(response.error, true);
                }
            },

            error: function(request) {

                var message = request.responseText;

                if (request.responseJSON) {
                    message = request.responseJSON.error;
                }

                dashboard.showMessage(message, true);
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.resetForm = function() {

        dashboard.state.editId = null;

        $('#on-prem-gateway-form-title').text(dashboard.config.formTitleNew);
        $('#on-prem-gateway-name').val('');
        $('#on-prem-gateway-is-active').prop('checked', true);
        $('#on-prem-gateway-hosts').val('');
        $('#on-prem-gateway-cancel').addClass('hidden');

        dashboard.hideMessage();
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.fillForm = function(gateway) {

        var hosts = gateway.hosts.join('\n');

        dashboard.state.editId = gateway.id;

        $('#on-prem-gateway-form-title').text(dashboard.config.formTitleEdit);
        $('#on-prem-gateway-name').val(gateway.name);
        $('#on-prem-gateway-is-active').prop('checked', gateway.is_active);
        $('#on-prem-gateway-hosts').val(hosts);
        $('#on-prem-gateway-cancel').removeClass('hidden');

        dashboard.hideMessage();
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.save = function() {

        var payload = {
            name: $('#on-prem-gateway-name').val(),
            is_active: $('#on-prem-gateway-is-active').is(':checked'),
            hosts: $('#on-prem-gateway-hosts').val()
        };

        var path = 'create';

        if (dashboard.state.editId !== null) {
            payload.id = dashboard.state.editId;
            path = 'edit';
        }

        dashboard.hideMessage();

        dashboard.post(path, payload, function() {
            dashboard.resetForm();
            dashboard.refresh();
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.showToken = function(name, token) {

        var title = dashboard.config.tokenTitle.replace('{name}', name);

        $('#on-prem-gateway-token-title').text(title);
        $('#on-prem-gateway-token-value').val(token);
        $('#on-prem-gateway-token-download').attr('href', dashboard.config.downloadUrl);
        $('#on-prem-gateway-token-copy').text(dashboard.config.copyLabel);
        $('#on-prem-gateway-token').removeClass('hidden');
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.getClickedGateway = function(element) {

        var id = $(element).closest('tr').data('id');

        return dashboard.findGateway(id);
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.bind = function() {

        $('#on-prem-gateway-save').on('click', function(event) {
            event.preventDefault();
            dashboard.save();
        });

        $('#on-prem-gateway-cancel').on('click', function(event) {
            event.preventDefault();
            dashboard.resetForm();
        });

        $('#on-prem-gateway-rows').on('click', '.on-prem-gateway-edit-link', function(event) {

            event.preventDefault();

            var gateway = dashboard.getClickedGateway(this);

            dashboard.fillForm(gateway);
        });

        $('#on-prem-gateway-rows').on('click', '.on-prem-gateway-delete-link', function(event) {

            event.preventDefault();

            var gateway = dashboard.getClickedGateway(this);
            var question = dashboard.config.deleteConfirm.replace('{name}', gateway.name);

            if (!window.confirm(question)) {
                return;
            }

            dashboard.post('delete/' + gateway.id, {}, function() {
                dashboard.resetForm();
                dashboard.refresh();
            });
        });

        $('#on-prem-gateway-rows').on('click', '.on-prem-gateway-reset-link', function(event) {

            event.preventDefault();

            var gateway = dashboard.getClickedGateway(this);
            var question = dashboard.config.resetKeyConfirm.replace('{name}', gateway.name);

            if (!window.confirm(question)) {
                return;
            }

            dashboard.post('reset-key/' + gateway.id, {}, function() {
                dashboard.refresh();
            });
        });

        $('#on-prem-gateway-rows').on('click', '.on-prem-gateway-token-link', function(event) {

            event.preventDefault();

            var gateway = dashboard.getClickedGateway(this);

            dashboard.post('enrollment-token/' + gateway.id, {}, function(data) {
                dashboard.showToken(gateway.name, data.token);
            });
        });

        $('#on-prem-gateway-token-copy').on('click', function(event) {

            event.preventDefault();

            var field = document.getElementById('on-prem-gateway-token-value');

            field.select();
            document.execCommand('copy');

            $('#on-prem-gateway-token-copy').text(dashboard.config.copiedLabel);
        });

        $('#on-prem-gateway-token-close').on('click', function(event) {
            event.preventDefault();
            $('#on-prem-gateway-token').addClass('hidden');
            $('#on-prem-gateway-token-value').val('');
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    dashboard.init = function(options) {

        dashboard.config.apiPrefix = options.apiPrefix;
        dashboard.config.hostsPlaceholder = options.hostsPlaceholder;
        dashboard.config.downloadUrl = options.downloadUrl;

        dashboard.state.gateways = options.gateways;

        $('#on-prem-gateway-hosts').attr('placeholder', dashboard.config.hostsPlaceholder);

        dashboard.render();
        dashboard.bind();
        dashboard.resetForm();

        dashboard.state.timer = window.setInterval(dashboard.refresh, dashboard.config.refreshInterval);
    };

})();
