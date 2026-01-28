$.fn.zato.rules = {};

$.fn.zato.rules.currentRule = null;
$.fn.zato.rules.rulesData = {};

$.fn.zato.rules.init = function() {
    $('#reload-button').on('click', $.fn.zato.rules.handleReload);
    $('#rule-select').on('change', $.fn.zato.rules.handleRuleSelect);
    $('#execute-button').on('click', $.fn.zato.rules.handleExecute);

    $.fn.zato.rules.loadRules();
};

$.fn.zato.rules.loadRules = function() {
    var containerList = $('#container-list');
    containerList.html('<div class="container-empty">Loading...</div>');

    $.ajax({
        url: '/zato/rules/get-rule-list/',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                $.fn.zato.rules.renderContainers(response.containers, response.rules);
                $.fn.zato.rules.populateRuleSelect(response.rules);
            } else {
                containerList.html('<div class="container-empty">Failed to load rules</div>');
            }
        },
        error: function() {
            containerList.html('<div class="container-empty">Error loading rules</div>');
        }
    });
};

$.fn.zato.rules.renderContainers = function(containers, rules) {
    var containerList = $('#container-list');

    if (!containers || containers.length === 0) {
        containerList.html('<div class="container-empty">No containers found</div>');
        return;
    }

    var html = '';
    for (var i = 0; i < containers.length; i++) {
        var container = containers[i];
        var containerRules = $.fn.zato.rules.getRulesForContainer(container.name, rules);

        html += '<div class="container-item">';
        html += '<div class="container-header" data-container="' + container.name + '">';
        html += '<span class="container-toggle">▶</span>';
        html += '<span class="container-name">' + container.name + '</span>';
        html += '</div>';
        html += '<div class="container-rules" data-container="' + container.name + '">';

        for (var j = 0; j < containerRules.length; j++) {
            var rule = containerRules[j];
            $.fn.zato.rules.rulesData[rule.full_name] = rule;
            html += '<div class="rule-item" data-rule="' + rule.full_name + '">' + rule.name + '</div>';
        }

        html += '</div>';
        html += '</div>';
    }

    containerList.html(html);

    $('.container-header').on('click', $.fn.zato.rules.handleContainerClick);
    $('.rule-item').on('click', $.fn.zato.rules.handleRuleClick);
};

$.fn.zato.rules.getRulesForContainer = function(containerName, rules) {
    var result = [];
    for (var i = 0; i < rules.length; i++) {
        if (rules[i].container_name === containerName) {
            result.push(rules[i]);
        }
    }
    return result;
};

$.fn.zato.rules.populateRuleSelect = function(rules) {
    var select = $('#rule-select');
    select.empty();
    select.append('<option value="">Select a rule...</option>');

    for (var i = 0; i < rules.length; i++) {
        var rule = rules[i];
        $.fn.zato.rules.rulesData[rule.full_name] = rule;
        select.append('<option value="' + rule.full_name + '">' + rule.full_name + '</option>');
    }
};

$.fn.zato.rules.handleContainerClick = function() {
    var header = $(this);
    var containerName = header.data('container');
    var rulesDiv = $('.container-rules[data-container="' + containerName + '"]');

    header.toggleClass('expanded');
    rulesDiv.toggleClass('expanded');
};

$.fn.zato.rules.handleRuleClick = function() {
    var item = $(this);
    var ruleName = item.data('rule');

    $('.rule-item').removeClass('selected');
    item.addClass('selected');

    $('#rule-select').val(ruleName);
    $.fn.zato.rules.selectRule(ruleName);
};

$.fn.zato.rules.handleRuleSelect = function() {
    var ruleName = $(this).val();
    if (ruleName) {
        $('.rule-item').removeClass('selected');
        $('.rule-item[data-rule="' + ruleName + '"]').addClass('selected');
        $.fn.zato.rules.selectRule(ruleName);
    }
};

