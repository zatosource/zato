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
    $('#auto-restart').on('change', $.fn.zato.in_app_updates.handleAutoUpdateToggle);
    $('#update-frequency').on('change', $.fn.zato.in_app_updates.handleFrequencyChange);
    $('#config-save-button').on('click', $.fn.zato.in_app_updates.handleSaveSchedule);

    $.fn.zato.in_app_updates.loadSchedule();

    $.fn.zato.in_app_updates.versionSteps = [
        {
            popover: {
                title: 'Version info',
                description: 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ullamco laboris nisi ut aliquip ex ea commodo consequat.'
            }
        },
        {
            element: '#check-button',
            popover: {
                title: 'Check for updates',
                description: 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ullamco laboris nisi ut aliquip ex ea commodo consequat.'
            }
        },
        {
            element: '#update-button',
            popover: {
                title: 'Install updates',
                description: 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ullamco laboris nisi ut aliquip ex ea commodo consequat.<br><br>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            }
        }
    ];

    $.fn.zato.in_app_updates.configSteps = [
        {
            popover: {
                title: 'Config',
                description: 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ullamco laboris nisi ut aliquip ex ea commodo consequat.'
            }
        },
        {
            element: '.summary-item',
            popover: {
                title: 'Auto-update',
                description: 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ullamco laboris nisi ut aliquip ex ea commodo consequat.<br><br>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            }
        }
    ];

    $.fn.zato.in_app_updates.logsSteps = [
        {
            popover: {
                title: 'Logs',
                description: 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ullamco laboris nisi ut aliquip ex ea commodo consequat.'
            }
        },
        {
            element: '.dashboard-link-item',
            popover: {
                title: 'Download logs',
                description: 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ullamco laboris nisi ut aliquip ex ea commodo consequat.<br><br>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            }
        }
    ];

    console.log('Creating single driver instance');
    $.fn.zato.in_app_updates.driverObj = window.driver.js.driver({
        showProgress: true,
        showButtons: ['next', 'previous', 'close'],
        overlayColor: 'rgba(0, 0, 0, 0.5)',
        popoverClass: 'driver-popover-custom',
        animate: false
    });
    console.log('Driver instance created');

    $('#version-info-help').on('click', function() {
        console.log('Version info help clicked, setting version steps:', JSON.stringify($.fn.zato.in_app_updates.versionSteps.map(s => s.popover ? s.popover.title : 'no title'), null, 2));
        $.fn.zato.in_app_updates.driverObj.setSteps($.fn.zato.in_app_updates.versionSteps);
        console.log('Steps set, now driving from step 0');
        $.fn.zato.in_app_updates.driverObj.drive(0);
    });

    $('#auto-update-help').on('click', function() {
        console.log('Auto-update help clicked, setting config steps:', JSON.stringify($.fn.zato.in_app_updates.configSteps.map(s => s.popover ? s.popover.title : 'no title'), null, 2));
        $.fn.zato.in_app_updates.driverObj.setSteps($.fn.zato.in_app_updates.configSteps);
        console.log('Steps set, now driving from step 0');
        $.fn.zato.in_app_updates.driverObj.drive(0);
    });

    $('#logs-help').on('click', function() {
        console.log('Logs help clicked, setting logs steps:', JSON.stringify($.fn.zato.in_app_updates.logsSteps.map(s => s.popover ? s.popover.title : 'no title'), null, 2));
        $.fn.zato.in_app_updates.driverObj.setSteps($.fn.zato.in_app_updates.logsSteps);
        console.log('Steps set, now driving from step 0');
        $.fn.zato.in_app_updates.driverObj.drive(0);
    });

    $('.summary-label').on('click', function() {
        const checkbox = $('#auto-restart');
        checkbox.prop('checked', !checkbox.prop('checked'));
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
    }, 200);
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

