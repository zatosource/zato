// Wizard kit - pick-one choice cards.
//
// A choice group is a set of cards of which exactly one is selected at a
// time - a radio group wearing the wizard card look. The selected card
// unfolds its body, where its own inline fields live, and may carry a
// one-line summary in its header.
//
// ---------------------------------------------------------------
// How to use
// ---------------------------------------------------------------
//
// The markup - cards share a data-choice-group value, each has its own
// data-choice-id, and the body is optional:
//
//      <div class="wizard-choice-card wizard-choice-card-selected"
//          data-choice-group="ready" data-choice-id="stability">
//          <div class="wizard-choice-header">
//              <span class="wizard-choice-radio"></span>
//              <span class="wizard-choice-label">When it stops changing</span>
//              <span class="wizard-choice-summary"></span>
//          </div>
//          <div class="wizard-choice-desc">...</div>
//          <div class="wizard-choice-body">...</div>
//      </div>
//
// The wiring:
//
//      var handle = $.fn.zato.wizard_kit.choices.init({
//          group: 'ready',
//          onChange: function(choiceId) { ... }
//      });
//
//      handle.get();          - the selected card's data-choice-id
//      handle.set('marker');  - selects a card programmatically

(function($) {

// ////////////////////////////////////////////////////////////////////////

var kit = $.fn.zato.wizard_kit;
kit.choices = {};

// ////////////////////////////////////////////////////////////////////////

kit.choices.init = function(config) {

    var cards = $('.wizard-choice-card[data-choice-group="' + config.group + '"]');

    var select = function(choiceId, shouldNotify) {

        cards.each(function() {
            var card = $(this);
            var isSelected = card.attr('data-choice-id') === choiceId;
            card.toggleClass('wizard-choice-card-selected', isSelected);
        });

        if(shouldNotify && config.onChange) {
            config.onChange(choiceId);
        }
    };

    cards.on('click', function(event) {

        // Clicks on the unfolded body's own inputs must not re-select,
        // which would steal the focus from the input being typed into
        if($(event.target).closest('.wizard-choice-body').length) {
            return;
        }

        select($(this).attr('data-choice-id'), true);
    });

    var out = {

        get: function() {
            var selected = cards.filter('.wizard-choice-card-selected');
            var out = selected.attr('data-choice-id');
            return out;
        },

        set: function(choiceId) {
            select(choiceId, false);
        }
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
