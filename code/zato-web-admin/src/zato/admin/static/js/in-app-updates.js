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

    $.fn.zato.in_app_updates.displayTimezone();
    $.fn.zato.in_app_updates.loadSchedule();
    $.fn.zato.in_app_updates.fetchLatestVersion();
    $.fn.zato.in_app_updates.startAuditLogRefresh();
    $.fn.zato.in_app_updates.initTimestampTooltips();

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
            element: '.config-item',
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

    $('.config-item:first .config-label').on('click', function() {
        const checkbox = $('#auto-restart');
        checkbox.prop('checked', !checkbox.prop('checked'));
    });
};

$.fn.zato.in_app_updates.fetchLatestVersion = function(showUpdatesFound) {
    const latestVersionEl = $('#latest-version');
    const copyIcon = latestVersionEl.siblings('.copy-icon');
    const currentVersion = $('#current-version').text();

    latestVersionEl.html('<img src="/static/gfx/spinner.svg" class="version-spinner">Checking...');
    copyIcon.addClass('hidden');

    $.ajax({
        url: '/zato/updates/check-latest-version',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                latestVersionEl.text(response.version);
                copyIcon.removeClass('hidden');
                
                $('.upgrade-info').text('⭐ Updated to ' + response.version);

                if (showUpdatesFound) {
                    const updatesFound = $('.updates-found');
                    updatesFound.addClass('show');
                    setTimeout(() => {
                        updatesFound.addClass('fade');
                        setTimeout(() => {
                            updatesFound.removeClass('show fade');
                        }, 500);
                    }, 1500);
                }

                
                if (response.version !== currentVersion) {
                    localStorage.setItem('zato_updates_available', 'true');
                    
                    const headerBadge = window.parent.document.getElementById('update-status-badge');
                    const headerText = window.parent.document.getElementById('update-status-text');
                    if (headerBadge && headerText) {
                        headerText.textContent = '⭐ Updates available';
                        headerBadge.classList.add('with-shine');
                        headerBadge.classList.add('loaded');
                    }
                    
                    setTimeout(() => {
                        latestVersionEl.addClass('pulsate');
                    }, 50);

                    setTimeout(() => {
                        latestVersionEl.removeClass('pulsate');
                    }, 1600);
                } else {
                    localStorage.setItem('zato_updates_available', 'false');
                    
                    const headerBadge = window.parent.document.getElementById('update-status-badge');
                    const headerText = window.parent.document.getElementById('update-status-text');
                    if (headerBadge && headerText) {
                        headerText.textContent = 'Up to date';
                        headerBadge.classList.remove('with-shine');
                        headerBadge.classList.add('loaded');
                    }
                }
            }
        },
        error: function() {
            latestVersionEl.text('Error loading version');
        }
    });
};

$.fn.zato.in_app_updates.handleCheckForUpdates = function() {
    $.fn.zato.in_app_updates.fetchLatestVersion(false);
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
    const targetElement = $('#' + targetId);
    
    const fullError = targetElement.closest('#progress-download').data('full-error');
    const text = fullError || targetElement.text();
    
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

$.fn.zato.in_app_updates.handleFrequencyChange = function() {
    $.fn.zato.in_app_updates.updateScheduleOptions();
};

$.fn.zato.in_app_updates.updateScheduleOptions = function() {
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

$.fn.zato.in_app_updates.loadSchedule = function() {
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
                $.fn.zato.in_app_updates.updateScheduleOptions();
            }
        }
    });
};

$.fn.zato.in_app_updates.displayTimezone = function() {
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    $('#timezone-display').text('(' + timezone + ')');
};

