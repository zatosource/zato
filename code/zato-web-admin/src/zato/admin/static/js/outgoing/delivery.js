// The queue and DLQ page of an outgoing connection.

// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.outgoing_delivery');

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing_delivery.config = {

    idPrefix: 'delivery',
    popoverClass: 'delivery-popover',

    messageUrl: '/zato/outgoing/delivery/message/',
    downloadUrl: '/zato/outgoing/delivery/download/',
    actionUrl: '/zato/outgoing/delivery/action/',
    saveUrl: '/zato/outgoing/delivery/save/',

    // The two halves of a download
    downloadBody: 'body',
    downloadDocument: 'document',

    // The hidden form the Forward popover reads and writes
    fieldForwardTo: 'forward_to',
    fieldKeepHeader: 'keep_header',

    actions: {
        retry:   {title: 'Retry',   doneLabel: 'Retry',   pastLabel: 'Retried'},
        forward: {title: 'Forward', doneLabel: 'Forward', pastLabel: 'Forwarded'},
        discard: {title: 'Discard', doneLabel: 'Discard', pastLabel: 'Discarded'}
    },

    labelTopic: 'Topic',
    labelKeepHeader: 'Keep the DLQ header',

    targetMessage: 'Message',
    targetSelectedSingular: 'selected message',
    targetSelectedPlural: 'selected messages',
    targetAllPrefix: 'All',
    targetAllMatching: 'matching',
    targetMessageSingular: 'message',
    targetMessagePlural: 'messages',

    scopeSelected: 'selected',
    scopeAll: 'all',
    disabledClass: 'delivery-action-disabled',
    escapeKey: 'Escape',

    tabSelector: '.delivery-tabs .dashboard-tab',
    tabPanelPrefix: 'delivery-tab-panel-',
    tabUrlParam: 'tab',
    tablePrefix: '#delivery-table-',

    resultSingular: 'message',
    resultPlural: 'messages',
    resultForwardTo: 'to',
    statusOK: 200,

    detailsTitle: 'Message',
    detailsWidth: '860px',
    labelConnection: 'Connection',
    labelCID: 'CID',
    labelPublished: 'Published',
    labelMovedToDLQ: 'Moved to DLQ',
    labelReason: 'Reason',
    labelRounds: 'Retries so far',
    labelLastError: 'Last error',
    labelSourceTopic: 'Source topic',
    labelMethod: 'Method',
    labelContentType: 'Content type',
    labelSize: 'Size',
    labelHeaders: 'Headers',
    labelQueryString: 'Query string',
    labelBody: 'Body',
    labelDownloadBody: 'Download body',
    labelDownloadDocument: 'Download document',
    sizeUnit: 'bytes',
    emptyValue: '-',

    // The Ace mode a body of an unknown content type is shown in
    defaultAceMode: 'ace/mode/text',
    editorMinLines: 12,
    editorMaxLines: 30
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing_delivery.state = {
    connType: '',
    connId: '',
    connName: '',
    clusterId: '',

    // Each tab's query and total, by kind
    tabs: {},

    pendingAction: '',
    pendingTarget: null
};

// The micro-forms kit installs the popover engine here
$.fn.zato.outgoing_delivery.forms = {};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing_delivery.init = function(options) {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;
    var state = page.state;

    state.connType = options.connType;
    state.connId = options.connId;
    state.connName = options.connName;
    state.clusterId = options.clusterId;
    state.tabs = options.tabs;

    page.initTabs(options.activeTab);

    $.fn.zato.micro_forms.setup(page, {
        descriptors: page.buildDescriptors(),
        popupClass: config.popoverClass,
        showHowItWorks: false,
        showCancel: true,
        onDone: page.runPendingAction
    });

    page.forms.registerKind('target', {
        build: page.buildTargetRow,
        save: function() {}
    });

    page.bindSelection();
    page.bindActions();
    page.bindDetails();
}

// /////////////////////////////////////////////////////////////////////////////

// The tabs, the active one is in the address
$.fn.zato.outgoing_delivery.initTabs = function(activeTab) {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;
    var kit = $.fn.zato.dashboard_kit;

    var updates = {};

    page.tabHandle = kit.tabs.init({
        tab_selector: config.tabSelector,
        panel_prefix: config.tabPanelPrefix,
        default_tab: activeTab,
        on_change: function(tabName) {
            updates[config.tabUrlParam] = tabName;
            kit.url_state.set(updates);
        }
    });

    kit.url_state.on_pop(function(params) {
        var popTab = params.get(config.tabUrlParam);
        if(popTab) {
            page.tabHandle.set_tab(popTab, true);
        }
    });
}

// /////////////////////////////////////////////////////////////////////////////

// The table of one tab
$.fn.zato.outgoing_delivery.table = function(kind) {
    var out = $($.fn.zato.outgoing_delivery.config.tablePrefix + kind);
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// A field of the hidden form
$.fn.zato.outgoing_delivery.field = function(fieldName) {
    var out = $('#id_' + fieldName);
    return out;
}

$.fn.zato.outgoing_delivery.helpDescriptions = function() {
    return {};
}

// /////////////////////////////////////////////////////////////////////////////

// The descriptors of the three popovers
$.fn.zato.outgoing_delivery.buildDescriptors = function() {

    var config = $.fn.zato.outgoing_delivery.config;
    var targetSpec = {field: 'target', label: '', kind: 'target'};

    var out = {};

    out.retry = {
        title: config.actions.retry.title,
        fitContent: true,
        pages: [[targetSpec]]
    };

    out.forward = {
        title: config.actions.forward.title,
        fitContent: true,
        pages: [[
            targetSpec,
            {field: config.fieldForwardTo, label: config.labelTopic, kind: 'select'},
            {field: config.fieldKeepHeader, label: config.labelKeepHeader, kind: 'checkbox'}
        ]]
    };

    out.discard = {
        title: config.actions.discard.title,
        fitContent: true,
        pages: [[targetSpec]]
    };

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The line at the top of a popover naming what the action is for
$.fn.zato.outgoing_delivery.buildTargetRow = function(fieldSpec, row) {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;
    var target = page.state.pendingTarget;

    var line = document.createElement('div');
    line.className = 'delivery-popover-target';

    if(target.msgId) {
        var label = document.createElement('span');
        label.textContent = config.targetMessage + ' ';

        var id = document.createElement('span');
        id.className = 'delivery-popover-target-id';
        id.textContent = target.msgId;

        line.appendChild(label);
        line.appendChild(id);
    }
    else if(target.scope === config.scopeSelected) {
        var count = document.createElement('span');
        count.className = 'delivery-popover-target-count';
        count.textContent = target.msgIdList.length;

        var noun = document.createElement('span');
        noun.textContent = ' ' + $.fn.zato.outgoing_delivery.pluralize(target.msgIdList.length,
            config.targetSelectedSingular, config.targetSelectedPlural);

        line.appendChild(count);
        line.appendChild(noun);
    }
    else {
        var tab = page.state.tabs[target.kind];

        var prefix = document.createElement('span');
        prefix.textContent = config.targetAllPrefix + ' ';

        var total = document.createElement('span');
        total.className = 'delivery-popover-target-count';
        total.textContent = tab.total;

        var totalNoun = document.createElement('span');
        totalNoun.textContent = ' ' + $.fn.zato.outgoing_delivery.pluralize(tab.total,
            config.targetMessageSingular, config.targetMessagePlural);

        line.appendChild(prefix);
        line.appendChild(total);
        line.appendChild(totalNoun);

        if(tab.query) {
            var matching = document.createElement('span');
            matching.textContent = ' ' + config.targetAllMatching + ' ';

            var query = document.createElement('span');
            query.className = 'delivery-popover-target-query';
            query.textContent = tab.query;

            line.appendChild(matching);
            line.appendChild(query);
        }
    }

    row.appendChild(line);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing_delivery.pluralize = function(count, singular, plural) {
    var out = count === 1 ? singular : plural;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The checkboxes of each table
$.fn.zato.outgoing_delivery.bindSelection = function() {

    var page = $.fn.zato.outgoing_delivery;

    $('.delivery-table').on('change', '.delivery-select-all', function() {
        var table = $(this).closest('table');
        table.find('.delivery-row-select').prop('checked', this.checked);
        page.updateActionLinks(table.attr('data-kind'));
    });

    $('.delivery-table').on('change', '.delivery-row-select', function() {
        var table = $(this).closest('table');
        var allCount = table.find('.delivery-row-select').length;
        var checkedCount = table.find('.delivery-row-select:checked').length;
        table.find('.delivery-select-all').prop('checked', allCount === checkedCount);
        page.updateActionLinks(table.attr('data-kind'));
    });

    $('.delivery-table').each(function() {
        page.updateActionLinks(this.getAttribute('data-kind'));
    });
}

// /////////////////////////////////////////////////////////////////////////////

// The "selected" links need a ticked row, the "all" links need any row
$.fn.zato.outgoing_delivery.updateActionLinks = function(kind) {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;
    var table = page.table(kind);

    var hasRows = table.find('.delivery-row-select').length > 0;
    var hasSelection = table.find('.delivery-row-select:checked').length > 0;

    var links = $('.delivery-action-link[data-kind="' + kind + '"]');

    links.filter('[data-scope="' + config.scopeSelected + '"]').toggleClass(config.disabledClass, !hasSelection);
    links.filter('[data-scope="' + config.scopeAll + '"]').toggleClass(config.disabledClass, !hasRows);
}

// /////////////////////////////////////////////////////////////////////////////

// The ids of the ticked rows of one table
$.fn.zato.outgoing_delivery.selectedMsgIdList = function(kind) {

    var out = [];

    $.fn.zato.outgoing_delivery.table(kind).find('.delivery-row-select:checked').each(function() {
        var row = $(this).closest('tr');
        out.push(row.attr('data-msg-id'));
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The action links above and inside each table
$.fn.zato.outgoing_delivery.bindActions = function() {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;

    $('.delivery-action-link').on('click', function() {

        if(this.classList.contains(config.disabledClass)) {
            return;
        }

        var kind = this.getAttribute('data-kind');
        var action = this.getAttribute('data-action');
        var scope = this.getAttribute('data-scope');

        var target = {kind: kind, scope: scope, msgId: '', msgIdList: []};

        if(scope === config.scopeSelected) {
            target.msgIdList = page.selectedMsgIdList(kind);
        }

        page.openAction(action, target, this);
    });

    $('.delivery-table').on('click', '.delivery-row-action', function() {

        var kind = this.getAttribute('data-kind');
        var action = this.getAttribute('data-action');
        var msgId = this.getAttribute('data-msg-id');

        var target = {kind: kind, scope: config.scopeSelected, msgId: msgId, msgIdList: [msgId]};
        page.openAction(action, target, this);
    });
}

// /////////////////////////////////////////////////////////////////////////////

// Opens one action's popover
$.fn.zato.outgoing_delivery.openAction = function(action, target, link) {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;

    page.state.pendingAction = action;
    page.state.pendingTarget = target;

    page.forms.config.doneLabel = config.actions[action].doneLabel;
    page.forms.open(action, link);
}

// /////////////////////////////////////////////////////////////////////////////

// Runs the action the popover was open for
$.fn.zato.outgoing_delivery.runPendingAction = function() {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;
    var state = page.state;

    var action = state.pendingAction;
    var target = state.pendingTarget;

    var msgIdList = '';
    var query = '';

    if(target.scope === config.scopeSelected) {
        msgIdList = JSON.stringify(target.msgIdList);
    }
    else {
        query = state.tabs[target.kind].query;
    }

    var data = {
        conn_type: state.connType,
        conn_id: state.connId,
        kind: target.kind,
        action: action,
        msg_id_list: msgIdList,
        query: query,
        forward_to: page.field(config.fieldForwardTo).val(),
        keep_header: page.field(config.fieldKeepHeader).prop('checked')
    };

    var callback = function(jqXHR) {

        var response = JSON.parse(jqXHR.responseText);

        if(jqXHR.status !== config.statusOK) {
            $.fn.zato.user_message(false, response.error);
            return;
        }

        page.onActionDone(action, target, response);
    };

    $.fn.zato.post(config.actionUrl, callback, data, 'text');
}

// /////////////////////////////////////////////////////////////////////////////

// Removes the rows the action took and reports how many
$.fn.zato.outgoing_delivery.onActionDone = function(action, target, response) {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;

    var count = response.count;
    var noun = page.pluralize(count, config.resultSingular, config.resultPlural);
    var message = config.actions[action].pastLabel + ' ' + count + ' ' + noun;

    if(action === 'forward') {
        message += ' ' + config.resultForwardTo + ' ' + response.forward_to;
    }

    var table = page.table(target.kind);

    if(target.scope === config.scopeSelected) {
        for(var idx = 0; idx < target.msgIdList.length; idx++) {
            table.find('tr[data-msg-id="' + target.msgIdList[idx] + '"]').remove();
        }
    }
    else {
        table.find('tbody tr').remove();
    }

    table.find('.delivery-select-all').prop('checked', false);
    page.updateActionLinks(target.kind);

    $.fn.zato.user_message(true, message);
}

// /////////////////////////////////////////////////////////////////////////////

// The message id links
$.fn.zato.outgoing_delivery.bindDetails = function() {

    var page = $.fn.zato.outgoing_delivery;

    $('.delivery-table').on('click', '.delivery-message-link', function() {
        var kind = this.getAttribute('data-kind');
        var msgId = this.getAttribute('data-msg-id');
        page.openDetails(kind, msgId);
    });

    $(document).on('keydown.delivery_details', function(event) {
        if(event.key !== page.config.escapeKey) {
            return;
        }
        if($('[data-delivery-details]').length) {
            event.preventDefault();
            page.closeDetails();
        }
    });
}

// /////////////////////////////////////////////////////////////////////////////

// The address of one message or of one of its downloads
$.fn.zato.outgoing_delivery.messageUrl = function(baseUrl, kind, msgId, what) {

    var state = $.fn.zato.outgoing_delivery.state;

    var out = baseUrl +
        '?cluster=' + encodeURIComponent(state.clusterId) +
        '&conn_type=' + encodeURIComponent(state.connType) +
        '&conn_id=' + encodeURIComponent(state.connId) +
        '&kind=' + encodeURIComponent(kind) +
        '&msg_id=' + encodeURIComponent(msgId);

    if(what) {
        out += '&what=' + encodeURIComponent(what);
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing_delivery.openDetails = function(kind, msgId) {

    var page = $.fn.zato.outgoing_delivery;
    var url = page.messageUrl(page.config.messageUrl, kind, msgId);

    $.getJSON(url, function(details) {
        page.showDetails(kind, msgId, details);
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing_delivery.closeDetails = function() {
    $('[data-delivery-details]').remove();
}

// /////////////////////////////////////////////////////////////////////////////

// One label and value pair of the details window
$.fn.zato.outgoing_delivery.addFact = function(facts, label, value, valueClass) {

    var config = $.fn.zato.outgoing_delivery.config;

    var labelElement = document.createElement('div');
    labelElement.className = 'delivery-details-label';
    labelElement.textContent = label;

    var valueElement = document.createElement('div');
    valueElement.className = 'delivery-details-value';

    if(valueClass) {
        valueElement.className += ' ' + valueClass;
    }

    if(value === '') {
        valueElement.textContent = config.emptyValue;
    }
    else {
        valueElement.textContent = value;
    }

    facts.appendChild(labelElement);
    facts.appendChild(valueElement);
}

// /////////////////////////////////////////////////////////////////////////////

// The headers or the query string, one line each
$.fn.zato.outgoing_delivery.addMapFact = function(facts, label, map) {

    var config = $.fn.zato.outgoing_delivery.config;
    var names = Object.keys(map);

    var labelElement = document.createElement('div');
    labelElement.className = 'delivery-details-label';
    labelElement.textContent = label;

    var valueElement = document.createElement('div');
    valueElement.className = 'delivery-details-value';

    if(names.length === 0) {
        valueElement.textContent = config.emptyValue;
    }
    else {
        var list = document.createElement('ul');
        list.className = 'delivery-details-headers';

        for(var nameIdx = 0; nameIdx < names.length; nameIdx++) {
            var name = names[nameIdx];
            var item = document.createElement('li');
            item.textContent = name + ': ' + map[name];
            list.appendChild(item);
        }

        valueElement.appendChild(list);
    }

    facts.appendChild(labelElement);
    facts.appendChild(valueElement);
}

// /////////////////////////////////////////////////////////////////////////////

// The details window
$.fn.zato.outgoing_delivery.showDetails = function(kind, msgId, details) {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;
    var state = page.state;

    page.closeDetails();

    var envelope = details.document;
    var request = envelope.request;

    var overlay = document.createElement('div');
    overlay.className = 'invoker-modal-overlay delivery-details';
    overlay.setAttribute('data-delivery-details', '1');
    overlay.style.zIndex = '100001';

    var backdrop = document.createElement('div');
    backdrop.className = 'invoker-modal-backdrop';
    backdrop.addEventListener('click', page.closeDetails);
    overlay.appendChild(backdrop);

    var content = document.createElement('div');
    content.className = 'invoker-modal-content';
    content.style.width = config.detailsWidth;
    content.style.maxHeight = '90vh';
    overlay.appendChild(content);

    var header = document.createElement('div');
    header.className = 'invoker-modal-header';

    var title = document.createElement('h2');
    title.textContent = config.detailsTitle + ' ' + msgId;
    header.appendChild(title);

    var closeButton = document.createElement('button');
    closeButton.className = 'invoker-modal-close-button';
    closeButton.addEventListener('click', page.closeDetails);
    header.appendChild(closeButton);

    content.appendChild(header);

    var body = document.createElement('div');
    body.className = 'invoker-modal-body';
    content.appendChild(body);

    var facts = document.createElement('div');
    facts.className = 'delivery-details-facts';

    page.addFact(facts, config.labelConnection, state.connName);
    page.addFact(facts, config.labelCID, envelope.cid);
    page.addFact(facts, config.labelPublished, envelope.pub_time_iso);

    if(details.has_dlq_header) {
        var dlqHeader = envelope.dlq;
        page.addFact(facts, config.labelMovedToDLQ, dlqHeader.moved_time_iso);
        page.addFact(facts, config.labelReason, dlqHeader.reason);
        page.addFact(facts, config.labelRounds, dlqHeader.rounds);
        page.addFact(facts, config.labelLastError, dlqHeader.error, 'delivery-details-value-error');
        page.addFact(facts, config.labelSourceTopic, dlqHeader.source_topic);
    }

    var dataSize = new Blob([request.data]).size;

    page.addFact(facts, config.labelMethod, request.method);
    page.addFact(facts, config.labelContentType, details.content_type);
    page.addFact(facts, config.labelSize, dataSize + ' ' + config.sizeUnit);
    page.addMapFact(facts, config.labelHeaders, request.headers);
    page.addMapFact(facts, config.labelQueryString, request.params);

    body.appendChild(facts);

    var bodyHeader = document.createElement('div');
    bodyHeader.className = 'delivery-details-body-header';

    var bodyLabel = document.createElement('span');
    bodyLabel.textContent = config.labelBody;
    bodyHeader.appendChild(bodyLabel);

    var links = document.createElement('span');
    links.className = 'delivery-details-body-links';

    var downloadBody = document.createElement('a');
    downloadBody.href = page.messageUrl(config.downloadUrl, kind, msgId, config.downloadBody);
    downloadBody.textContent = config.labelDownloadBody;
    links.appendChild(downloadBody);

    var downloadDocument = document.createElement('a');
    downloadDocument.href = page.messageUrl(config.downloadUrl, kind, msgId, config.downloadDocument);
    downloadDocument.textContent = config.labelDownloadDocument;
    links.appendChild(downloadDocument);

    bodyHeader.appendChild(links);
    body.appendChild(bodyHeader);

    var editor = document.createElement('div');
    editor.className = 'delivery-details-editor';
    body.appendChild(editor);

    document.body.appendChild(overlay);

    var aceMode = $.fn.zato.highlight_pane.mime_to_ace_mode(details.content_type);

    if(!aceMode) {
        aceMode = config.defaultAceMode;
    }

    $.fn.zato.highlight_pane.init({
        container: editor,
        text: details.data,
        editable: true,
        ace_mode: aceMode,
        ace_options: {
            minLines: config.editorMinLines,
            maxLines: config.editorMaxLines
        },
        buttons: [
            $.fn.zato.highlight_pane.buttons.copy(),
            $.fn.zato.highlight_pane.buttons.save({
                poll_url: config.saveUrl,
                save_action: 'update-message',
                hidden_fields: {
                    conn_type: state.connType,
                    conn_id: state.connId,
                    kind: kind,
                    msg_id: msgId
                }
            })
        ]
    });
}

// /////////////////////////////////////////////////////////////////////////////
