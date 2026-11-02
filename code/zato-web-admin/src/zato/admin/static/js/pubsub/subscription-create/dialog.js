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

    elements.subscriber = document.getElementById(prefix + 'subscriber');
    elements.cards = document.getElementById(prefix + 'cards');
    elements.pane = document.getElementById(prefix + 'pane');
    elements.total = document.getElementById(prefix + 'total');
    elements.inputs = document.getElementById(prefix + 'inputs');
    elements.submit = document.getElementById(prefix + 'submit');
    elements.cards.appendChild(form.buildSearch());

    elements.subscriber.addEventListener('change', form.onSubscriberChange);
    elements.cards.addEventListener('click', form.onCardClick);
    elements.pane.addEventListener('click', form.onPaneClick);
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
    $.fn.zato.remove_css_attention(form.elements.total);

    form.renderSubscriber();
    form.renderTopics();

    $(config.dialogId).dialog('option', 'width', config.dialogWidth);
    $.fn.zato.data_table._create_edit('create', labels.title, null);
    form.widenSelects();
};

// ////////////////////////////////////////////////////////////////////////

form.open = function() {
    form.load(form.show);
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
        if(state.service === '') {
            out = form.selectOf('service');
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
            out = form.elements.total;
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
// and a client is the security definition it authenticates with.
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
        form.addInput('delivery_type', config.deliveryPush);
        form.addInput('push_type', config.pushTypeService);
        form.addInput('push_service_name', state.service);
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

    var selects = form.elements.subscriber.querySelectorAll('select');
    var missing = form.missingPart();

    $.fn.zato.remove_css_attention(selects);
    $.fn.zato.remove_css_attention(form.elements.total);

    if(missing !== null) {
        $.fn.zato.draw_attention_to(missing);
        return;
    }

    form.writeInputs();
    $.fn.zato.data_table.on_submit('create');
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
