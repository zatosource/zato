(function($) {

var shell = $.fn.zato.outgoing.sftp.command_shell;

shell.config = {
    formSelector: '#sftp-shell-form',
    connectionSelector: '#sftp-shell-conn-select',
    tabSelector: '.sftp-shell-card .dashboard-tab',
    panelPrefix: 'sftp-shell-tab-panel-',
    defaultTab: 'stdout',
    errorTab: 'stderr',
    emptyOutput: '(None)',
    runningMessage: 'Running ..',
    okMessage: 'Done',
    okStatusClass: 'sftp-shell-status-ok',
    errorStatusClass: 'sftp-shell-status-error',
    statusClearMs: 4000
};

shell._tabHandle = null;
shell._statusTimer = null;

// ////////////////////////////////////////////////////////////////////////
// Status message
// ////////////////////////////////////////////////////////////////////////

shell.setStatus = function(text, statusClass) {
    var config = shell.config;
    var $status = $('#sftp-shell-status');

    $status.text(text).removeClass(config.okStatusClass + ' ' + config.errorStatusClass);

    if (statusClass) {
        $status.addClass(statusClass);
    }

    if (shell._statusTimer) {
        clearTimeout(shell._statusTimer);
        shell._statusTimer = null;
    }

    // Keep an error on screen, everything else fades out on its own.
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
    $('#sftp-shell-' + name).text(text);

    // A command's output ends in a newline, which is not a line of its own.
    var lineCount = 0;
    var trimmed = text.replace(/\s+$/, '');

    if (trimmed && trimmed !== shell.config.emptyOutput) {
        lineCount = trimmed.split('\n').length;
    }

    $('#sftp-shell-' + name + '-lines').text(lineCount);
};

shell.clearOutput = function() {
    shell.setOutput('stdout', '');
    shell.setOutput('stderr', '');
    $('#sftp-shell-timing').prop('hidden', true).text('');
};

// ////////////////////////////////////////////////////////////////////////
// Running a command
// ////////////////////////////////////////////////////////////////////////

shell.onSuccess = function(data) {
    var config = shell.config;

    shell.setOutput('stdout', data.stdout);
    shell.setOutput('stderr', data.stderr);

    $('#sftp-shell-timing').prop('hidden', false).text(data.response_time + ' (#' + data.command_no + ')');

    if (data.is_ok) {
        shell.setStatus(config.okMessage, config.okStatusClass);
    }
    else {
        shell.setStatus(data.error_message, config.errorStatusClass);

        // A command that failed says why on stderr, so that is what the reader needs to see.
        shell._tabHandle.set_tab(config.errorTab, true);
    }
};

shell.onError = function(xhr) {
    shell.setOutput('stdout', '');
    shell.setOutput('stderr', xhr.responseText);

    // The response body is what the request failed on, which is more use than the status line's `Internal Server Error`.
    shell.setStatus(xhr.responseText, shell.config.errorStatusClass);
    shell._tabHandle.set_tab(shell.config.errorTab, true);
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
        default_tab: config.defaultTab
    });

    $(config.formSelector).submit(function() {
        shell.run();
        return false;
    });

    // Each option's value is the URL of that connection's own command shell.
    $(config.connectionSelector).change(function() {
        window.location.href = this.value;
    });

    $('#sftp-shell-clear').click(function() {
        shell.clearOutput();
        shell.setStatus('', null);
    });

    // .. nothing has run yet, so both panes start empty ..
    shell.clearOutput();

    // .. and fade in.
    kit.reveal();
};

})(jQuery);