$.fn.zato.in_app_updates.handleAutoUpdateToggle = function() {
    const isEnabled = $(this).is(':checked');

    console.log('Auto-update toggle changed, enabled:', isEnabled);

    if (isEnabled) {
        console.log('Showing schedule frequency');
        $('#schedule-frequency').removeClass('hidden');
        $('.save-button-container').css('display', 'flex');
        $.fn.zato.in_app_updates.updateScheduleOptions();
    } else {
        console.log('Hiding all schedule fields');
        $('#schedule-frequency').addClass('hidden');
        $('#schedule-day').addClass('hidden');
        $('#schedule-position').addClass('hidden');
        $('#schedule-time').addClass('hidden');
        $('.save-button-container').css('display', 'none');

        $.ajax({
            url: '/zato/updates/delete-schedule',
            type: 'POST',
            headers: {
                'X-CSRFToken': $.cookie('csrftoken')
            }
        });
    }
};

$.fn.zato.in_app_updates.handleFrequencyChange = function() {
    $.fn.zato.in_app_updates.updateScheduleOptions();
};

$.fn.zato.in_app_updates.updateScheduleOptions = function() {
    const frequency = $('#update-frequency').val();

    console.log('updateScheduleOptions called, frequency:', frequency);

    $('#schedule-day').addClass('hidden');
    $('#schedule-position').addClass('hidden');
    $('#schedule-time').addClass('hidden');

    console.log('All schedule fields hidden');

    if (frequency === 'hourly') {
        console.log('Hourly selected - no additional fields shown');
    } else if (frequency === 'daily') {
        console.log('Daily selected - showing time');
        $('#schedule-time').removeClass('hidden');
    } else if (frequency === 'weekly') {
        console.log('Weekly selected - showing day and time');
        $('#schedule-day').removeClass('hidden');
        $('#schedule-time').removeClass('hidden');
    } else if (frequency === 'monthly') {
        console.log('Monthly selected - showing position, day, and time');
        $('#schedule-position').removeClass('hidden');
        $('#schedule-day').removeClass('hidden');
        $('#schedule-time').removeClass('hidden');
    }

    console.log('schedule-day hidden:', $('#schedule-day').hasClass('hidden'));
    console.log('schedule-position hidden:', $('#schedule-position').hasClass('hidden'));
    console.log('schedule-time hidden:', $('#schedule-time').hasClass('hidden'));
};

$.fn.zato.in_app_updates.loadSchedule = function() {
    $.ajax({
        url: '/zato/updates/load-schedule',
        type: 'GET',
        success: function(response) {
            if (response.success && response.schedule) {
                $('#auto-restart').prop('checked', true);
                $('#update-frequency').val(response.schedule.frequency);
                $('#update-day').val(response.schedule.day);
                $('#update-position').val(response.schedule.position);
                $('#update-time').val(response.schedule.time);

                $('#schedule-frequency').removeClass('hidden');
                $('.save-button-container').css('display', 'flex');
                $.fn.zato.in_app_updates.updateScheduleOptions();
            }
        }
    });
};

$.fn.zato.in_app_updates.handleSaveSchedule = function() {
    const scheduleData = {
        frequency: $('#update-frequency').val(),
        day: $('#update-day').val(),
        position: $('#update-position').val(),
        time: $('#update-time').val()
    };

    $('.config-save-spinner').css('display', 'block');
    $('.config-saved-message').css('display', 'none');
    $('#config-save-button').prop('disabled', true);

    const startTime = Date.now();

    $.ajax({
        url: '/zato/updates/save-schedule',
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify(scheduleData),
        contentType: 'application/json',
        success: function(response) {
            const elapsed = Date.now() - startTime;
            const minDelay = 500;
            const remainingDelay = Math.max(0, minDelay - elapsed);

            setTimeout(function() {
                $('.config-save-spinner').css('display', 'none');
                $('.config-saved-message').css('display', 'inline-block');
                $('#config-save-button').prop('disabled', false);

                setTimeout(function() {
                    $('.config-saved-message').css('display', 'none');
                }, 1500);
            }, remainingDelay);
        },
        error: function() {
            $('.config-save-spinner').css('display', 'none');
            $('#config-save-button').prop('disabled', false);
        }
    });
};

