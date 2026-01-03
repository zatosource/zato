$.fn.zato.updates.init = function() {
    const headerBadge = document.getElementById('update-status-badge');
    if (headerBadge) {
        headerBadge.style.animation = 'none';
    }

    $('#check-button').on('click', $.fn.zato.updates.handleCheckForUpdates);
    $('.copy-icon').on('click', $.fn.zato.settings.handleCopyIcon);
    $(document).on('click', '.info-message', $.fn.zato.updates.handleCopyUpgradeInfo);
    $('#update-button').on('click', $.fn.zato.updates.handleUpdateClick);
    $('#auto-restart').on('change', $.fn.zato.updates.handleAutoUpdateToggle);
    $('#update-frequency').on('change', $.fn.zato.updates.handleFrequencyChange);
    $('#config-save-button').on('click', $.fn.zato.updates.handleSaveSchedule);

    $.fn.zato.updates.displayTimezone();
    $.fn.zato.updates.loadSchedule();
    $.fn.zato.updates.fetchLatestVersion();
    $.fn.zato.updates.startAuditLogRefresh();
    $.fn.zato.updates.initTimestampTooltips();

    const tours = {};

    tours.versionInfo = {};
    tours.versionInfo.trigger = '#version-info-help';
    tours.versionInfo.steps = [];

    tours.versionInfo.steps[0] = {};
    tours.versionInfo.steps[0].popover = {};
    tours.versionInfo.steps[0].popover.title = 'Version info';
    tours.versionInfo.steps[0].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.';

    tours.versionInfo.steps[1] = {};
    tours.versionInfo.steps[1].element = '#check-button';
    tours.versionInfo.steps[1].popover = {};
    tours.versionInfo.steps[1].popover.title = 'Check for updates';
    tours.versionInfo.steps[1].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.';

    tours.versionInfo.steps[2] = {};
    tours.versionInfo.steps[2].element = '#update-button';
    tours.versionInfo.steps[2].popover = {};
    tours.versionInfo.steps[2].popover.title = 'Install updates';
    tours.versionInfo.steps[2].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.<br><br>' +
        'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.';

    tours.config = {};
    tours.config.trigger = '#auto-update-help';
    tours.config.steps = [];

    tours.config.steps[0] = {};
    tours.config.steps[0].popover = {};
    tours.config.steps[0].popover.title = 'Config';
    tours.config.steps[0].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.';

    tours.config.steps[1] = {};
    tours.config.steps[1].element = '.config-item';
    tours.config.steps[1].popover = {};
    tours.config.steps[1].popover.title = 'Auto-update';
    tours.config.steps[1].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.<br><br>' +
        'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.';

    tours.logs = {};
    tours.logs.trigger = '#logs-help';
    tours.logs.steps = [];

    tours.logs.steps[0] = {};
    tours.logs.steps[0].popover = {};
    tours.logs.steps[0].popover.title = 'Logs';
    tours.logs.steps[0].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.';

    tours.logs.steps[1] = {};
    tours.logs.steps[1].element = '.dashboard-link-item';
    tours.logs.steps[1].popover = {};
    tours.logs.steps[1].popover.title = 'Download logs';
    tours.logs.steps[1].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.<br><br>' +
        'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.';

    $.fn.zato.settings.initDriverTours(Object.values(tours));

    $.fn.zato.settings.initToggleLabelClick('.config-item:first .config-label', '#auto-restart');
};

$.fn.zato.updates.fetchLatestVersion = function(showUpdatesFound) {
    const latestVersionEl = $('#latest-version');
    const copyIcon = latestVersionEl.siblings('.copy-icon');
    const currentVersion = $('#current-version').text();
    latestVersionEl.html('<img src="/static/gfx/spinner.svg" class="info-spinner">Checking...');
    copyIcon.addClass('hidden');

    $.ajax({
        url: '/zato/updates/check-latest-version',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                latestVersionEl.text(response.version);
                copyIcon.removeClass('hidden');

                if (showUpdatesFound) {
                    const updatesFound = $('.status-message');
                    updatesFound.addClass('show');
                    setTimeout(() => {
                        updatesFound.addClass('fade');
                        setTimeout(() => {
                            updatesFound.removeClass('show fade');
                        }, 500);
                    }, 1500);
                }

                const upToDateBadge = $('#up-to-date-badge');
                if (response.version !== currentVersion) {
                    upToDateBadge.removeClass('success').addClass('error').text('No');

                    const headerBadge = document.getElementById('update-status-badge');
                    const headerText = document.getElementById('update-status-text');
                    if (headerBadge && headerText) {
                        headerText.textContent = '⭐ Updates available';
                        headerBadge.classList.remove('white');
                        headerBadge.classList.add('with-shine', 'loaded');
                    }

                    setTimeout(() => {
                        latestVersionEl.addClass('pulsate');
                    }, 50);

                    setTimeout(() => {
                        latestVersionEl.removeClass('pulsate');
                    }, 1600);
                } else {
                    upToDateBadge.removeClass('error').addClass('success').text('Yes');

                    const headerBadge = document.getElementById('update-status-badge');
                    const headerText = document.getElementById('update-status-text');
                    if (headerBadge && headerText) {
                        headerText.textContent = 'Up to date';
                        headerBadge.classList.remove('with-shine');
                        headerBadge.classList.add('loaded');
                    }
                }
            }

            $.fn.zato.settings.deactivateSpinner('.button-spinner');
        },
        error: function(xhr, status, error) {
            latestVersionEl.text('Error loading version');
            $.fn.zato.settings.deactivateSpinner('.button-spinner');
        }
    });
};

