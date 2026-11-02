// Pub/sub - the form creating a subscription, the subscriber row.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var form = $.fn.zato.pubsub.subscription_create;
var config = form.config;
var labels = config.labels;

// ////////////////////////////////////////////////////////////////////////

form.buildKindField = function() {

    var kindOptions = [
        {value: config.kindService, label: labels.service},
        {value: config.kindClient, label: labels.client}
    ];

    var out = form.buildSelectField('kind', labels.subscriber, kindOptions);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.buildActiveField = function() {

    var inputId = config.activeInputId;

    var field = document.createElement('div');
    field.className = 'micro-form-field ' + config.idPrefix + 'field-active';

    var label = document.createElement('label');
    label.className = 'micro-form-label';
    label.setAttribute('for', inputId);
    label.textContent = labels.active;

    var control = document.createElement('div');
    control.className = config.idPrefix + 'switch';

    var input = document.createElement('input');
    input.type = 'checkbox';
    input.id = inputId;
    input.name = config.activeInputName;
    input.setAttribute('data-key', 'isActive');
    input.checked = form.state.isActive;

    control.appendChild(input);

    field.appendChild(label);
    field.appendChild(control);

    var out = field;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

form.renderSubscriber = function() {

    var row = form.elements.subscriber;

    row.textContent = '';

    row.appendChild(form.buildActiveField());
    row.appendChild(form.buildKindField());
    row.appendChild(form.buildSubscriberFields());
};

// ////////////////////////////////////////////////////////////////////////

// The row has to be on screen, a select in a closed dialog measures nothing.
form.widenSelects = function() {

    var selects = form.elements.subscriber.querySelectorAll('select');
    var naturalWidths = [];

    for(var selectIdx = 0; selectIdx < selects.length; selectIdx++) {
        naturalWidths.push(selects[selectIdx].offsetWidth);
    }

    for(var widenIdx = 0; widenIdx < selects.length; widenIdx++) {
        selects[widenIdx].style.width = (naturalWidths[widenIdx] + config.selectExtraWidth) + 'px';
    }
};

// ////////////////////////////////////////////////////////////////////////

form.onSubscriberChange = function(event) {

    var target = event.target;
    var stateKey = target.getAttribute('data-key');

    // The switch only flips the flag ..
    if(target.type === 'checkbox') {
        form.state[stateKey] = target.checked;
        return;
    }

    form.state[stateKey] = target.value;

    // .. the kind and the delivery decide the fields of the subscriber ..
    if(stateKey === 'kind' || stateKey === 'delivery') {
        form.renderSubscriber();
        form.widenSelects();
    }

    // .. and the kind and a client's permissions decide the topics.
    if(stateKey === 'kind' || stateKey === 'client') {
        form.renderTopics();
    }

    form.syncFooter();
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
