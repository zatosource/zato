// The queue and DLQ page of an outgoing connection.

// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.outgoing_delivery');

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing_delivery.config = {

    idPrefix: 'delivery',
    popoverClass: 'delivery-popover',

    messageUrl: '/zato/outgoing/delivery/message/',
    refreshUrl: '/zato/outgoing/delivery/refresh/',
    downloadUrl: '/zato/outgoing/delivery/download/',
    actionUrl: '/zato/outgoing/delivery/action/',
    saveUrl: '/zato/outgoing/delivery/save/',

    // The two halves of a download
    downloadBody: 'body',
    downloadDocument: 'document',

    actions: {
        retry:   {title: 'Retry',   doneLabel: 'Retry',   pastLabel: 'Retried'},
        discard: {title: 'Discard', doneLabel: 'Discard', pastLabel: 'Discarded'}
    },

    targetSelectedSingular: 'selected message',
    targetSelectedPlural: 'selected messages',

    disabledClass: 'delivery-action-disabled',
    chipVisibleClass: 'delivery-selected-chip-visible',
    chipSizerClass: 'delivery-selected-chip-sizer',
    chipRowSingular: 'row',
    chipRowPlural: 'rows',
    escapeKey: 'Escape',

    tabSelector: '.delivery-tabs .dashboard-tab',
    tabPanelPrefix: 'delivery-tab-panel-',
    tabUrlParam: 'tab',
    tablePrefix: '#delivery-table-',

    resultSingular: 'message',
    resultPlural: 'messages',
    statusOK: 200,
    successHideMs: 2500,

    // The time-ago cells of both tabs
    timeAgoContainer: '#markup',
    timeAgoTimeField: 'time_utc',

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
    labelRule: 'DLQ rule',
    labelDestination: 'Destination',
    labelSize: 'Size',
    labelBody: 'Body',
    labelDownloadBody: 'Download body',
    labelDownloadDocument: 'Download document',
    sizeUnit: 'bytes',
    emptyValue: '-',

    // The Ace modes are named by the services as the part after this prefix
    aceModePrefix: 'ace/mode/',
    editorMinLines: 12,
    editorMaxLines: 30
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing_delivery.state = {
    connType: '',
    connId: '',
    connName: '',
    clusterId: '',

    pendingAction: '',
    pendingTarget: null,
    pendingLink: null
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

    page.initSelectedChips();
    page.bindSelection();
    page.bindActions();
    page.bindDetails();
    page.initTimeAgo();
}

// /////////////////////////////////////////////////////////////////////////////

// The "Pub time" and "Moved to DLQ time" columns are the same time-ago cells the scheduler's
// Last run column is, with the words of this page and its own refresh URL
$.fn.zato.outgoing_delivery.initTimeAgo = function() {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;
    var state = page.state;
    var timeAgo = $.fn.zato.time_ago;

    timeAgo.config.highlight_column = '';
    timeAgo.config.refresh_time_field = config.timeAgoTimeField;
    timeAgo.config.refresh_url = config.refreshUrl + '?conn_type=' + state.connType + '&conn_id=' + state.connId;

    timeAgo.init(config.timeAgoContainer);
    timeAgo.start_auto_refresh(config.timeAgoContainer, timeAgo.config.refresh_url);
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

$.fn.zato.outgoing_delivery.helpDescriptions = function() {
    return {};
}

// /////////////////////////////////////////////////////////////////////////////

// The descriptors of the two popovers
$.fn.zato.outgoing_delivery.buildDescriptors = function() {

    var config = $.fn.zato.outgoing_delivery.config;
    var targetSpec = {field: 'target', label: '', kind: 'target'};

    var out = {};

    out.retry = {
        title: config.actions.retry.title,
        fitContent: true,
        pages: [[targetSpec]]
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

    var count = document.createElement('span');
    count.className = 'delivery-popover-target-count';
    count.textContent = target.msgIdList.length;

    var noun = document.createElement('span');
    noun.textContent = ' ' + $.fn.zato.outgoing_delivery.pluralize(target.msgIdList.length,
        config.targetSelectedSingular, config.targetSelectedPlural);

    line.appendChild(count);
    line.appendChild(noun);

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

// An action link waits for at least one ticked row and says how many there are
$.fn.zato.outgoing_delivery.updateActionLinks = function(kind) {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;
    var table = page.table(kind);

    var selectedCount = table.find('.delivery-row-select:checked').length;
    var links = $('.delivery-action-link[data-kind="' + kind + '"]');

    links.toggleClass(config.disabledClass, !selectedCount);

    page.updateSelectedChip(kind, selectedCount);
}

// /////////////////////////////////////////////////////////////////////////////

// The chip in the gutter to the left of the table that says how many rows are ticked -
// it is out of the table's flow, so it can come and go without moving anything.
$.fn.zato.outgoing_delivery.updateSelectedChip = function(kind, selectedCount) {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;

    var chip = $('.delivery-selected-chip[data-kind="' + kind + '"]');

    if(!selectedCount) {
        chip.removeClass(config.chipVisibleClass);
        return;
    }

    chip.text(page.chipText(selectedCount));

    // Level with the header's checkbox, whatever the header's height is
    var header = page.table(kind).find('th.delivery-cell-select')[0];
    var headerRect = header.getBoundingClientRect();
    var wrapRect = chip.parent()[0].getBoundingClientRect();
    var top = headerRect.top - wrapRect.top + headerRect.height / 2;

    chip.css('top', top + 'px');
    chip.addClass(config.chipVisibleClass);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing_delivery.chipText = function(count) {
    var config = $.fn.zato.outgoing_delivery.config;
    var out = count + ' ' + $.fn.zato.outgoing_delivery.pluralize(count, config.chipRowSingular, config.chipRowPlural);
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Each chip is given the width of the widest count its table can show, which is the count
// of all its rows, so that the chip never grows or shrinks as rows are ticked.
$.fn.zato.outgoing_delivery.initSelectedChips = function() {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;

    $('.delivery-table').each(function() {

        var kind = this.getAttribute('data-kind');
        var rowCount = $(this).find('.delivery-row-select').length;
        var chip = $('.delivery-selected-chip[data-kind="' + kind + '"]');

        // The copy is measured off the body, since a hidden tab's own panel has no size to give
        var sizer = $('<span></span>');
        sizer.attr('class', chip.attr('class'));
        sizer.addClass(config.chipVisibleClass);
        sizer.addClass(config.chipSizerClass);
        sizer.text(page.chipText(rowCount));

        $(document.body).append(sizer);
        chip.css('min-width', sizer[0].getBoundingClientRect().width + 'px');
        sizer.remove();
    });
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

// The action links above each table
$.fn.zato.outgoing_delivery.bindActions = function() {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;

    $('.delivery-action-link').on('click', function() {

        if(this.classList.contains(config.disabledClass)) {
            return;
        }

        var kind = this.getAttribute('data-kind');
        var action = this.getAttribute('data-action');

        var target = {kind: kind, msgIdList: page.selectedMsgIdList(kind)};

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
    page.state.pendingLink = link;

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

    var data = {
        conn_type: state.connType,
        conn_id: state.connId,
        kind: target.kind,
        action: action,
        msg_id_list: JSON.stringify(target.msgIdList)
    };

    $.fn.zato.action_runner.run({
        link_elem: state.pendingLink,
        url: config.actionUrl,
        data: $.param(data),
        parse: function(jqXHR) {
            var out = page.parseActionResponse(action, jqXHR);
            return out;
        },
        details_modal_title: config.actions[action].title,
        success_hide_ms: config.successHideMs,
        on_complete: function(instance, result) {
            if(result.is_success) {
                page.onActionDone(target);
            }
        }
    });
}

// /////////////////////////////////////////////////////////////////////////////

// What the tippy on the link says
$.fn.zato.outgoing_delivery.parseActionResponse = function(action, jqXHR) {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;

    var response = JSON.parse(jqXHR.responseText);

    if(jqXHR.status !== config.statusOK) {
        var out = {
            is_success: false,
            label: response.error,
            details_title: response.error,
            details_body: jqXHR.responseText,
            details_lexer: '',
            status_code: jqXHR.status
        };
        return out;
    }

    var count = response.count;
    var noun = page.pluralize(count, config.resultSingular, config.resultPlural);
    var label = config.actions[action].pastLabel + ' ' + count + ' ' + noun;

    var out = {
        is_success: true,
        label: label,
        details_title: label,
        details_body: jqXHR.responseText,
        details_lexer: '',
        status_code: jqXHR.status
    };
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Removes the rows the action took
$.fn.zato.outgoing_delivery.onActionDone = function(target) {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;

    var table = page.table(target.kind);

    for(var idx = 0; idx < target.msgIdList.length; idx++) {
        table.find('tr[data-msg-id="' + target.msgIdList[idx] + '"]').remove();
    }

    table.find('.delivery-select-all').prop('checked', false);
    page.updateActionLinks(target.kind);
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

    $('.delivery-table').on('click', '.delivery-address-link', function() {
        var kind = this.getAttribute('data-kind');
        var msgId = this.getAttribute('data-msg-id');
        page.openInvoker(kind, msgId);
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
