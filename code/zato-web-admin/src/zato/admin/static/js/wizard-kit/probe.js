// Wizard kit - the live check a step can run against what has been filled
// in so far.
//
// Some answers can be proven right there and then. An address and the
// framing that goes with it are one such set - either something answers
// on the other side or it does not, and a wizard that can say so before
// anything is saved spares the reader a round trip through the list page.
//
// A probe is one button and one verdict beside it. It posts the named
// fields of the rendered Django form to an endpoint of the instance's
// choosing and paints what comes back. Nothing is stored, so a probe
// works on the very first step of a wizard that has never saved.
//
// ---------------------------------------------------------------
// How to use
// ---------------------------------------------------------------
//
//      $.fn.zato.wizard_kit.probe.init(wizard, {
//          slotId: 'my-wizard-slot-check',
//          buttonId: 'my-wizard-check',
//          endpoint: '/zato/my/check/?cluster=1',
//          fields: ['address', 'start_seq', 'end_seq'],
//          runLabel: 'Test the connection'
//      });
//
// The template holds the row and its label, the label pointing at buttonId
// so the check is a regular "How does it work?" stop, and the kit fills the
// slot with the button and the verdict.
//
// The endpoint answers with {is_ok, summary} - the instance's own view
// decides what the one line says, the kit only decides how it looks.
//
// init returns a handle with reset(), for an instance that wants the
// verdict cleared once an answer the check was about has changed.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var kit = $.fn.zato.wizard_kit;
kit.probe = {};

// ////////////////////////////////////////////////////////////////////////

kit.probe.config = {

    // What the button says, and what it says while a check is running
    runLabel: 'Test it',
    busyLabel: 'Testing ..',

    // What a check that never reached the endpoint reports
    requestErrorText: 'The check could not be run',

    // What a checkbox sends when it is on, which is what a browser
    // posting the form itself would send
    checkedValue: 'on'
};

// ////////////////////////////////////////////////////////////////////////

kit.probe.init = function(wizard, spec) {

    var probeConfig = kit.probe.config;

    var runLabel = spec.runLabel ? spec.runLabel : probeConfig.runLabel;
    var busyLabel = spec.busyLabel ? spec.busyLabel : probeConfig.busyLabel;

    var slot = document.getElementById(spec.slotId);

    // A step re-entered does not build its controls again
    slot.innerHTML = '';

    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'wizard-probe-button';
    button.id = spec.buttonId;
    button.textContent = runLabel;
    slot.appendChild(button);

    var result = document.createElement('span');
    result.className = 'wizard-probe-result';
    slot.appendChild(result);

// ////////////////////////////////////////////////////////////////////////

    // Whatever the last check said is no longer about what is on screen
    var reset = function() {
        result.textContent = '';
        result.classList.remove('wizard-probe-ok', 'wizard-probe-error');
    };

// ////////////////////////////////////////////////////////////////////////

    // What goes with the check - the current value of each named field,
    // a checkbox contributing only while it is on, the way a browser
    // posting the form itself would send it
    var buildRequest = function() {

        var out = {};

        for(var fieldIdx = 0; fieldIdx < spec.fields.length; fieldIdx++) {

            var fieldName = spec.fields[fieldIdx];
            var field = wizard.field(fieldName);

            if(field.attr('type') === 'checkbox') {
                if(field.is(':checked')) {
                    out[fieldName] = probeConfig.checkedValue;
                }
            }
            else {
                out[fieldName] = field.val();
            }
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    var paint = function(isOk, summary) {

        result.textContent = summary;
        result.classList.toggle('wizard-probe-ok', isOk);
        result.classList.toggle('wizard-probe-error', !isOk);
    };

// ////////////////////////////////////////////////////////////////////////

    button.addEventListener('click', function() {

        // A check already on its way is left to finish
        if(button.disabled) {
            return;
        }

        reset();

        button.disabled = true;
        button.textContent = busyLabel;

        var callback = function(data, status) {

            button.disabled = false;
            button.textContent = runLabel;

            // The endpoint answers with a verdict either way, so anything
            // else means the request itself did not get through
            if(status !== 'success') {
                paint(false, probeConfig.requestErrorText);
                return;
            }

            var response = JSON.parse(data.responseText);
            paint(response.is_ok, response.summary);
        };

        $.fn.zato.post(spec.endpoint, callback, buildRequest());
    });

// ////////////////////////////////////////////////////////////////////////

    var out = {
        reset: reset
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
