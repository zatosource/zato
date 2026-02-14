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
            }

            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                var tabId = inputElement.getAttribute('data-tab-id');
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
                return true;
            }

            return false;
        },

        handleInput: function(e) {
            var inputElement = e.target.closest('.ai-chat-input');
            if (!inputElement) {
                return;
            }
            this.convertEmojisInInput(inputElement);
        },

        convertEmojisInInput: function(inputElement) {
            if (typeof markedEmoji === 'undefined' || !markedEmoji.emojis) {
                return;
            }

            var sel = window.getSelection();
            if (!sel.rangeCount) return;

            var range = sel.getRangeAt(0);
            var container = range.startContainer;

            if (container.nodeType !== Node.TEXT_NODE) {
                return;
            }

            var text = container.textContent;
            var cursorPos = range.startOffset;

            var shortcodeMatch = text.match(/:([a-z0-9_+-]+):/i);
            if (shortcodeMatch) {
                var name = shortcodeMatch[1].toLowerCase();
                var emoji = markedEmoji.emojis[name];
                if (emoji) {
                    var matchStart = shortcodeMatch.index;
                    var matchEnd = matchStart + shortcodeMatch[0].length;
                    var newText = text.substring(0, matchStart) + emoji + text.substring(matchEnd);
                    container.textContent = newText;
                    var newCursorPos = matchStart + emoji.length;
                    if (cursorPos > matchEnd) {
                        newCursorPos = cursorPos - shortcodeMatch[0].length + emoji.length;
                    } else if (cursorPos > matchStart) {
                        newCursorPos = matchStart + emoji.length;
                    } else {
                        newCursorPos = cursorPos;
                    }
                    var newRange = document.createRange();
                    newRange.setStart(container, Math.min(newCursorPos, newText.length));
                    newRange.collapse(true);
                    sel.removeAllRanges();
                    sel.addRange(newRange);
                    return;
                }
            }

            var asciiEmoticons = {
                ":)": "smile", ":-)": "smile", ":(": "frown", ":-(": "frown",
                ":D": "grin", ":-D": "grin", ";)": "wink", ";-)": "wink",
                ":P": "yum", ":-P": "yum", ":p": "yum", ":-p": "yum",
                ":O": "open_mouth", ":-O": "open_mouth", ":o": "open_mouth", ":-o": "open_mouth",
                ":/": "confused", ":-/": "confused", ":|": "neutral_face", ":-|": "neutral_face",
                ":*": "kissing_heart", ":-*": "kissing_heart",
                "B)": "sunglasses", "B-)": "sunglasses",
                "XD": "joy", "xD": "joy",
                ":3": "blush", ":-3": "blush",
                "<3": "heart", "</3": "broken_heart"
            };

            var sortedAscii = Object.keys(asciiEmoticons).sort(function(a, b) {
                return b.length - a.length;
            });

            for (var i = 0; i < sortedAscii.length; i++) {
                var ascii = sortedAscii[i];
                var idx = text.indexOf(ascii);
                if (idx !== -1) {
                    var beforeChar = idx > 0 ? text[idx - 1] : ' ';
                    var afterIdx = idx + ascii.length;
                    var afterChar = afterIdx < text.length ? text[afterIdx] : ' ';
                    if ((beforeChar === ' ' || beforeChar === '\n' || idx === 0) &&
                        (afterChar === ' ' || afterChar === '\n' || afterIdx === text.length)) {
                        var emojiName = asciiEmoticons[ascii];
                        var emojiChar = markedEmoji.emojis[emojiName];
                        if (emojiChar) {
                            var newText = text.substring(0, idx) + emojiChar + text.substring(afterIdx);
                            container.textContent = newText;
                            var newCursorPos = idx + emojiChar.length;
                            if (cursorPos > afterIdx) {
                                newCursorPos = cursorPos - ascii.length + emojiChar.length;
                            } else if (cursorPos > idx) {
                                newCursorPos = idx + emojiChar.length;
                            } else {
                                newCursorPos = cursorPos;
                            }
                            var newRange = document.createRange();
                            newRange.setStart(container, Math.min(newCursorPos, newText.length));
                            newRange.collapse(true);
                            sel.removeAllRanges();
                            sel.addRange(newRange);
                            return;
                        }
                    }
                }
            }
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
                    return false;
                }


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
