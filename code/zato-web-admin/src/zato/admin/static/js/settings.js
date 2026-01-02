$.namespace('zato.settings');

$.fn.zato.settings.copyToClipboard = function(text, event) {
    navigator.clipboard.writeText(text).then(function() {
        const tooltip = $('<div class="copy-tooltip">Copied to clipboard</div>');
        $('body').append(tooltip);

        const rect = event.target.getBoundingClientRect();
        tooltip.css({
            left: rect.left + rect.width / 2 - tooltip.outerWidth() / 2 + 'px',
            top: rect.top - tooltip.outerHeight() - 8 + 'px'
        });

        setTimeout(() => tooltip.addClass('show'), 10);

        setTimeout(() => {
            tooltip.removeClass('show');
            setTimeout(() => tooltip.remove(), 200);
        }, 1500);
    });
};

$.fn.zato.settings.handleCopyIcon = function(e) {
    e.stopPropagation();
    const targetId = $(this).data('copy');
    const targetElement = $('#' + targetId);

    const parentProgress = targetElement.closest('.progress-item');
    const fullError = parentProgress.data('full-error');
    const text = fullError || targetElement.text();

    $.fn.zato.settings.copyToClipboard(text, e);
};

$.fn.zato.settings.initDriverTours = function(tours) {
    const driverObj = window.driver.js.driver({
        showProgress: true,
        showButtons: ['next', 'previous', 'close'],
        overlayColor: 'rgba(0, 0, 0, 0.5)',
        popoverClass: 'driver-popover-custom',
        animate: false
    });

    tours.forEach(function(tour) {
        $(tour.trigger).on('click', function() {
            driverObj.setSteps(tour.steps);
            driverObj.drive(0);
        });
    });
};

$.fn.zato.settings.initToggleLabelClick = function(labelSelector, checkboxSelector) {
    $(labelSelector).on('click', function() {
        const checkbox = $(checkboxSelector);
        checkbox.prop('checked', !checkbox.prop('checked')).trigger('change');
    });
};

$.fn.zato.settings.updateProgress = function(step, status, message, statusText) {
    const item = $('#progress-' + step);
    const icon = item.find('.progress-icon');
    const text = item.find('.progress-text');
    const copyButton = item.find('.progress-error-copy');

    const displayMessage = statusText ? '<span class="progress-count">' + message + '</span> <span class="progress-status">' + statusText + '</span>' : message;

    if (status === 'processing') {
        icon.addClass('spinner').removeClass('completed error').html('<img src="/static/gfx/spinner.svg">');
        item.removeClass('error-state').addClass('processing-state');
        if (copyButton.length) {
            copyButton.addClass('hidden');
        }
    } else if (status === 'completed') {
        icon.removeClass('spinner error').addClass('completed').text('✓');
        item.removeClass('error-state processing-state');
        if (copyButton.length) {
            copyButton.addClass('hidden');
        }
    } else if (status === 'error') {
        icon.removeClass('spinner completed').addClass('error').text('✗');
        item.addClass('error-state').removeClass('processing-state');
        if (copyButton.length) {
            copyButton.removeClass('hidden');
        }
    }

    text.html(displayMessage);
};

$.fn.zato.settings.activateSpinner = function(spinnerSelector) {
    $(spinnerSelector).addClass('active');
};

$.fn.zato.settings.deactivateSpinner = function(spinnerSelector) {
    $(spinnerSelector).removeClass('active');
};
