(function() {
    'use strict';

    var LLMChatInput = {

        handleKeyDown: function(e, sendMessageCallback) {
            var inputElement = e.target.closest('.llm-chat-input');
            if (!inputElement) {
                return false;
            }

            console.debug('LLMChatInput.handleKeyDown: key:', e.key, 'shiftKey:', e.shiftKey);

            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                var tabId = inputElement.getAttribute('data-tab-id');
                console.debug('LLMChatInput.handleKeyDown: enter pressed, tabId:', tabId);
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
                    console.debug('LLMChatInput.handleKeyDown:', e.key, 'removed br:', JSON.stringify({
                        brCountBefore: brCount,
                        brCountAfter: newBrCount,
                        innerHTML: inputElement.innerHTML
                    }));
                    if (newBrCount === 0) {
                        inputElement.innerHTML = '';
                        var inputArea = inputElement.closest('.llm-chat-input-area');
                        if (inputArea) {
                            inputArea.classList.remove('multiline');
                            inputArea.removeAttribute('data-user-multiline');
                        }
                    }
                    return true;
                }
            }

            if (e.key === 'Enter' && e.shiftKey) {
                e.preventDefault();
                var inputArea = inputElement.closest('.llm-chat-input-area');
                if (inputArea) {
                    var brCountBefore = inputElement.querySelectorAll('br').length;
                    inputArea.classList.add('multiline');
                    inputArea.setAttribute('data-user-multiline', 'true');
                    var br = document.createElement('br');
                    var sel = window.getSelection();
                    var range = sel.getRangeAt(0);
                    range.deleteContents();
                    range.insertNode(br);
                    range.setStartAfter(br);
                    range.setEndAfter(br);
                    sel.removeAllRanges();
                    sel.addRange(range);
                    var brCountAfter = inputElement.querySelectorAll('br').length;
                    console.debug('LLMChatInput.handleKeyDown: shift+enter:', JSON.stringify({
                        brCountBefore: brCountBefore,
                        brCountAfter: brCountAfter,
                        innerHTML: inputElement.innerHTML,
                        inputScrollHeight: inputElement.scrollHeight,
                        inputOffsetHeight: inputElement.offsetHeight,
                        inputAreaHeight: inputArea.offsetHeight,
                        hasMultilineClass: inputArea.classList.contains('multiline')
                    }));
                }
                return true;
            }

            return false;
        },

        handleInput: function(e) {
            if (e.target.classList.contains('llm-chat-input')) {
                this.updateMultilineState(e.target);
            }
        },

        handleKeyUp: function(e) {
            var inputElement = e.target.closest('.llm-chat-input');
            if (inputElement && (e.key === 'Backspace' || e.key === 'Delete')) {
                this.updateMultilineState(inputElement);
            }
        },

        updateMultilineState: function(inputElement) {
            var inputArea = inputElement.closest('.llm-chat-input-area');
            if (!inputArea) {
                return;
            }

            var text = (inputElement.textContent || '').trim();
            var brCount = inputElement.querySelectorAll('br').length;
            var inputHeight = inputElement.scrollHeight;
            var inputOffsetHeight = inputElement.offsetHeight;
            var inputAreaHeight = inputArea.offsetHeight;
            var hasMultilineClass = inputArea.classList.contains('multiline');
            var userMultiline = inputArea.getAttribute('data-user-multiline');

            console.debug('LLMChatInput.updateMultilineState:', JSON.stringify({
                text: text,
                textLength: text.length,
                brCount: brCount,
                innerHTML: inputElement.innerHTML,
                inputScrollHeight: inputHeight,
                inputOffsetHeight: inputOffsetHeight,
                inputAreaHeight: inputAreaHeight,
                hasMultilineClass: hasMultilineClass,
                userMultiline: userMultiline
            }));

            if (text === '' && brCount === 0) {
                console.debug('LLMChatInput.updateMultilineState: clearing - empty text and no br');
                inputElement.innerHTML = '';
                inputArea.classList.remove('multiline');
                inputArea.removeAttribute('data-user-multiline');
            }
        },

        getMessageText: function(inputElement) {
            return (inputElement.textContent || inputElement.innerText || '').trim();
        },

        clearInput: function(inputElement) {
            inputElement.innerHTML = '';
            var inputArea = inputElement.closest('.llm-chat-input-area');
            if (inputArea) {
                inputArea.classList.remove('multiline');
                inputArea.removeAttribute('data-user-multiline');
            }
        }
    };

    window.LLMChatInput = LLMChatInput;

})();
