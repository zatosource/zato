(function() {
    'use strict';

    var AIChatInput = {

        handleKeyDown: function(e, sendMessageCallback) {
            var inputElement = e.target.closest('.ai-chat-input');
            if (!inputElement) {
                return false;
            }

            console.debug('AIChatInput.handleKeyDown: key:', e.key, 'shiftKey:', e.shiftKey);

            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                var tabId = inputElement.getAttribute('data-tab-id');
                console.debug('AIChatInput.handleKeyDown: enter pressed, tabId:', tabId);
                sendMessageCallback(tabId);
                return true;
            }

            if (e.key === 'Backspace' || e.key === 'Delete') {
                var text = (inputElement.textContent || '').trim();
                var brCount = inputElement.querySelectorAll('br').length;
                if (text === '' && brCount > 0) {
                    e.preventDefault();
                    var brs = inputElement.querySelectorAll('br');
                    var brToRemove = e.key === 'Backspace' ? brs[brs.length - 1] : brs[0];
                    brToRemove.parentNode.removeChild(brToRemove);
                    var newBrCount = inputElement.querySelectorAll('br').length;
                    console.debug('AIChatInput.handleKeyDown:', e.key, 'removed br:', JSON.stringify({
                        brCountBefore: brCount,
                        brCountAfter: newBrCount,
                        innerHTML: inputElement.innerHTML
                    }));
                    if (newBrCount === 0) {
                        inputElement.innerHTML = '';
                    }
                    return true;
                }
            }

            if (e.key === 'Enter' && e.shiftKey) {
                e.preventDefault();
                var br = document.createElement('br');
                var sel = window.getSelection();
                var range = sel.getRangeAt(0);
                range.deleteContents();
                range.insertNode(br);
                range.setStartAfter(br);
                range.setEndAfter(br);
                sel.removeAllRanges();
                sel.addRange(range);
                return true;
            }

            return false;
        },

        handleInput: function(e) {
        },

        handleKeyUp: function(e) {
        },

        getMessageText: function(inputElement) {
            return (inputElement.textContent || inputElement.innerText || '').trim();
        },

        clearInput: function(inputElement) {
            inputElement.innerHTML = '';
        }
    };

    window.AIChatInput = AIChatInput;

})();