$.fn.zato.rules.selectRule = function(ruleName) {
    $.fn.zato.rules.currentRule = ruleName;

    var rule = $.fn.zato.rules.rulesData[ruleName];
    if (rule) {
        $.fn.zato.rules.displayRuleCode(rule);
        $.fn.zato.rules.displayRuleInfo(rule);
        $.fn.zato.rules.prefillExecutionData(rule);
    } else {
        $.fn.zato.rules.loadRuleDetails(ruleName);
    }
};

$.fn.zato.rules.loadRuleDetails = function(ruleName) {
    $.ajax({
        url: '/zato/rules/get-rule/' + encodeURIComponent(ruleName) + '/',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                $.fn.zato.rules.rulesData[ruleName] = response;
                $.fn.zato.rules.displayRuleCode(response);
                $.fn.zato.rules.displayRuleInfo(response);
                $.fn.zato.rules.prefillExecutionData(response);
            }
        }
    });
};

$.fn.zato.rules.displayRuleCode = function(rule) {
    var code = $.fn.zato.rules.buildRuleSource(rule);
    var highlighted = $.fn.zato.rules.highlightCode(code);
    var lines = code.split('\n');

    var lineNumbers = '';
    for (var i = 1; i <= lines.length; i++) {
        lineNumbers += i + '\n';
    }

    $('#line-numbers').text(lineNumbers);
    $('#code-content').html(highlighted);
};

$.fn.zato.rules.buildRuleSource = function(rule) {
    var lines = [];

    lines.push('rule');
    lines.push('    ' + rule.name);

    if (rule.docs) {
        lines.push('docs');
        lines.push('    """' + rule.docs.trim() + '"""');
    }

    if (rule.defaults && Object.keys(rule.defaults).length > 0) {
        lines.push('defaults');
        var defaultKeys = Object.keys(rule.defaults);
        for (var i = 0; i < defaultKeys.length; i++) {
            var key = defaultKeys[i];
            var value = rule.defaults[key];
            lines.push('    ' + key + ' = ' + $.fn.zato.rules.formatValue(value));
        }
    }

    if (rule.when) {
        lines.push('when');
        var whenLines = rule.when.split('\n');
        for (var j = 0; j < whenLines.length; j++) {
            lines.push('    ' + whenLines[j].trim());
        }
    }

    if (rule.then && Object.keys(rule.then).length > 0) {
        lines.push('then');
        var thenKeys = Object.keys(rule.then);
        for (var k = 0; k < thenKeys.length; k++) {
            var thenKey = thenKeys[k];
            var thenValue = rule.then[thenKey];
            lines.push('    ' + thenKey + ' = ' + $.fn.zato.rules.formatValue(thenValue));
        }
    }

    return lines.join('\n');
};

$.fn.zato.rules.formatValue = function(value) {
    if (typeof value === 'string') {
        return "'" + value + "'";
    } else if (typeof value === 'boolean') {
        return value ? 'True' : 'False';
    } else if (typeof value === 'number') {
        return value.toString();
    } else if (Array.isArray(value)) {
        return JSON.stringify(value);
    } else if (typeof value === 'object' && value !== null) {
        return JSON.stringify(value);
    }
    return String(value);
};

$.fn.zato.rules.highlightCode = function(code) {
    var lines = code.split('\n');
    var result = [];

    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        var highlighted = $.fn.zato.rules.highlightLine(line);
        result.push(highlighted);
    }

    return result.join('\n');
};

