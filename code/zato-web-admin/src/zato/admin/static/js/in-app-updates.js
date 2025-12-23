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
    
    $.fn.zato.in_app_updates.driverObj = window.driver.js.driver({
        showProgress: false,
        showButtons: [],
        overlayColor: 'rgba(0, 0, 0, 0.5)',
        popoverClass: 'driver-popover-custom'
    });

    $('#auto-update-help').on('click', function() {
        $.fn.zato.in_app_updates.driverObj.highlight({
            popover: {
                title: 'Auto-update Information',
                description: 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ullamco laboris nisi ut aliquip ex ea commodo consequat.<br><br>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            }
        });
    });

    $('#version-info-help').on('click', function() {
        $.fn.zato.in_app_updates.driverObj.highlight({
            popover: {
                title: 'Version Information',
                description: 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ullamco laboris nisi ut aliquip ex ea commodo consequat.'
            }
        });
    });
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
