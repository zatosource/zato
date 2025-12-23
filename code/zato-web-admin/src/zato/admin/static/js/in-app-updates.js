$.namespace('zato.in_app_updates');

$.fn.zato.in_app_updates.init = function() {
    const headerBadge = window.parent.document.getElementById('update-status-badge');
    if (headerBadge) {
        headerBadge.style.animation = 'none';
    }

    $('#check-button').on('click', $.fn.zato.in_app_updates.handleCheckForUpdates);
    $('.copy-icon').on('click', $.fn.zato.in_app_updates.handleCopyIcon);
    $(document).on('click', '.upgrade-info', $.fn.zato.in_app_updates.handleCopyUpgradeInfo);
    $('#update-button').on('click', $.fn.zato.in_app_updates.handleUpdateClick);
    $('#auto-update-help').on('click', $.fn.zato.in_app_updates.showHelpOverlay);
    $('.help-overlay-close').on('click', $.fn.zato.in_app_updates.hideHelpOverlay);
    $('#auto-update-help-overlay').on('click', function(e) {
        if (e.target === this) {
            $.fn.zato.in_app_updates.hideHelpOverlay();
        }
    });
};

$.fn.zato.in_app_updates.showHelpOverlay = function() {
    $('#auto-update-help-overlay').fadeIn(200);
};

$.fn.zato.in_app_updates.hideHelpOverlay = function() {
    $('#auto-update-help-overlay').fadeOut(200);
};

$.fn.zato.in_app_updates.handleCheckForUpdates = function() {
    const spinner = $(this).siblings('.check-button-spinner');
    const updatesFound = $(this).siblings('.updates-found');

    spinner.addClass('active');

    setTimeout(() => {
        spinner.removeClass('active');
        updatesFound.addClass('show');

        const timestamp = Date.now();
        const newVersion = $('#latest-version').data('base-version') + '.' + timestamp;
        const latestVersionEl = $('#latest-version');
        latestVersionEl.text(newVersion);

        setTimeout(() => {
            latestVersionEl.addClass('pulsate');
        }, 50);

        setTimeout(() => {
            updatesFound.addClass('fade');
            setTimeout(() => {
                updatesFound.removeClass('show fade');
            }, 500);
        }, 1500);

        setTimeout(() => {
            latestVersionEl.removeClass('pulsate');
        }, 1600);
    }, 2000);
};

$.fn.zato.in_app_updates.copyToClipboard = function(text, event) {
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

$.fn.zato.in_app_updates.handleCopyIcon = function(e) {
    e.stopPropagation();
    const targetId = $(this).data('copy');
    const text = $('#' + targetId).text();
    $.fn.zato.in_app_updates.copyToClipboard(text, e);
};

$.fn.zato.in_app_updates.handleCopyUpgradeInfo = function(e) {
    const text = $(this).text().trim();
    $.fn.zato.in_app_updates.copyToClipboard(text, e);
};

$.fn.zato.in_app_updates.handleUpdateClick = function() {
    const button = $(this);
    button.prop('disabled', true);

    $('.progress-item').removeClass('hidden');

    $.fn.zato.in_app_updates.updateProgress('download', 'processing', 'Downloading update package...');

    setTimeout(() => {
        $.fn.zato.in_app_updates.updateProgress('download', 'completed', 'Download complete');
        $.fn.zato.in_app_updates.updateProgress('install', 'processing', 'Installing updates...');

        setTimeout(() => {
            $.fn.zato.in_app_updates.updateProgress('install', 'completed', 'Installation complete');

            setTimeout(() => {
                $('#progress-install .upgrade-info').addClass('show');
                const latestVersion = $('#latest-version').data('base-version');
                $('#current-version').text(latestVersion);
                button.prop('disabled', false);

                const upToDateBadge = $('#up-to-date-badge');
                upToDateBadge.removeClass('no').addClass('yes').text('Yes');

                const headerBadge = window.parent.document.getElementById('update-status-badge');
                if (headerBadge) {
                    headerBadge.classList.remove('with-shine');
                    headerBadge.classList.add('white');
                    headerBadge.textContent = 'Up to date';
                }

                confetti({
                    particleCount: 40,
                    spread: 50,
                    origin: { y: 0.5 },
                    colors: ['#0073bb', '#067f39', '#ffd700', '#ff8c00'],
                    scalar: 0.7,
                    gravity: 1,
                    drift: 0,
                    ticks: 150
                });
            }, 300);
        }, 100);
    }, 100);
};

$.fn.zato.in_app_updates.updateProgress = function(step, status, message) {
    const item = $('#progress-' + step);
    const icon = item.find('.progress-icon');
    const text = item.find('.progress-text');

    if (status === 'processing') {
        icon.addClass('spinner').html('<img src="/static/gfx/spinner.svg" style="animation: spin 0.5s linear infinite; width: 28px; height: 28px; filter: brightness(0) saturate(100%) invert(8%) sepia(91%) saturate(2593%) hue-rotate(194deg) brightness(96%) contrast(99%);">');  
    } else if (status === 'completed') {
        icon.removeClass('spinner').addClass('completed').text('✓');
    }

    text.text(message);
};

$(document).ready(function() {
    $.fn.zato.in_app_updates.init();
});