$.fn.zato.updates.handleCheckForUpdates = function() {
    const upToDateBadge = $('#up-to-date-badge');
    upToDateBadge.removeClass('success error').text('Checking...');

    $.fn.zato.settings.activateSpinner('.button-spinner');
    $.fn.zato.updates.fetchLatestVersion(false);
};

$.fn.zato.updates.handleCopyUpgradeInfo = function(e) {
    const text = $(this).text().trim();
    $.fn.zato.settings.copyToClipboard(text, e);
};

$.fn.zato.updates.handleAutoUpdateToggle = function() {
    const isEnabled = $(this).is(':checked');

    console.log('Auto-update toggle changed, enabled:', isEnabled);

    if (isEnabled) {
        console.log('Showing schedule frequency');
        $('#schedule-frequency').removeClass('hidden');
        $('.save-button-container').css('display', 'flex');
        $.fn.zato.updates.updateScheduleOptions();
    } else {
        console.log('Hiding all schedule fields');
        $('#schedule-frequency').addClass('hidden');
        $('#schedule-day').addClass('hidden');
        $('#schedule-week').addClass('hidden');
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

$.fn.zato.updates.handleFrequencyChange = function() {
    $.fn.zato.updates.updateScheduleOptions();
};

$.fn.zato.updates.updateScheduleOptions = function() {
    const frequency = $('#update-frequency').val();

    console.log('updateScheduleOptions called, frequency:', frequency);

    $('#schedule-day').addClass('hidden');
    $('#schedule-week').addClass('hidden');
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
        console.log('Monthly selected - showing week, day, and time');
        $('#schedule-week').removeClass('hidden');
        $('#schedule-day').removeClass('hidden');
        $('#schedule-time').removeClass('hidden');
    }

    console.log('schedule-day hidden:', $('#schedule-day').hasClass('hidden'));
    console.log('schedule-week hidden:', $('#schedule-week').hasClass('hidden'));
    console.log('schedule-time hidden:', $('#schedule-time').hasClass('hidden'));
};

$.fn.zato.updates.loadSchedule = function() {
    $.ajax({
        url: '/zato/updates/load-schedule',
        type: 'GET',
        success: function(response) {
            if (response.success && response.schedule) {
                $('#auto-restart').prop('checked', true);
                $('#update-frequency').val(response.schedule.frequency);
                $('#update-day').val(response.schedule.day);
                $('#update-week').val(response.schedule.week);
                $('#update-time').val(response.schedule.time);

                $('#schedule-frequency').removeClass('hidden');
                $('.save-button-container').css('display', 'flex');
                $.fn.zato.updates.updateScheduleOptions();
            }
        }
    });
};

$.fn.zato.updates.displayTimezone = function() {
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    $('#timezone-display').text('(' + timezone + ')');
};

$.fn.zato.updates.handleSaveSchedule = function() {
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const scheduleData = {
        enabled: true,
        frequency: $('#update-frequency').val(),
        day: $('#update-day').val(),
        week: $('#update-week').val(),
        time: $('#update-time').val(),
        timezone: timezone
    };

    $.fn.zato.settings.saveWithSpinner({
        url: '/zato/updates/save-schedule',
        data: scheduleData
    });
};

$.fn.zato.updates.handleUpdateClick = function() {
    const button = $(this);
    button.prop('disabled', true);

    $('#progress-download').removeClass('hidden error-state');
    $('#progress-install').addClass('hidden').removeClass('error-state');
    $('#progress-install .info-message').removeClass('show');
    $.fn.zato.settings.updateProgress('download', 'processing', 'Downloading updates...');

    $.ajax({
        url: '/zato/updates/download-and-install',
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        success: function(response) {
            $.fn.zato.settings.updateProgress('download', 'completed', 'Download complete');

            $('#progress-install').removeClass('hidden');
            $.fn.zato.updates.runRestartSteps(button, response.version_to);
        },
        error: function(xhr) {
            console.error('Update error, status:', xhr.status);
            console.error('Response text:', xhr.responseText);

            let errorMsg = 'Download and install failed';
            let fullError = errorMsg;
            try {
                const response = JSON.parse(xhr.responseText);
                console.error('Parsed response:', JSON.stringify(response, null, 2));

                errorMsg = response.error || errorMsg;
                fullError = errorMsg;

                if (response.stdout) {
                    fullError += '\n\nStdout:\n' + response.stdout;
                }
                if (response.stderr) {
                    fullError += '\n\nStderr:\n' + response.stderr;
                }
                if (response.restart_results) {
                    fullError += '\n\nRestart results:\n' + JSON.stringify(response.restart_results, null, 2);
                }
            } catch(e) {
                console.error('Failed to parse response:', JSON.stringify(e));
                errorMsg = xhr.responseText || errorMsg;
                fullError = errorMsg;
            }

            console.error('Final error message:', errorMsg);
            console.error('Full error:', fullError);

            $('#progress-download').data('full-error', fullError);
            $.fn.zato.settings.updateProgress('download', 'error', errorMsg);
            button.prop('disabled', false);
        }
    });
};

$.fn.zato.updates.runRestartSteps = function(button, latestVersion) {
    const config = {};
    config.progressKey = 'install';
    config.button = button;
    config.pollUrl = '/zato/updates/';
    config.completedText = 'Installation complete';
    config.completionBadgeSelector = '#progress-install .info-message';
    config.baseUrl = '/zato/updates';

    config.completionBadgeText = '⭐ Updated to ' + latestVersion;

    config.onAllComplete = function() {
        $('#current-version').text(latestVersion);

        const upToDateBadge = $('#up-to-date-badge');
        upToDateBadge.removeClass('error').addClass('success').text('Yes');

        const headerBadge = document.getElementById('update-status-badge');
        const headerText = document.getElementById('update-status-text');
        if (headerBadge && headerText) {
            headerBadge.classList.remove('with-shine', 'white');
            headerText.textContent = 'Up to date';
        }

        $.ajax({
            url: '/zato/updates/get-latest-audit-entry',
            type: 'GET',
            success: function(response) {
                if (response.success && response.entry) {
                    response.entry.time_ago = 'A moment ago';
                    const newEntryHtml = $.fn.zato.updates.renderAuditLogEntry(response.entry, 'fade-in');

                    const auditLogList = $('.audit-log-list');
                    if (auditLogList.length) {
                        const emptyMessage = auditLogList.find('.audit-log-empty');
                        if (emptyMessage.length) {
                            emptyMessage.remove();
                        }
                        auditLogList.prepend(newEntryHtml);
                        const entries = auditLogList.children('.audit-log-entry');
                        if (entries.length > 3) {
                            entries.last().remove();
                        }

                        auditLogList.siblings('.links-row').css('display', '');
                    }
                }
            }
        });
    };

    $.fn.zato.settings.executeSteps(config);
};


$.fn.zato.updates.renderAuditLogEntry = function(entry, extraClass) {
    const template = document.getElementById('audit-log-entry-template');
    const clone = template.content.cloneNode(true);
    const entryDiv = clone.querySelector('.audit-log-entry');
    
    if (extraClass) {
        entryDiv.classList.add(extraClass);
    }
    
    const timeSpan = clone.querySelector('.audit-log-time');
    timeSpan.setAttribute('data-timestamp', entry.timestamp);
    timeSpan.textContent = entry.time_ago;
    
    clone.querySelector('.audit-log-type').textContent = entry.type;
    clone.querySelector('.audit-log-version-from').textContent = entry.version_from;
    clone.querySelector('.audit-log-version-to').textContent = entry.version_to;
    
    return clone;
};

$.fn.zato.updates.initTimestampTooltips = function() {
    $('.audit-log-time').each(function() {
        const elem = this;
        const timestamp = $(elem).data('timestamp');
        if (timestamp) {
            const date = new Date(timestamp);
            const formattedDate = date.toLocaleString();

            tippy(elem, {
                content: formattedDate,
                allowHTML: false,
                theme: 'dark',
                trigger: 'mouseenter',
                placement: 'top',
                arrow: true,
                interactive: false,
                inertia: true,
                role: 'tooltip'
            });
        }
    });
};

$.fn.zato.updates.startAuditLogRefresh = function() {
    const refreshAuditLog = function() {
        $.ajax({
            url: '/zato/updates/get-audit-log-refresh',
            type: 'GET',
            success: function(response) {
                if (response.success && response.entries && response.entries.length > 0) {
                    const auditLogList = $('.audit-log-list');
                    if (auditLogList.length) {
                        auditLogList.empty();
                        for (const entry of response.entries) {
                            const entryFragment = $.fn.zato.updates.renderAuditLogEntry(entry);
                            auditLogList.append(entryFragment);
                        }
                        $.fn.zato.updates.initTimestampTooltips();
                    }
                }
            }
        });
    };

    setInterval(refreshAuditLog, 60000);
};

$(document).ready(function() {
    $.fn.zato.updates.init();
});
