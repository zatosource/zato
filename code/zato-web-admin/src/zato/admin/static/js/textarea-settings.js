$.fn.zato.textarea_settings = {};

$.fn.zato.textarea_settings.init = function(config) {

    var state = {};
    state.config = config;
    state.initialContent = $('#' + config.textareaId).val();

    $('#check-button').on('click', function() {
        $.fn.zato.textarea_settings.handleTest(state);
    });

    $('#update-button').on('click', function() {
        $.fn.zato.textarea_settings.handleSave(state);
    });

    if (config.tourSteps) {
        var tours = {};
        tours.main = {};
        tours.main.trigger = '#version-info-help';
        tours.main.steps = config.tourSteps;
        $.fn.zato.settings.initDriverTours(Object.values(tours));
    }

    $.fn.zato.textarea_settings.setupHoverMatching(config);

    $('#allow-delete-label').on('click', function() {
        var toggle = $('#allow-delete-toggle');
        toggle.prop('checked', !toggle.prop('checked'));
    });

    $('#restore-initial-label').on('click', function(e) {
        e.preventDefault();
        $('#' + config.textareaId).val(state.initialContent);
        $('.test-results').remove();
        var statusMessage = $('.status-message.test-success');
        statusMessage.removeClass('show fade test-error-message').text('OK');

        var elem = this;
        if (elem._tippy) {
            elem._tippy.destroy();
        }
        var tip = tippy(elem, {
            content: 'OK, restored initial values',
            trigger: 'manual',
            placement: 'top',
            arrow: true,
            theme: 'dark',
        });
        tip.show();
        setTimeout(function() {
            tip.hide();
            setTimeout(function() { tip.destroy(); }, 200);
        }, 1000);
    });
};

$.fn.zato.textarea_settings.showTestResults = function(results, response, config) {
    var changeCount = response.change_count || 0;
    var deleteCount = response.delete_count || 0;
    var statusMessage = $('.status-message.test-success');

    var errors = [];
    var changes = [];
    var deletes = [];
    for (var i = 0; i < results.length; i++) {
        if (results[i].status === 'error') {
            errors.push(results[i]);
        } else if (results[i].status === 'delete') {
            deletes.push(results[i]);
        } else {
            changes.push(results[i]);
        }
    }

    statusMessage.removeClass('test-error-message');

    var existingResults = $('.test-results');
    if (existingResults.length) {
        existingResults.remove();
    }

    if (errors.length === 0 && changes.length === 0 && deleteCount === 0) {
        if (config.useCustomStatus) {
            statusMessage.text('No changes');
        }
        return;
    }

    if (config.useCustomStatus) {
        var htmlParts = [];
        if (changes.length > 0) {
            var changeNoun = changes.length === 1 ? 'change' : 'changes';
            htmlParts.push(changes.length + ' ' + changeNoun);
        }
        if (deleteCount > 0) {
            var deleteNoun = deleteCount === 1 ? 'deletion' : 'deletions';
            htmlParts.push('<span class="status-delete-text">' + deleteCount + ' ' + deleteNoun + '</span>');
        }
        if (errors.length > 0) {
            var errorNoun = errors.length === 1 ? 'error' : 'errors';
            htmlParts.push('<span class="status-error-text">' + errors.length + ' ' + errorNoun + '</span>');
        }
        statusMessage.html(htmlParts.join(', '));
    }

    var showItems = changes.concat(deletes).concat(errors);
    if (showItems.length > 0) {
        var labelKey = config.resultLabelKey || 'label';
        var html = '<div class="test-results">';
        for (var i = 0; i < showItems.length; i++) {
            var result = showItems[i];
            var statusClass, statusText;
            if (result.status === 'error') {
                statusClass = 'error';
                statusText = 'Error';
            } else if (result.status === 'delete') {
                statusClass = 'delete';
                statusText = 'Delete';
            } else if (result.status === 'new') {
                statusClass = 'ok';
                statusText = 'New';
            } else if (result.status === 'changed') {
                statusClass = 'ok';
                statusText = 'Changed';
            } else if (result.status === 'skipped') {
                statusClass = 'skipped';
                statusText = 'Skipped';
            } else {
                statusClass = 'ok';
                statusText = 'OK';
            }
            var itemLabel = result[labelKey] || '';
            html += '<div class="result-item">';
            html += '<span class="result-package">' + $.fn.zato.textarea_settings.escapeHtml(itemLabel) + '</span>';
            html += ' <span class="result-status-cell"><span class="result-status ' + statusClass + '">' + statusText + '</span></span>';
            if (config.renderMessage) {
                html += ' ' + config.renderMessage(result);
            } else {
                html += ' <span class="result-message">' + $.fn.zato.textarea_settings.escapeHtml(result.message || '') + '</span>';
            }
            html += '</div>';
        }
        html += '</div>';
        $('.button-container').after(html);
    }
};

