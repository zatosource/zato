
// Mapper kit - modal dialogs.
// A hand-rolled modal with a title, an optional textarea, an optional
// text input, an error line and OK / Cancel buttons. Used by the schema
// panel for pasting examples, pasting JSON Schema documents and naming
// saved schemas.

(function($) {

    zato.mapper.dialog = {};

// ////////////////////////////////////////////////////////////////////////

    // Opens a modal dialog.
    // dialogConfig:
    //   title:        heading text
    //   withTextarea: include a paste textarea
    //   withInput:    include a single-line text input
    //   inputLabel:   label for the text input
    //   okLabel:      text of the confirm button
    //   onSubmit:     called with {text, value}; returning an error string
    //                 keeps the dialog open and shows the error, returning
    //                 nothing closes it
    zato.mapper.dialog.open = function(dialogConfig) {

        var overlay = document.createElement('div');
        overlay.className = 'mapper-dialog-overlay';

        var dialog = document.createElement('div');
        dialog.className = 'mapper-dialog';
        dialog.setAttribute('role', 'dialog');

        var title = document.createElement('h2');
        title.className = 'mapper-dialog-title';
        title.textContent = dialogConfig.title;
        dialog.appendChild(title);

        var textarea = null;
        if (dialogConfig.withTextarea) {
            textarea = document.createElement('textarea');
            textarea.className = 'mapper-dialog-textarea';
            dialog.appendChild(textarea);
        }

        var input = null;
        if (dialogConfig.withInput) {
            var label = document.createElement('label');
            label.className = 'mapper-dialog-label';
            label.textContent = dialogConfig.inputLabel;

            input = document.createElement('input');
            input.className = 'mapper-dialog-input';
            input.type = 'text';

            label.appendChild(input);
            dialog.appendChild(label);
        }

        var error = document.createElement('div');
        error.className = 'mapper-dialog-error';
        dialog.appendChild(error);

        var buttons = document.createElement('div');
        buttons.className = 'mapper-dialog-buttons';

        var cancelButton = document.createElement('button');
        cancelButton.className = 'mapper-button zato-action-button';
        cancelButton.type = 'button';
        cancelButton.textContent = 'Cancel';
        buttons.appendChild(cancelButton);

        var okButton = document.createElement('button');
        okButton.className = 'mapper-button zato-action-button mapper-button-confirm';
        okButton.type = 'button';
        okButton.textContent = dialogConfig.okLabel;
        buttons.appendChild(okButton);

        dialog.appendChild(buttons);
        overlay.appendChild(dialog);
        document.body.appendChild(overlay);

        function close() {
            $(overlay).remove();
        }

        function submit() {

            var text = '';
            if (textarea) {
                text = textarea.value;
            }

            var value = '';
            if (input) {
                value = input.value;
            }

            // The handler decides: an error string keeps the dialog open.
            var errorText = dialogConfig.onSubmit({text: text, value: value});
            if (errorText) {
                error.textContent = errorText;
                return;
            }

            close();
        }

        $(cancelButton).on('click', close);
        $(okButton).on('click', submit);

        // Escape cancels, exactly like the Cancel button.
        $(overlay).on('keydown', function(event) {
            if (event.key === 'Escape') {
                close();
            }
        });

        // Focus goes to the first editable element.
        if (textarea) {
            textarea.focus();
        }
        else if (input) {
            input.focus();
        }
        else {
            okButton.focus();
        }
    };

})(jQuery);