$.fn.zato.in_app_updates.handleSaveSchedule = function() {
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const scheduleData = {
        enabled: true,
        frequency: $('#update-frequency').val(),
        day: $('#update-day').val(),
        week: $('#update-week').val(),
        time: $('#update-time').val(),
        timezone: timezone
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
    $.fn.zato.in_app_updates.updateProgress('download', 'processing', 'Downloading updates...');

    $.ajax({
        url: '/zato/updates/download-and-install',
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        success: function(response) {
            $.fn.zato.in_app_updates.updateProgress('download', 'completed', 'Download complete');

            $('#progress-install').removeClass('hidden');
            $.fn.zato.in_app_updates.runRestartSteps(button);
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
            $.fn.zato.in_app_updates.updateProgress('download', 'error', errorMsg);
            button.prop('disabled', false);
        }
    });
};

$.fn.zato.in_app_updates.runRestartSteps = function(button) {
    const steps = [
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

            localStorage.setItem('zato_updates_available', 'false');

            const headerBadge = window.parent.document.getElementById('update-status-badge');
            if (headerBadge) {
                headerBadge.classList.remove('with-shine');
                headerBadge.classList.add('white');
                headerBadge.textContent = 'Up to date';
            }

            $.ajax({
                url: '/zato/updates/get-latest-audit-entry',
                type: 'GET',
                success: function(response) {
                    if (response.success && response.entry) {
                        const newEntryHtml = $.fn.zato.in_app_updates.renderAuditLogEntry(response.entry, 'fade-in');
                        
                        const auditLogList = $('.audit-log-list');
                        if (auditLogList.length) {
                            auditLogList.prepend(newEntryHtml);
                            const entries = auditLogList.children('.audit-log-entry');
                            if (entries.length > 5) {
                                entries.last().remove();
                            }
                        }
                    }
                }
            });

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
                if (step.url === '/zato/updates/restart-dashboard') {
                    let pollAttempts = 0;
                    const maxPollAttempts = 60;
                    
                    const pollDashboard = function() {
                        pollAttempts++;
                        $.ajax({
                            url: '/zato/updates/',
                            type: 'GET',
                            timeout: 2000,
                            success: function() {
                                currentStep++;
                                runNextStep();
                            },
                            error: function() {
                                if (pollAttempts < maxPollAttempts) {
                                    setTimeout(pollDashboard, 1000);
                                } else {
                                    $.fn.zato.in_app_updates.updateProgress('install', 'error', progressText, 'Dashboard did not restart');
                                    button.prop('disabled', false);
                                }
                            }
                        });
                    };
                    
                    setTimeout(pollDashboard, 2000);
                } else {
                    currentStep++;
                    setTimeout(runNextStep, 500);
                }
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

$.fn.zato.in_app_updates.renderAuditLogEntry = function(entry, extraClass) {
    const classAttr = extraClass ? `class="audit-log-entry ${extraClass}"` : 'class="audit-log-entry"';
    return `
        <div ${classAttr}>
            <div class="audit-log-header">
                <span class="audit-log-time" data-timestamp="${entry.timestamp}">${entry.time_ago}</span>
                <span class="audit-log-type">${entry.type}</span>
            </div>
            <div class="audit-log-version-row">
                <span class="audit-log-label">From:</span>
                <span class="audit-log-version">${entry.version_from}</span>
            </div>
            <div class="audit-log-version-row">
                <span class="audit-log-label">To:</span>
                <span class="audit-log-version">${entry.version_to}</span>
            </div>
        </div>
    `;
};

$.fn.zato.in_app_updates.initTimestampTooltips = function() {
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

$.fn.zato.in_app_updates.startAuditLogRefresh = function() {
    const refreshAuditLog = function() {
        $.ajax({
            url: '/zato/updates/get-audit-log-refresh',
            type: 'GET',
            success: function(response) {
                if (response.success && response.entries && response.entries.length > 0) {
                    const auditLogList = $('.audit-log-list');
                    if (auditLogList.length) {
                        let entriesHtml = '';
                        for (const entry of response.entries) {
                            entriesHtml += $.fn.zato.in_app_updates.renderAuditLogEntry(entry);
                        }
                        auditLogList.html(entriesHtml);
                        $.fn.zato.in_app_updates.initTimestampTooltips();
                    }
                }
            }
        });
    };

    setInterval(refreshAuditLog, 60000);
};

$(document).ready(function() {
    $.fn.zato.in_app_updates.init();
});