$.fn.zato.textarea_settings.handleTest = function(state) {
    var config = state.config;

    $('#progress-test').addClass('hidden').removeClass('error-state');
    $('#progress-configure').addClass('hidden').removeClass('error-state');
    $('#progress-scheduler').addClass('hidden');
    $('#progress-server').addClass('hidden');
    $('#progress-proxy').addClass('hidden');
    $('#progress-dashboard').addClass('hidden');
    $('.test-results').remove();

    var statusMessage = $('.status-message.test-success');
    statusMessage.removeClass('show fade test-error-message').text('OK');

    $.fn.zato.settings.activateSpinner('.button-spinner');

    $.ajax({
        url: config.testUrl,
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify(config.buildTestPayload()),
        contentType: 'application/json',
        success: function(response) {
            $.fn.zato.settings.deactivateSpinner('.button-spinner');
            statusMessage.addClass('show');

            if (config.showTestResults) {
                config.showTestResults(response.results, response, config);
            } else {
                $.fn.zato.textarea_settings.showTestResults(response.results, response, config);
            }

            if (!config.useCustomStatus) {
                setTimeout(function() {
                    statusMessage.addClass('fade');
                    setTimeout(function() {
                        statusMessage.removeClass('show fade test-error-message');
                        statusMessage.text('OK');
                    }, 500);
                }, 3000);
            }
        },
        error: function(xhr) {
            $.fn.zato.settings.deactivateSpinner('.button-spinner');

            var errorMsg = 'Test failed';
            var results = [];
            var response = null;
            try {
                response = JSON.parse(xhr.responseText);
                if (response.error) {
                    errorMsg = response.error;
                }
                if (response.results) {
                    results = response.results;
                }
            } catch(e) {
                errorMsg = xhr.responseText || errorMsg;
            }

            if (config.useCustomStatus && response) {
                statusMessage.addClass('show');
                if (config.showTestResults) {
                    config.showTestResults(results, response, config);
                } else {
                    $.fn.zato.textarea_settings.showTestResults(results, response, config);
                }
            } else if (results.length) {
                if (config.showTestResults) {
                    config.showTestResults(results, response, config);
                } else {
                    $.fn.zato.textarea_settings.showTestResults(results, response, config);
                }

                setTimeout(function() {
                    statusMessage.addClass('fade');
                    setTimeout(function() {
                        statusMessage.removeClass('show fade test-error-message');
                        statusMessage.text('OK');
                    }, 3000);
                }, 3000);
            }
        }
    });
};

$.fn.zato.textarea_settings.handleSave = function(state) {
    var config = state.config;
    var content = $('#' + config.textareaId).val().trim();

    if (!content) {
        return;
    }

    var button = $('#update-button');
    button.prop('disabled', true);

    $('#progress-test').addClass('hidden').removeClass('error-state');
    $('#progress-configure').addClass('hidden').removeClass('error-state');
    $('#progress-scheduler').addClass('hidden');
    $('#progress-server').addClass('hidden');
    $('#progress-proxy').addClass('hidden');
    $('#progress-dashboard').addClass('hidden');
    $('.test-results').remove();

    $('#progress-configure').removeClass('hidden error-state');
    $('#progress-install').addClass('hidden').removeClass('error-state');
    $('#progress-install .info-message').removeClass('show');
    $.fn.zato.settings.updateProgress('configure', 'processing', config.saveProgressLabel || 'Saving...');

    $.ajax({
        url: config.saveUrl,
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify(config.buildSavePayload()),
        contentType: 'application/json',
        success: function(response) {
            var doneText = config.saveSuccessLabel || 'Saved';
            $.fn.zato.settings.updateProgress('configure', 'completed', doneText);

            if (config.showRestartSteps) {
                $('#progress-install').removeClass('hidden');
                $.fn.zato.textarea_settings.runRestartSteps(state, button);
            } else {
                button.prop('disabled', false);
            }

            if (config.onSaveSuccess) {
                config.onSaveSuccess(response);
            }
        },
        error: function(xhr) {
            var errorMsg = config.saveErrorLabel || 'Save failed';
            var fullError = errorMsg;
            try {
                var response = JSON.parse(xhr.responseText);
                errorMsg = response.error || errorMsg;
                fullError = errorMsg;
            } catch(e) {
                errorMsg = xhr.responseText || errorMsg;
                fullError = errorMsg;
            }

            $('#progress-configure').data('full-error', fullError);
            $.fn.zato.settings.updateProgress('configure', 'error', errorMsg);
            button.prop('disabled', false);
        }
    });
};

