// Wizard kit - the live check a step can run against what has been filled
// in so far.
//
// Some answers can be proven right there and then. An address and the
// framing that goes with it are one such set - either something answers
// on the other side or it does not, and a wizard that can say so before
// anything is saved spares the reader a round trip through the list page.
//
// A probe is one button, the spinner that turns beside it while the check
// runs and the verdict written next to them once it is over. It posts the
// named fields of the rendered Django form to an endpoint of the instance's
// choosing through the action runner, which is what every other button on
// the dashboard reports its outcome through - the tooltip beside the button
// saying how it went, and a failed check keeping the whole of what came
// back one click away behind Show details. Nothing is stored, so a probe
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
//          validate: function() { return wizard.field('address').val() ? '' : 'The address is empty'; },
//          validatedField: 'address',
//          runLabel: 'Ping'
//      });
//
// The template holds the row and its label, the label pointing at buttonId
// so the check is a regular "How does it work?" stop, and the kit fills the
// slot with the button, the spinner and the verdict.
//
// validate says whether there is anything to send to - it returns an empty
// string when there is and the text to write beside the button when there
// is not, in which case nothing is sent, no spinner turns and no tooltip
// opens, and the focus moves to validatedField, the one the text is about,
// so it can be put right at once. The instance clears the text through
// reset() once that field is typed into.
//
// The endpoint answers with {is_ok, summary, details, details_lexer} - the
// summary is the one line said beside the button, the details what Show
// details opens, highlighted with the named Pygments lexer. The instance's
// own view decides what both say, the kit only decides how they look.
//
// init returns a handle with reset(), for an instance that wants the
// verdict cleared once an answer the check was about has changed.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var kit = $.fn.zato.wizard_kit;
kit.probe = {};

// ////////////////////////////////////////////////////////////////////////

kit.probe.config = {

    // What the button says - it stays as it is while a check is running
    runLabel: 'Test it',

    // What a check that never reached the endpoint reports
    requestErrorText: 'The check could not be run',

    // What the details of an outcome open under
    detailsModalTitle: 'Response',

    // Which side of the button the outcome tooltip opens on
    placement: 'top',

    // The spinner beside the button - the one the settings pages turn
    // beside their own buttons, in settings.css - and how long it stays
    // on screen at the least, the way theirs does, so a fast answer does
    // not flash it
    spinnerSrc: '/static/gfx/spinner.svg',
    spinnerActiveClass: 'active',
    spinnerMinMs: 500,

    // What a checkbox sends when it is on, which is what a browser
    // posting the form itself would send
    checkedValue: 'on'
};

// ////////////////////////////////////////////////////////////////////////

kit.probe.init = function(wizard, spec) {

    var probeConfig = kit.probe.config;

    var runLabel = spec.runLabel ? spec.runLabel : probeConfig.runLabel;

    var slot = document.getElementById(spec.slotId);

    // A step re-entered does not build its controls again
    slot.innerHTML = '';

    // The spinner and the button share one wrapper, the way the settings
    // pages lay theirs out - the spinner after the button, so the button
    // stays where it is when the spinner comes on ..
    var wrapper = document.createElement('div');
    wrapper.className = 'button-wrapper';
    slot.appendChild(wrapper);

    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'secondary-button';
    button.id = spec.buttonId;
    button.textContent = runLabel;
    wrapper.appendChild(button);

    var spinner = document.createElement('img');
    spinner.className = 'button-spinner';
    spinner.src = probeConfig.spinnerSrc;
    wrapper.appendChild(spinner);

    // .. and the verdict follows them on the same line.
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

    // The endpoint answers with a verdict either way, so anything else
    // means the request itself did not get through
    var parse = function(jqXHR) {

        var isHttpOk = (jqXHR.status >= 200 && jqXHR.status < 300);

        if(!isHttpOk) {
            return {
                is_success: false,
                label: probeConfig.requestErrorText,
                details_title: probeConfig.requestErrorText,
                details_body: jqXHR.responseText,
                details_lexer: '',
                status_code: jqXHR.status
            };
        }

        var response = JSON.parse(jqXHR.responseText);

        var out = {
            is_success: response.is_ok,
            label: response.summary,
            details_title: response.summary,
            details_body: response.details,
            details_lexer: response.details_lexer,
            status_code: 0
        };

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    var paint = function(summary) {

        result.textContent = summary;
        result.classList.add('wizard-probe-ok');
    };

    // What is said beside the button when there is nothing to send to -
    // no request goes out, so no spinner turns and no tooltip opens
    var paintInvalid = function(text) {

        result.textContent = text;
        result.classList.add('wizard-probe-error');
    };

// ////////////////////////////////////////////////////////////////////////

    // Whether a check is on its way - the button itself stays as it is
    // throughout, the way the settings pages' buttons do, the spinner
    // beside it being the only thing that says so
    var isRunning = false;

    button.addEventListener('click', function() {

        // A check already on its way is left to finish
        if(isRunning) {
            return;
        }

        reset();

        // Nothing to send to - said right here, the request and everything
        // that goes with it being for an endpoint that was actually named
        var invalidText = spec.validate();

        if(invalidText) {
            paintInvalid(invalidText);

            // The field the text is about takes the focus, with what is in it left
            // as it is - the caret goes to its end rather than the text being selected
            var field = wizard.field(spec.validatedField)[0];
            field.focus();
            field.setSelectionRange(field.value.length, field.value.length);

            return;
        }

        isRunning = true;
        spinner.classList.add(probeConfig.spinnerActiveClass);

        $.fn.zato.action_runner.run({
            link_elem: button,
            url: spec.endpoint,
            data: buildRequest(),
            placement: probeConfig.placement,
            details_modal_title: probeConfig.detailsModalTitle,

            // The spinner beside the button is the indicator, so the tooltip
            // only reports the outcome, and not before the spinner has had
            // its time on screen
            show_spinner: false,
            min_wait_ms: probeConfig.spinnerMinMs,
            parse: parse,

            on_complete: function(instance, outcome) {

                isRunning = false;
                spinner.classList.remove(probeConfig.spinnerActiveClass);

                // The OK tooltip is gone after a moment, so the verdict stays written
                // beside the button - a failure stays in its own tooltip with Show
                // details, which is where it is read, so nothing is written beside it
                if(outcome.is_success) {
                    paint(outcome.label);
                }
            }
        });
    });

// ////////////////////////////////////////////////////////////////////////

    var out = {
        reset: reset
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
