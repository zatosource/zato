(function() {
    'use strict';

    var AIChatInput = {

        debugKeystrokes: false,
        pasteToAttachmentThreshold: 8000,

        handleKeyDown: function(e, sendMessageCallback) {
            var inputElement = e.target.closest('.ai-chat-input');
            if (!inputElement) {
                return false;
            }

            if (this.debugKeystrokes) {
                var sel = window.getSelection();
                var cursorInfo = sel.rangeCount > 0 ? {
                    startOffset: sel.getRangeAt(0).startOffset,
                    endOffset: sel.getRangeAt(0).endOffset,
                    collapsed: sel.getRangeAt(0).collapsed,
                    startContainer: sel.getRangeAt(0).startContainer.nodeName,
                    innerHTML: inputElement.innerHTML
                } : null;
                console.debug('AIChatInput.handleKeyDown: key:', e.key, 'shiftKey:', e.shiftKey, 'cursor:', JSON.stringify(cursorInfo));
            }

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
                var textNode = document.createTextNode('\u200B');
                var selEnter = window.getSelection();
                var range = selEnter.getRangeAt(0);
                range.deleteContents();
                range.insertNode(textNode);
                range.insertNode(br);
                range.setStart(textNode, 1);
                range.setEnd(textNode, 1);
                selEnter.removeAllRanges();
                selEnter.addRange(range);
                console.debug('AIChatInput.handleKeyDown: shift+enter inserted br, innerHTML:', inputElement.innerHTML);
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
        },

        handlePaste: function(e, addAttachmentCallback) {
            var clipboardData = e.clipboardData || window.clipboardData;
            if (!clipboardData) {
                return false;
            }

            var pastedText = clipboardData.getData('text/plain');
            if (pastedText && pastedText.length > this.pasteToAttachmentThreshold) {
                e.preventDefault();

                var inputElement = e.target.closest('.ai-chat-input');
                var tabId = inputElement ? inputElement.getAttribute('data-tab-id') : null;
                if (!tabId) {
                    console.debug('AIChatInput.handlePaste: no tabId found');
                    return false;
                }

                console.debug('AIChatInput.handlePaste: converting to attachment, length:', pastedText.length, 'tabId:', tabId);

                var attachment = AIChatTabState.createAttachmentFromPaste(tabId, pastedText);

                if (addAttachmentCallback) {
                    addAttachmentCallback(attachment, tabId);
                }

                return true;
            }

            return false;
        }
    };

    window.AIChatInput = AIChatInput;

})();