$.fn.zato.textarea_settings.runRestartSteps = function(state, button) {
    var config = state.config;

    var stepConfig = {};
    stepConfig.progressKey = 'install';
    stepConfig.button = button;
    stepConfig.pollUrl = config.apiPrefix;
    stepConfig.completedText = config.restartCompletedText || 'All components restarted';
    stepConfig.completionBadgeSelector = '#progress-install .info-message';
    stepConfig.baseUrl = config.apiPrefix.replace(/\/$/, '');
    stepConfig.completionBadgeText = config.restartBadgeText || 'Done';

    $.fn.zato.settings.executeSteps(stepConfig);
};

$.fn.zato.textarea_settings.escapeHtml = function(text) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
};

$.fn.zato.textarea_settings.setupHoverMatching = function(config) {
    var textarea = document.getElementById(config.textareaId);
    if (!textarea) return;

    var container = textarea.parentNode;
    var highlight = document.createElement('div');
    highlight.className = 'textarea-line-highlight';
    container.appendChild(highlight);

    var lineHeight = parseFloat(window.getComputedStyle(textarea).lineHeight) || 19.5;
    var paddingTop = parseFloat(window.getComputedStyle(textarea).paddingTop) || 12;

    var getKeyFromLine = config.getKeyFromLine || function(lineText) {
        var trimmed = lineText.trim();
        if (!trimmed || trimmed.startsWith('#')) return null;
        var eqIdx = trimmed.indexOf('=');
        if (eqIdx > 0) return trimmed.substring(0, eqIdx).trim();
        return trimmed;
    };

    var getLineAtY = function(y) {
        var rect = textarea.getBoundingClientRect();
        var relY = y - rect.top - paddingTop + textarea.scrollTop;
        return Math.floor(relY / lineHeight);
    };

    var getLines = function() {
        return textarea.value.split('\n');
    };

    textarea.addEventListener('mousemove', function(e) {
        var lineIdx = getLineAtY(e.clientY);
        var lines = getLines();
        if (lineIdx < 0 || lineIdx >= lines.length) {
            highlight.style.display = 'none';
            $('.test-results .result-item').removeClass('result-highlight');
            return;
        }

        var topOffset = paddingTop + (lineIdx * lineHeight) - textarea.scrollTop;
        highlight.style.display = 'block';
        highlight.style.top = topOffset + 'px';

        var key = getKeyFromLine(lines[lineIdx]);
        $('.test-results .result-item').removeClass('result-highlight');
        if (key) {
            $('.test-results .result-item').each(function() {
                var label = $(this).find('.result-package').text();
                if (label === key) {
                    $(this).addClass('result-highlight');
                }
            });
        }
    });

    textarea.addEventListener('mouseleave', function() {
        highlight.style.display = 'none';
        $('.test-results .result-item').removeClass('result-highlight');
    });

    textarea.addEventListener('scroll', function() {
        highlight.style.display = 'none';
    });

    $(document).on('mouseenter', '.test-results .result-item', function() {
        var key = $(this).find('.result-package').text();
        if (!key) return;

        var lines = getLines();
        for (var i = 0; i < lines.length; i++) {
            var lineKey = getKeyFromLine(lines[i]);
            if (lineKey === key) {
                var topOffset = paddingTop + (i * lineHeight) - textarea.scrollTop;
                highlight.style.display = 'block';
                highlight.style.top = topOffset + 'px';
                return;
            }
        }
    });

    $(document).on('mouseleave', '.test-results .result-item', function() {
        highlight.style.display = 'none';
    });
};