$.fn.zato.rules.highlightLine = function(line) {
    var trimmed = line.trim();

    if (trimmed.startsWith('#')) {
        return '<span class="token-comment">' + $.fn.zato.rules.escapeHtml(line) + '</span>';
    }

    var keywords = ['rule', 'docs', 'defaults', 'when', 'then', 'invoke'];
    for (var i = 0; i < keywords.length; i++) {
        if (trimmed === keywords[i]) {
            return '<span class="token-keyword">' + $.fn.zato.rules.escapeHtml(line) + '</span>';
        }
    }

    var result = line;

    result = result.replace(/\b(and|or|not|in|is)\b/g, '<span class="token-operator">$1</span>');

    result = result.replace(/(True|False)/g, '<span class="token-boolean">$1</span>');

    result = result.replace(/('[^']*')/g, '<span class="token-string">$1</span>');
    result = result.replace(/("""[^]*?""")/g, '<span class="token-string">$1</span>');

    result = result.replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="token-number">$1</span>');

    result = result.replace(/(==|!=|>=|<=|>|<|=~)/g, '<span class="token-punctuation">$1</span>');

    return result;
};

$.fn.zato.rules.escapeHtml = function(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
};

$.fn.zato.rules.displayRuleInfo = function(rule) {
    var panel = $('#rule-info-panel');
    var html = '';

    html += '<div class="info-row"><span class="info-key">Name</span><span class="info-value">' + rule.name + '</span></div>';
    html += '<div class="info-row"><span class="info-key">Container</span><span class="info-value">' + rule.container_name + '</span></div>';
    html += '<div class="info-row"><span class="info-key">Full name</span><span class="info-value" title="' + rule.full_name + '">' + rule.full_name + '</span></div>';

    if (rule.defaults && Object.keys(rule.defaults).length > 0) {
        html += '<div class="info-row"><span class="info-key">Defaults</span><span class="info-value">' + Object.keys(rule.defaults).length + ' fields</span></div>';
    }

    if (rule.docs) {
        html += '<div class="info-docs">' + $.fn.zato.rules.escapeHtml(rule.docs.trim()) + '</div>';
    }

    panel.html(html);
};

$.fn.zato.rules.prefillExecutionData = function(rule) {
    var data = {};

    if (rule.defaults) {
        var keys = Object.keys(rule.defaults);
        for (var i = 0; i < keys.length; i++) {
            data[keys[i]] = rule.defaults[keys[i]];
        }
    }

    $('#execution-data').val(JSON.stringify(data, null, 2));
};

$.fn.zato.rules.handleExecute = function() {
    var ruleName = $.fn.zato.rules.currentRule;
    if (!ruleName) {
        $.fn.zato.rules.showResult('Please select a rule first', 'error');
        return;
    }

    var dataText = $('#execution-data').val().trim();
    var data = {};

    if (dataText) {
        try {
            data = JSON.parse(dataText);
        } catch (e) {
            $.fn.zato.rules.showResult('Invalid json: ' + e.message, 'error');
            return;
        }
    }

    var button = $('#execute-button');
    button.addClass('loading').prop('disabled', true);

    $.ajax({
        url: '/zato/rules/execute/',
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        contentType: 'application/json',
        data: JSON.stringify({
            rule_name: ruleName,
            data: data
        }),
        success: function(response) {
            button.removeClass('loading').prop('disabled', false);

            if (response.success) {
                if (response.matched) {
                    $.fn.zato.rules.showResult(JSON.stringify(response.result, null, 2), 'success');
                } else {
                    $.fn.zato.rules.showResult('No match - conditions not satisfied', 'no-match');
                }
            } else {
                $.fn.zato.rules.showResult(response.error || 'Execution failed', 'error');
            }
        },
        error: function(xhr) {
            button.removeClass('loading').prop('disabled', false);
            var errorMsg = 'Request failed';
            try {
                var response = JSON.parse(xhr.responseText);
                errorMsg = response.error || errorMsg;
            } catch (e) {
                errorMsg = xhr.responseText || errorMsg;
            }
            $.fn.zato.rules.showResult(errorMsg, 'error');
        }
    });
};

$.fn.zato.rules.showResult = function(text, type) {
    var container = $('#result-container');
    container.removeClass('result-success result-error result-no-match');

    if (type === 'success') {
        container.addClass('result-success');
    } else if (type === 'error') {
        container.addClass('result-error');
    } else if (type === 'no-match') {
        container.addClass('result-no-match');
    }

    container.text(text);
};

$.fn.zato.rules.handleReload = function() {
    var button = $(this);
    button.addClass('loading');

    $.ajax({
        url: '/zato/rules/reload/',
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        success: function() {
            $.fn.zato.rules.loadRules();
            button.removeClass('loading');
        },
        error: function() {
            button.removeClass('loading');
        }
    });
};

$(document).ready(function() {
    $.fn.zato.rules.init();
});