$.fn.zato.in_app_updates.handleUpdateClick = function() {
    const button = $(this);
    button.prop('disabled', true);

    $('#progress-download').removeClass('hidden error-state');
    $('#progress-install').addClass('hidden').removeClass('error-state');
    $('#progress-install .upgrade-info').removeClass('show');
    $.fn.zato.in_app_updates.updateProgress('download', 'processing', 'Downloading latest updates...');

    $.ajax({
        url: '/zato/updates/download',
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        success: function(response) {
            $.fn.zato.in_app_updates.updateProgress('download', 'completed', 'Download complete');

            $('#progress-install').removeClass('hidden');
            $.fn.zato.in_app_updates.runInstallSteps(button);
        },
        error: function(xhr) {
            let errorMsg = 'Download failed';
            try {
                const response = JSON.parse(xhr.responseText);
                errorMsg = response.error || errorMsg;
            } catch(e) {
                errorMsg = xhr.responseText || errorMsg;
            }

            $.fn.zato.in_app_updates.updateProgress('download', 'error', errorMsg);
            button.prop('disabled', false);
        }
    });
};

$.fn.zato.in_app_updates.runInstallSteps = function(button) {
    const steps = [
        {url: '/zato/updates/install', text: 'Installing updates'},
        {url: '/zato/updates/restart-scheduler', text: 'Restarting scheduler'},
        {url: '/zato/updates/restart-server', text: 'Restarting server'},
        {url: '/zato/updates/restart-proxy', text: 'Restarting proxy'},
        {url: '/zato/updates/restart-dashboard', text: 'Restarting dashboard'}
    ];

    let currentStep = 0;
    const totalSteps = steps.length;

    const runNextStep = function() {
        if (currentStep >= totalSteps) {
            $.fn.zato.in_app_updates.updateProgress('install', 'completed', 'Installation complete');

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
            return;
        }

        const step = steps[currentStep];
        const stepNumber = currentStep + 1;
        const progressText = stepNumber + ' / ' + totalSteps;
        const statusText = step.text + '...';

        $.fn.zato.in_app_updates.updateProgress('install', 'processing', progressText, statusText);

        $.ajax({
            url: step.url,
            type: 'POST',
            headers: {
                'X-CSRFToken': $.cookie('csrftoken')
            },
            success: function(response) {
                currentStep++;
                runNextStep();
            },
            error: function(xhr) {
                let errorMsg = step.text + ' failed';
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMsg = response.error || errorMsg;
                } catch(e) {
                    errorMsg = xhr.responseText || errorMsg;
                }

                $.fn.zato.in_app_updates.updateProgress('install', 'error', progressText, errorMsg);
                button.prop('disabled', false);
            }
        });
    };

    runNextStep();
};

$.fn.zato.in_app_updates.updateProgress = function(step, status, message, statusText) {
    const item = $('#progress-' + step);
    const icon = item.find('.progress-icon');
    const text = item.find('.progress-text');
    const copyButton = item.find('.download-error-copy');

    const displayMessage = statusText ? '<span style="color: #000; font-weight: 600;">' + message + '</span> <span style="color: var(--text-muted);">' + statusText + '</span>' : message;

    if (status === 'processing') {
        icon.addClass('spinner').removeClass('completed error').html('<img src="/static/gfx/spinner.svg" style="animation: spin 0.5s linear infinite; width: 28px; height: 28px; filter: brightness(0) saturate(100%) invert(8%) sepia(91%) saturate(2593%) hue-rotate(194deg) brightness(96%) contrast(99%);">');
        item.removeClass('error-state');
        if (copyButton.length) {
            copyButton.hide();
        }
    } else if (status === 'completed') {
        icon.removeClass('spinner error').addClass('completed').text('✓');
        item.removeClass('error-state');
        if (copyButton.length) {
            copyButton.hide();
        }
    } else if (status === 'error') {
        icon.removeClass('spinner completed').addClass('error').text('✗');
        item.addClass('error-state');
        if (copyButton.length) {
            copyButton.show();
        }
    }

    text.html(displayMessage);
};

$(document).ready(function() {
    $.fn.zato.in_app_updates.init();
});
