// The details window of one message and the invoke dialog its destination opens.

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

$.fn.zato.outgoing_delivery.aceMode = function(bodyMode) {
    var out = $.fn.zato.outgoing_delivery.config.aceModePrefix + bodyMode;
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

// The invoke dialog of the connection type's list page, with the message's own method, query string and body filled in
$.fn.zato.outgoing_delivery.openInvoker = function(kind, msgId) {

    var page = $.fn.zato.outgoing_delivery;
    var config = page.config;
    var state = page.state;
    var url = page.messageUrl(config.messageUrl, kind, msgId);

    $.getJSON(url, function(details) {
        var invoker = details.invoker;

        var options = {
            id: state.connId,
            name: state.connName,
            connection: invoker.connection,
            history_key: invoker.history_key_prefix + state.connId,
            get_invoke_url_func: function(id) {
                return invoker.url_prefix + id + '/';
            },
            request: details.data,
            request_mode: page.aceMode(details.body_mode)
        };

        // What is the message's own - for an HTTP type its method and query string - comes from the services
        $.extend(options, invoker.options);

        $.fn.zato.invoker.open_overlay(options);
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

// A fact whose value is a map, one line per entry
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

// The request facts the services describe - a value that is a map is listed one line per entry
$.fn.zato.outgoing_delivery.addRequestFacts = function(facts, requestFacts) {

    var page = $.fn.zato.outgoing_delivery;

    for(var factIdx = 0; factIdx < requestFacts.length; factIdx++) {
        var fact = requestFacts[factIdx];

        if(typeof fact.value === 'object') {
            page.addMapFact(facts, fact.label, fact.value);
        }
        else {
            page.addFact(facts, fact.label, fact.value);
        }
    }
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
        page.addFact(facts, config.labelRule, details.rule);
    }

    var dataSize = new Blob([request.data]).size;

    page.addFact(facts, config.labelDestination, details.destination);
    page.addFact(facts, config.labelSize, dataSize + ' ' + config.sizeUnit);
    page.addRequestFacts(facts, details.facts);

    body.appendChild(facts);

    var bodyHeader = document.createElement('div');
    bodyHeader.className = 'delivery-details-body-header';

    var bodyLabel = document.createElement('span');
    bodyLabel.textContent = config.labelBody;
    bodyHeader.appendChild(bodyLabel);

    body.appendChild(bodyHeader);

    var editor = document.createElement('div');
    editor.className = 'delivery-details-editor';
    body.appendChild(editor);

    document.body.appendChild(overlay);

    $.fn.zato.highlight_pane.init({
        container: editor,
        text: details.data,
        editable: true,
        ace_mode: page.aceMode(details.body_mode),
        ace_options: {
            minLines: config.editorMinLines,
            maxLines: config.editorMaxLines
        },
        buttons: [
            $.fn.zato.highlight_pane.buttons.download({
                id: 'delivery-details-download-body',
                label: config.labelDownloadBody,
                url: page.messageUrl(config.downloadUrl, kind, msgId, config.downloadBody)
            }),
            $.fn.zato.highlight_pane.buttons.download({
                id: 'delivery-details-download-document',
                label: config.labelDownloadDocument,
                url: page.messageUrl(config.downloadUrl, kind, msgId, config.downloadDocument)
            }),
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
