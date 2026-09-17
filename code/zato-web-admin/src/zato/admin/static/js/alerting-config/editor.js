// Alert rules - the popover editor.
//
// The wizard kit's micro-form, hosted here on the hidden fields the
// template carries, one set serving every row. The row clicked fills
// them in before the popover opens on the very value that was clicked.

(function($) {

var screen = $.fn.zato.alerting_config;
var config = screen.config;

// ////////////////////////////////////////////////////////////////////////

var editor = {
    forms: {},
    config: {idPrefix: config.idPrefix}
};
screen.editor = editor;

// The hidden fields the popover reads and writes, named the way it expects
editor.field = function(name) {
    var out = $('#id_' + config.idPrefix + '-' + name);
    return out;
};

// A field is explained in the same words wherever it is edited
editor.helpDescriptions = function() {

    var out = {};

    $.each(config.fieldHelp, function(fieldName, text) {
        out[editor.forms.inputId(fieldName)] = text;
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Seeds the hidden fields from the row and opens its popover on the very
// value that was clicked
screen.openEditor = function(link) {

    var openCard = link.closest('.alert-rules-set-card');
    screen.openCard = openCard;

    var typeName = screen.setNameOf(openCard);

    openCard.querySelectorAll('.alert-rules-param-edit').forEach(function(edit) {

        var fieldInput = editor.field(edit.dataset.field);

        if(edit.dataset.kind === 'checkbox') {
            fieldInput.prop('checked', edit.dataset.value === 'true');
        }
        else if(edit.dataset.kind === 'duration') {
            var parts = screen.splitDuration(parseInt(edit.dataset.value));
            fieldInput.val(parts.count);
            editor.field(screen.unitFieldName(edit.dataset.field)).val(parts.unit.value);
        }
        else if(edit.dataset.kind === 'amount') {
            var amountParts = screen.splitAmount(parseInt(edit.dataset.value));
            fieldInput.val(amountParts.count);
            editor.field(screen.unitFieldName(edit.dataset.field)).val(amountParts.unit.value);
        }
        else if(edit.dataset.kind === 'size') {
            var sizeParts = screen.splitSize(parseInt(edit.dataset.value));
            fieldInput.val(sizeParts.count);
            editor.field(screen.unitFieldName(edit.dataset.field)).val(sizeParts.unit.value);
        }
        else {
            fieldInput.val(edit.dataset.value);
        }
    });

    editor.forms.open(typeName, link, link.dataset.field);
};

// ////////////////////////////////////////////////////////////////////////

// The help at each type's own row header, keyed by the type's hidden state field
screen.helpDescriptions = function() {

    var out = {};

    $.each(config.typeHelp, function(setName, text) {
        out[config.fieldIdPrefix + setName] = text;
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
