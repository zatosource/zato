(function($) {

var shell = $.fn.zato.outgoing.fileCommandShell;

shell.config = {
    formSelector: '#file-shell-form',
    connectionSelector: '#file-shell-connection-select',
    tabSelector: '.file-shell-card .dashboard-tab',
    copySelector: '#file-shell-copy',
    copyTooltipPlacement: 'left',
    activeOutputSelector: '.file-shell-card .dashboard-tab-panel:not([hidden]) .file-shell-output',
    panelPrefix: 'file-shell-tab-panel-',
    defaultTab: 'stdout',
    errorTab: 'stderr',
    emptyOutput: '(None)',
    runningMessage: 'Running ..',
    okMessage: 'Done',
    okStatusClass: 'file-shell-status-ok',
    errorStatusClass: 'file-shell-status-error',
    statusClearMs: 4000
};

shell._tabHandle = null;
shell._statusTimer = null;

// ////////////////////////////////////////////////////////////////////////
// Status message
// ////////////////////////////////////////////////////////////////////////

shell.setStatus = function(text, statusClass) {
    var config = shell.config;
    var $status = $('#file-shell-status');

    $status.text(text).removeClass(config.okStatusClass + ' ' + config.errorStatusClass);

    if (statusClass) {
        $status.addClass(statusClass);
    }

    if (shell._statusTimer) {
        clearTimeout(shell._statusTimer);
        shell._statusTimer = null;
    }

    if (statusClass !== config.errorStatusClass) {
        shell._statusTimer = setTimeout(function() {
            $status.text('');
        }, config.statusClearMs);
    }
};

// ////////////////////////////////////////////////////////////////////////
// Output panes
// ////////////////////////////////////////////////////////////////////////

shell.setOutput = function(name, text) {
    $('#file-shell-' + name).text(text);

    // A command's output ends in a newline, which is not a line of its own.
    var lineCount = 0;
    var trimmed = text.replace(/\s+$/, '');

    if (trimmed) {
        if (trimmed !== shell.config.emptyOutput) {
            lineCount = trimmed.split('\n').length;
        }
    }

    $('#file-shell-' + name + '-lines').text(lineCount);
};

shell.clearOutput = function() {
    shell.setOutput('stdout', '');
    shell.setOutput('stderr', '');
    $('#file-shell-timing').prop('hidden', true).text('');
    shell.refreshCopy();
};

// ////////////////////////////////////////////////////////////////////////
// Copy button
// ////////////////////////////////////////////////////////////////////////

// Copy is only clickable while the pane of the open tab has something to take.
shell.refreshCopy = function() {
    var config = shell.config;
    var text = $(config.activeOutputSelector).text();

    var hasText = false;

    if (text) {
        if (text !== config.emptyOutput) {
            hasText = true;
        }
    }

    $(config.copySelector).prop('disabled', !hasText);
};

// ////////////////////////////////////////////////////////////////////////
// Running a command
// ////////////////////////////////////////////////////////////////////////

shell.onSuccess = function(data) {
    var config = shell.config;

    shell.setOutput('stdout', data.stdout);
    shell.setOutput('stderr', data.stderr);

    $('#file-shell-timing').prop('hidden', false).text(data.response_time + ' (#' + data.command_no + ')');

    if (data.is_ok) {
        shell.setStatus(config.okMessage, config.okStatusClass);
    }
    else {
        shell.setStatus(data.error_message, config.errorStatusClass);
        shell._tabHandle.set_tab(config.errorTab, true);
    }

    shell.refreshCopy();
};

shell.onError = function(xhr) {
    shell.setOutput('stdout', '');
    shell.setOutput('stderr', xhr.responseText);
    shell.setStatus(xhr.responseText, shell.config.errorStatusClass);
    shell._tabHandle.set_tab(shell.config.errorTab, true);
    shell.refreshCopy();
};

shell.run = function() {
    var config = shell.config;
    var $form = $(config.formSelector);

    shell.clearOutput();
    shell.setStatus(config.runningMessage, null);

    $.ajax({
        type: 'POST',
        url: $form.attr('action'),
        data: $form.serialize(),
        dataType: 'json',
        success: shell.onSuccess,
        error: shell.onError
    });
};

// ////////////////////////////////////////////////////////////////////////
// Initialization
// ////////////////////////////////////////////////////////////////////////

shell.init = function() {
    var config = shell.config;
    var kit = $.fn.zato.dashboard_kit;

    shell._tabHandle = kit.tabs.init({
        tab_selector: config.tabSelector,
        panel_prefix: config.panelPrefix,
        default_tab: config.defaultTab,
        on_change: shell.refreshCopy
    });

    $(config.formSelector).submit(function() {
        shell.run();
        return false;
    });

    // Each option's value is the URL of that connection's own command shell.
    $(config.connectionSelector).change(function() {
        window.location.href = this.value;
    });

    $('#file-shell-clear').click(function() {
        shell.clearOutput();
        shell.setStatus('', null);
    });

    // Copy takes the pane of whichever tab stands open.
    $(config.copySelector).click(function() {
        var text = $(config.activeOutputSelector).text();
        kit.copy_to_clipboard(this, text, config.copyTooltipPlacement);
    });

    shell.clearOutput();

    kit.reveal();
};

})(jQuery);
