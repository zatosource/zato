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
