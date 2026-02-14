(function() {
    'use strict';

    function ZatoConfirmButton() {
    }

    ZatoConfirmButton.buildRemoveHtml = function(itemId, extraClasses) {
        var classes = 'zato-confirm-btn zato-confirm-remove';
        if (extraClasses) {
            classes += ' ' + extraClasses;
        }
        var html = '<button class="' + classes + '" data-item-id="' + itemId + '" data-state="initial">';
        html += '<span class="zato-confirm-text">Remove</span>';
        html += '</button>';
        return html;
    };

    ZatoConfirmButton.buildEditHtml = function(itemId, extraClasses) {
        var classes = 'zato-confirm-btn zato-confirm-edit';
        if (extraClasses) {
            classes += ' ' + extraClasses;
        }
        var html = '<button class="' + classes + '" data-item-id="' + itemId + '">';
        html += '<span class="zato-confirm-text">Edit</span>';
        html += '</button>';
        return html;
    };

    ZatoConfirmButton.handleClick = function(button, onConfirm) {
        if (!button.classList.contains('zato-confirm-remove')) {
            return false;
        }

        var itemId = button.getAttribute('data-item-id');
        var state = button.getAttribute('data-state');

        if (state === 'initial') {
            button.setAttribute('data-state', 'confirming');
            button.classList.add('zato-confirm-confirming');
            var textEl = button.querySelector('.zato-confirm-text');
            if (textEl) {
                textEl.textContent = 'Really?';
            }

            var existingTimer = button.getAttribute('data-timer-id');
            if (existingTimer) {
                clearTimeout(parseInt(existingTimer, 10));
            }

            var timerId = setTimeout(function() {
                ZatoConfirmButton.reset(button);
                button.removeAttribute('data-timer-id');
            }, 2200);

            button.setAttribute('data-timer-id', timerId.toString());
            return true;

        } else if (state === 'confirming') {
            var existingTimer = button.getAttribute('data-timer-id');
            if (existingTimer) {
                clearTimeout(parseInt(existingTimer, 10));
                button.removeAttribute('data-timer-id');
            }

            if (onConfirm) {
                onConfirm(itemId);
            }
            return true;
        }

        return false;
    };

    ZatoConfirmButton.reset = function(button) {
        button.setAttribute('data-state', 'initial');
        button.classList.remove('zato-confirm-confirming');
        var textEl = button.querySelector('.zato-confirm-text');
        if (textEl) {
            textEl.textContent = 'Remove';
        }
    };

    ZatoConfirmButton.resetAll = function(container) {
        var buttons = container.querySelectorAll('.zato-confirm-remove[data-state="confirming"]');
        for (var i = 0; i < buttons.length; i++) {
            var btn = buttons[i];
            var timerId = btn.getAttribute('data-timer-id');
            if (timerId) {
                clearTimeout(parseInt(timerId, 10));
                btn.removeAttribute('data-timer-id');
            }
            ZatoConfirmButton.reset(btn);
        }
    };

    window.ZatoConfirmButton = ZatoConfirmButton;

})();
