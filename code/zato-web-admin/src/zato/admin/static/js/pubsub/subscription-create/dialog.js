// Pub/sub - the form creating a subscription, the data from the server, the dialog and the submission.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var form = $.fn.zato.pubsub.subscription_create;
var config = form.config;
var labels = config.labels;

// ////////////////////////////////////////////////////////////////////////

form.init = function() {

    var elements = form.elements;
    var prefix = config.idPrefix;

    elements.root = document.getElementById(config.formId);
    elements.subscriber = document.getElementById(prefix + 'subscriber');
    elements.cards = document.getElementById(prefix + 'cards');
    elements.pane = document.getElementById(prefix + 'pane');
    elements.topics = document.getElementById(prefix + 'topics');
    elements.togglesHeader = document.getElementById(prefix + 'toggles-header');
    elements.togglesHeader.textContent = labels.topicsField;
    elements.inputs = document.getElementById(prefix + 'inputs');
    elements.submit = document.getElementById(prefix + 'submit');
    elements.cards.appendChild(form.buildSearch());

    elements.subscriber.addEventListener('change', form.onSubscriberChange);
    elements.cards.addEventListener('click', form.onCardClick);
    elements.pane.addEventListener('click', form.onPaneClick);
    elements.topics.addEventListener('click', form.onTopicsClick);
    elements.submit.addEventListener('click', form.submit);
};

// ////////////////////////////////////////////////////////////////////////

form.load = function(onLoaded) {

    var onSuccess = function(data) {
        form.takeData(data);
        onLoaded();
    };

    // A proxy in front of the server may answer with a page rather than with the view's own JSON
    var onError = function(request) {

        var message = request.statusText;

        if(request.responseJSON !== undefined) {
            message = request.responseJSON.error;
        }

        $.fn.zato.user_message(false, message);
    };

    $.ajax({
        type: 'GET',
        url: config.dataURL,
        dataType: 'json',
        success: onSuccess,
        error: onError
    });
};

// ////////////////////////////////////////////////////////////////////////

// Each opening starts from a form just opened, whatever an earlier one was left with.
form.show = function() {

    form.state = form.newState();
    form.view = form.newView();

    form.elements.searchInput.value = '';
    form.fitSearch();
    form.clearAttention();
    form.chooseLayout();

    form.renderSubscriber();
    form.renderTopics();

    $(config.dialogId).dialog('option', 'width', config.dialogWidths[form.layout]);
    $.fn.zato.data_table._create_edit('create', labels.title, null);
    form.widenSelects();
    form.fitHeight();
};

// ////////////////////////////////////////////////////////////////////////

form.open = function() {
    form.load(form.show);
};

// ////////////////////////////////////////////////////////////////////////

// The dialog can be measured only once open - the topics give up whatever height the window lacks,
// and the dialog is centered again at its new height.
form.fitHeight = function() {

    var dialog = $(config.dialogId);
    var root = form.elements.root;
    var area = form.layout === config.layoutCards ? form.elements.cards.parentNode : form.elements.topics;

    root.style.removeProperty(config.heightProperty);

    var dialogHeight = dialog.dialog('widget').outerHeight();
    var excess = dialogHeight + (2 * config.windowMargin) - window.innerHeight;

    if(excess > 0) {
        root.style.setProperty(config.heightProperty, (area.offsetHeight - excess) + 'px');
    }

    dialog.dialog('option', 'position', {my: 'center', at: 'center', of: window});
};

// ////////////////////////////////////////////////////////////////////////

form.clearAttention = function() {

    var elements = form.elements;
    var selects = elements.subscriber.querySelectorAll('select');

    $.fn.zato.remove_css_attention(selects);
    $.fn.zato.remove_css_attention(elements.subscriber.querySelectorAll('.' + config.servicesTriggerClass));
    $.fn.zato.remove_css_attention(elements.cards);
    $.fn.zato.remove_css_attention(elements.topics);
};

// ////////////////////////////////////////////////////////////////////////

form.selectOf = function(stateKey) {
    var out = form.elements.subscriber.querySelector('select[data-key="' + stateKey + '"]');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The first part of the form still without an answer, or null when every part has one.
form.missingPart = function() {

    var state = form.state;
    var out = null;

    if(state.kind === config.kindService) {
        if(state.services.length === 0) {
            out = form.servicesTrigger();
        }
    }
    else if(state.client === '') {
        out = form.selectOf('client');
    }
    else if(state.delivery === config.deliveryPush) {
        if(state.endpoint === '') {
            out = form.selectOf('endpoint');
        }
    }

    if(out === null) {
        if(state.topics.length === 0) {
            out = form.topicsArea();
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.addInput = function(name, value) {

    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = name;
    input.value = value;

    form.elements.inputs.appendChild(input);
};

// ////////////////////////////////////////////////////////////////////////

// The fields the create view reads - a service receives its messages by push,
// one subscription for each service, and a client is the security definition it authenticates with.
form.writeInputs = function() {

    var state = form.state;

    form.elements.inputs.textContent = '';

    for(var topicIdx = 0; topicIdx < state.topics.length; topicIdx++) {

        var topicData = {
            topic_name: state.topics[topicIdx],
            is_pub_enabled: true,
            is_delivery_enabled: true
        };

        form.addInput('topic_data', JSON.stringify(topicData));
    }

    if(state.kind === config.kindService) {
        form.addInput('sec_base_id', '');
        form.addInput('delivery_type', config.deliveryPush);
        form.addInput('push_type', config.pushTypeService);
        form.addInput('push_service_name', form.pendingServices.shift());
        return;
    }

    form.addInput('sec_base_id', state.client);
    form.addInput('delivery_type', state.delivery);

    if(state.delivery === config.deliveryPush) {
        form.addInput('push_type', config.pushTypeREST);
        form.addInput('rest_push_endpoint_id', state.endpoint);
        form.addInput('rest_push_endpoint_name', form.data.endpointNames[state.endpoint]);
    }
};

// ////////////////////////////////////////////////////////////////////////

form.submit = function() {

    var missing = form.missingPart();

    form.clearAttention();

    if(missing !== null) {
        $.fn.zato.draw_attention_to(missing);
        return;
    }

    if(form.state.kind === config.kindService) {
        form.pendingServices = form.state.services.slice();
    }
    else {
        form.pendingServices = [];
    }

    form.submitNext();
};

// ////////////////////////////////////////////////////////////////////////

// The data table resets the form after each request, the switch included, so it is set again from the state.
form.submitNext = function() {

    var activeInput = document.getElementById(config.activeInputId);
    activeInput.checked = form.state.isActive;

    form.writeInputs();
    $.fn.zato.data_table.on_submit('create');
};

// ////////////////////////////////////////////////////////////////////////

// A failed request leaves the services after it without a subscription.
form.onSubmitComplete = function(status) {

    if(status !== 'success') {
        form.pendingServices = [];
        return;
    }

    if(form.pendingServices.length > 0) {
        form.submitNext();
    }
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
