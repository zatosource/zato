(function() {
    'use strict';

    var AIChatClickHandlers = {

        handleClick: function(e, widget, core) {
            var target = e.target;

            var timestamp = target.closest('.ai-chat-message-time');
            if (timestamp) {
                this.handleTimestampCopy(timestamp);
                return;
            }

            var diffNavBtn = target.closest('.ai-diff-nav-btn');
            if (diffNavBtn) {
                this.handleDiffNavClick(diffNavBtn);
                return;
            }

            var diffCopyBtn = target.closest('.ai-diff-copy');
            if (diffCopyBtn) {
                this.handleDiffCopy(diffCopyBtn);
                return;
            }

            var diffTag = target.closest('.ai-tool-tag[data-diff]');
            if (diffTag) {
                this.handleDiffTagClick(diffTag);
                return;
            }

            var anyTag = target.closest('.ai-tool-tag');
            if (anyTag) {
            }

            var showBtn = target.closest('.ai-tool-show-btn');
            if (showBtn) {
                this.handleShowItems(showBtn);
                return;
            }

            var retryBtn = target.closest('.ai-chat-retry-btn');
            if (retryBtn) {
                this.handleRetry(retryBtn, widget, core);
                return;
            }

            if (target.id === 'ai-chat-minimize') {
                AIChatWindow.toggleMinimize(widget, core);
                return;
            }

            if (target.id === 'ai-chat-maximize') {
                AIChatWindow.toggleMaximize(widget, core);
                return;
            }

            var settingsMenuItem = target.closest('.ai-chat-settings-menu-item');
            if (settingsMenuItem) {
                var action = settingsMenuItem.getAttribute('data-action');
                AIChatSettings.handleAction(action, null, {
                    onChangeProvider: function(hadKey) {
                        core.hadKeyOnEntry = hadKey;
                        core.cameFromChat = true;
                        core.needsConfig = true;
                        core.configMode = 'providers';
                        core.render();
                    },
                    onManageKeys: function(hadKey) {
                        core.hadKeyOnEntry = hadKey;
                        core.cameFromChat = true;
                        core.needsConfig = true;
                        core.configMode = 'manage-keys';
                        core.render();
                    }
                });
                e.stopPropagation();
                return;
            }


            if (target.classList.contains('ai-chat-send-button') || target.closest('.ai-chat-send-button')) {
                var button = target.classList.contains('ai-chat-send-button') ? target : target.closest('.ai-chat-send-button');
                var tabId = button.getAttribute('data-tab-id');
                if (button.classList.contains('ai-chat-stop-button')) {
                    AIChatStreaming.stopMessage(widget, core, tabId);
                } else {
                    var input = widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
                    var message = input ? AIChatInput.getMessageText(input) : '';
                    if (!message) {
                        if (input) {
                            input.focus();
                            core.showTemporaryTooltip(input, 'Type a message ..', 2100, true);
                        }
                        return;
                    }
                    AIChatStreaming.sendMessage(widget, core, tabId);
                }
                return;
            }

            if (target.classList.contains('ai-chat-options-button') || target.closest('.ai-chat-options-button')) {
                var optionsBtn = target.classList.contains('ai-chat-options-button') ? target : target.closest('.ai-chat-options-button');
                core.hideTooltip();
                AIChatOptionsMenu.toggle(widget, core.activeTabId, optionsBtn);
                e.stopPropagation();
                return;
            }

            var optionsMenuItem = target.closest('.ai-chat-options-menu-item');
            if (optionsMenuItem) {
                var action = optionsMenuItem.getAttribute('data-action');
                AIChatOptionsMenu.hide(widget);
                AIChatOptionsMenu.handleAction(action, {
                    onManageKeys: function() {
                        core.cameFromChat = true;
                        core.hadKeyOnEntry = AIChatConfig.hasAnyKey();
                        core.needsConfig = true;
                        core.configMode = 'manage-keys';
                        core.render();
                    },
                    onAddFiles: function() {
                        AIChatOptionsMenu.showFileDialog(core.activeTabId, function() {
                            AIChatAttachments.render(widget, core.activeTabId, core.tabs);
                        });
                    },
                    onManageMCP: function() {
                        core.cameFromChat = true;
                        core.needsConfig = true;
                        core.configMode = 'manage-mcp';
                        AIChatMCP.loadServers(function() {
                            core.render();
                        });
                    }
                });
                e.stopPropagation();
                return;
            }

            if (target.classList.contains('ai-chat-message-copy')) {
                var messageEl = target.closest('.ai-chat-message');
                if (messageEl) {
                    var contentEl = messageEl.querySelector('.ai-chat-message-content');
                    if (contentEl) {
                        var text = contentEl.textContent || contentEl.innerText;
                        navigator.clipboard.writeText(text).then(function() {
                            target.textContent = 'Copied';
                            setTimeout(function() {
                                target.textContent = 'Copy';
                            }, 1000);
                        });
                    }
                }
                return;
            }

            if (target.classList.contains('ai-chat-message-continue')) {
                var messageIndex = parseInt(target.getAttribute('data-message-index'), 10);
                AIChatStreaming.continueMessage(widget, core, core.activeTabId, messageIndex);
                return;
            }

            if (target.classList.contains('ai-chat-message-stop') || target.closest('.ai-chat-message-stop')) {
                var stopBtn = target.classList.contains('ai-chat-message-stop') ? target : target.closest('.ai-chat-message-stop');
                var tabId = stopBtn.getAttribute('data-tab-id');
                AIChatStreaming.stopMessage(widget, core, tabId);
                return;
            }

            if (target.classList.contains('ai-chat-attachment-remove') || target.closest('.ai-chat-attachment-remove')) {
                var removeBtn = target.classList.contains('ai-chat-attachment-remove') ? target : target.closest('.ai-chat-attachment-remove');
                var attachmentId = removeBtn.getAttribute('data-attachment-id');
                var tabPanel = removeBtn.closest('.ai-chat-tab-panel');
                var tabId = tabPanel ? tabPanel.getAttribute('data-tab-id') : core.activeTabId;
                AIChatTabState.removeAttachment(tabId, attachmentId);
                AIChatAttachments.render(widget, tabId, core.tabs);
                return;
            }

            var attachmentEl = target.closest('.ai-chat-attachment');
            if (attachmentEl && !target.closest('.ai-chat-attachment-remove')) {
                var attId = attachmentEl.getAttribute('data-attachment-id');
                var attTabPanel = attachmentEl.closest('.ai-chat-tab-panel');
                var attTabId = attTabPanel ? attTabPanel.getAttribute('data-tab-id') : core.activeTabId;
                var attachments = AIChatTabState.getAttachments(attTabId);
                for (var i = 0; i < attachments.length; i++) {
                    if (attachments[i].id === attId) {
                        AIChatPreview.show(attachments[i]);
                        break;
                    }
                }
                return;
            }

            var providerEl = target.closest('.ai-chat-config-provider');
            if (providerEl) {
                var providerId = providerEl.getAttribute('data-provider-id');
                core.needsConfig = true;
                core.configMode = 'key-input';
                AIChatSettings.showKeyInput(widget, providerId, function() {
                    core.render();
                });
                return;
            }

            var mcpBack = target.closest('#ai-chat-mcp-back');
            if (mcpBack) {
                core.needsConfig = false;
                core.configMode = 'providers';
                core.render();
                return;
            }

            var mcpDetailBack = target.closest('#ai-chat-mcp-detail-back');
            if (mcpDetailBack) {
                AIChatMCP.selectedServer = null;
                AIChatMCP.selectedServerTools = [];
                core.configMode = 'manage-mcp';
                core.render();
                return;
            }

            var mcpEditBack = target.closest('#ai-chat-mcp-edit-back');
            if (mcpEditBack) {
                AIChatMCP.selectedServer = null;
                core.configMode = 'manage-mcp';
                core.render();
                return;
            }

            var mcpAddBack = target.closest('#ai-chat-mcp-add-back');
            if (mcpAddBack) {
                core.configMode = 'manage-mcp';
                core.render();
                return;
            }

            var backEl = target.closest('.ai-chat-config-back');
            if (backEl) {
                AIChatSettings.handleBackClick(core.configMode, core.cameFromChat, core.hadKeyOnEntry, core.cameFromManageKeys, {
                    onReturnToChat: function() {
                        core.cameFromChat = false;
                        core.cameFromManageKeys = false;
                        core.needsConfig = false;
                        core.configMode = 'providers';
                        AIChatConfig.selectedProvider = null;
                        core.render();
                    },
                    onShowProviders: function() {
                        core.cameFromManageKeys = false;
                        core.needsConfig = true;
                        core.configMode = 'providers';
                        AIChatConfig.selectedProvider = null;
                        core.render();
                    },
                    onShowManageKeys: function() {
                        core.cameFromManageKeys = false;
                        core.needsConfig = true;
                        core.configMode = 'manage-keys';
                        AIChatConfig.selectedProvider = null;
                        core.render();
                    }
                });
                return;
            }

            var mcpAdd = target.closest('#ai-chat-mcp-add');
            if (mcpAdd) {
                core.configMode = 'add-mcp';
                core.render();
                return;
            }

            var mcpSave = target.closest('#ai-chat-mcp-save');
            if (mcpSave) {
                var endpointInput = widget.querySelector('#ai-chat-mcp-endpoint');
                var endpoint = endpointInput ? endpointInput.value.trim() : '';

                if (!endpoint) {
                    return;
                }

                var saveBtn = mcpSave;
                var originalText = saveBtn.textContent;
                saveBtn.disabled = true;
                saveBtn.innerHTML = '<img src="/static/img/spinner.svg" class="ai-chat-spinner-icon" alt="">Connecting...';

                AIChatMCP.addServer({endpoint: endpoint}, function(servers, error) {
                    saveBtn.disabled = false;
                    saveBtn.textContent = originalText;

                    if (error) {
                        AIChatError.show(error);
                        return;
                    }
                    core.configMode = 'manage-mcp';
                    core.render();
                });
                return;
            }

            var mcpRemoveBtn = target.closest('.ai-chat-mcp-remove-btn');
            if (mcpRemoveBtn) {
                ZatoConfirmButton.handleClick(mcpRemoveBtn, function(serverId) {
                    AIChatMCP.removeServer(serverId, function() {
                        core.render();
                    });
                });
                return;
            }

            if (target.classList.contains('ai-chat-mcp-enabled')) {
                var serverEl = target.closest('.ai-chat-mcp-server-row');
                var serverId = serverEl ? serverEl.getAttribute('data-server-id') : null;
                if (serverId) {
                    var enabled = target.checked;
                    AIChatMCP.updateServer(serverId, { enabled: enabled }, function() {
                        core.render();
                    });
                }
                return;
            }

            var mcpServerNameLink = target.closest('.ai-chat-mcp-server-name-link');
            if (mcpServerNameLink) {
                var serverId = mcpServerNameLink.getAttribute('data-server-id');
                AIChatMCP.selectedServer = AIChatMCP.getServerById(serverId);
                AIChatMCP.loadingTools = true;
                AIChatMCP.selectedServerTools = [];
                core.configMode = 'mcp-detail';
                core.render();
                AIChatMCP.loadToolsForServer(serverId, function() {
                    core.render();
                });
                return;
            }

            var mcpEditBtn = target.closest('.ai-chat-mcp-edit-btn');
            if (mcpEditBtn) {
                var serverId = mcpEditBtn.getAttribute('data-item-id');
                AIChatMCP.selectedServer = AIChatMCP.getServerById(serverId);
                core.configMode = 'edit-mcp';
                core.render();
                return;
            }

            var mcpEditSave = target.closest('#ai-chat-mcp-edit-save');
            if (mcpEditSave) {
                var serverId = mcpEditSave.getAttribute('data-server-id');
                var endpointInput = widget.querySelector('#ai-chat-mcp-edit-endpoint');
                var newEndpoint = endpointInput ? endpointInput.value.trim() : '';

                if (!newEndpoint) {
                    return;
                }

                var saveBtn = mcpEditSave;
                var originalText = saveBtn.textContent;
                saveBtn.disabled = true;
                saveBtn.innerHTML = '<img src="/static/img/spinner.svg" class="ai-chat-spinner-icon" alt="">Saving...';

                AIChatMCP.updateServer(serverId, { endpoint: newEndpoint }, function(servers, error) {
                    saveBtn.disabled = false;
                    saveBtn.textContent = originalText;

                    if (error) {
                        AIChatError.show(error);
                        return;
                    }
                    AIChatMCP.selectedServer = null;
                    core.configMode = 'manage-mcp';
                    core.render();
                });
                return;
            }

            if (target.classList.contains('ai-chat-config-save-button')) {
                var providerId = target.getAttribute('data-provider-id');
                AIChatSettings.saveApiKey(widget, providerId, function() {
                    core.needsConfig = false;
                    core.configMode = 'providers';
                    AIChatSettings.showConfigSuccess(widget, function() {
                        core.render();
                    });
                });
                return;
            }

            var configKeyRemove = target.closest('.ai-chat-config-key-remove');
            if (configKeyRemove) {
                ZatoConfirmButton.handleClick(configKeyRemove, function(providerId) {
                    AIChatSettings.removeApiKey(providerId, {
                        onNoKeysLeft: function() {
                            core.needsConfig = true;
                            core.configMode = 'providers';
                            core.cameFromChat = false;
                            core.hadKeyOnEntry = false;
                        },
                        onSuccess: function() {
                            core.render();
                        }
                    });
                });
                return;
            }

            var configKeyAdd = target.closest('.ai-chat-config-key-add');
            if (configKeyAdd) {
                var providerId = configKeyAdd.getAttribute('data-item-id');
                core.needsConfig = true;
                core.configMode = 'key-input';
                core.cameFromManageKeys = true;
                AIChatConfig.selectedProvider = providerId;
                core.render();
                return;
            }

            var configKeyEdit = target.closest('.ai-chat-config-key-edit');
            if (configKeyEdit) {
                var providerId = configKeyEdit.getAttribute('data-item-id');
                core.needsConfig = true;
                core.configMode = 'key-input';
                core.cameFromManageKeys = true;
                AIChatConfig.selectedProvider = providerId;
                core.render();
                return;
            }

            var contextBar = target.closest('.ai-chat-context-bar');
            if (contextBar && !target.closest('.ai-chat-context-help-link')) {
                e.preventDefault();
                e.stopPropagation();
                core.hideTooltip();
                var tooltip = contextBar.querySelector('.ai-chat-context-tooltip');
                if (tooltip) {
                    tooltip.classList.toggle('open');
                }
                return;
            }

            var contextHelpLink = target.closest('.ai-chat-context-help-link');
            if (contextHelpLink) {
                e.preventDefault();
                e.stopPropagation();
                var openTooltip = document.querySelector('.ai-chat-context-tooltip.open');
                if (openTooltip) {
                    openTooltip.classList.remove('open');
                }
                AIChatContextHelp.show();
                return;
            }
        },

        handleShowItems: function(btn) {
            var progressEl = btn.closest('.ai-tool-progress');
            if (!progressEl) return;

            var existingList = progressEl.parentNode.querySelector('.ai-tool-items-list');
            if (existingList) {
                existingList.remove();
                btn.textContent = 'Show';
                return;
            }

            var itemsJson = btn.getAttribute('data-items');
            var items = [];
            try { items = JSON.parse(itemsJson); } catch (e) {}
            if (!items.length) return;

            var listHtml = '<div class="ai-tool-items-list"><table>';
            for (var i = 0; i < items.length; i++) {
                listHtml += '<tr><td>' + items[i].type + '</td><td><a href="#">' + items[i].name + '</a></td></tr>';
            }
            listHtml += '</table></div>';

            progressEl.insertAdjacentHTML('afterend', listHtml);
            btn.textContent = 'Hide';
        },

        handleDiffTagClick: function(tag) {
            var fileName = tag.textContent;
            var progressEl = tag.closest('.ai-tool-progress');
            if (!progressEl) {
                return;
            }

            var diffWrapper = progressEl.querySelector('.ai-diff-wrapper[data-file="' + fileName + '"]');
            if (!diffWrapper) {
                return;
            }

            var isActive = tag.classList.contains('active');

            if (isActive) {
                tag.classList.remove('active');
                diffWrapper.style.display = 'none';
            } else {
                tag.classList.add('active');
                diffWrapper.style.display = 'block';

                var isNewFile = diffWrapper.querySelector('.ai-diff-new');
                if (!isNewFile) {
                    var container = diffWrapper.querySelector('.ai-diff-container');
                    if (container) {
                        AIChatDiff.navigateToHunk(container, 0);
                    }
                }
            }
        },

        handleDiffNavClick: function(btn) {
            var container = btn.closest('.ai-diff-container');
            if (!container) return;

            var currentHunk = parseInt(container.getAttribute('data-current-hunk') || '0', 10);
            var isUp = btn.classList.contains('ai-diff-nav-up');

            var newHunk = isUp ? currentHunk - 1 : currentHunk + 1;
            AIChatDiff.navigateToHunk(container, newHunk);
        },

        handleDiffCopy: function(btn) {
            var container = btn.closest('.ai-diff-container');
            if (!container) return;

            var content = '';
            if (btn.classList.contains('ai-diff-copy-file')) {
                content = container.getAttribute('data-new-content') || '';
            } else if (btn.classList.contains('ai-diff-copy-diff')) {
                content = container.getAttribute('data-diff-content') || '';
            }

            if (content) {
                var decoded = content.replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
                navigator.clipboard.writeText(decoded);
                this.showCopiedFeedback(btn);
            }
        },

        handleTimestampCopy: function(el) {
            var text = el.textContent;
            if (text) {
                navigator.clipboard.writeText(text);
                this.showCopiedFeedback(el);
            }
        },

        showCopiedFeedback: function(el) {
            var originalText = el.textContent;
            el.textContent = 'Copied';
            (function(e, o) {
                var start = Date.now();
                var check = function() {
                    if (Date.now() - start >= 1500) {
                        e.textContent = o;
                    } else {
                        requestAnimationFrame(check);
                    }
                };
                requestAnimationFrame(check);
            })(el, originalText);
        },

        handleRetry: function(btn, widget, core) {
            var tabId = btn.getAttribute('data-tab-id');
            if (!tabId) {
                return;
            }

            var tab = null;
            for (var i = 0; i < core.tabs.length; i++) {
                if (core.tabs[i].id === tabId) {
                    tab = core.tabs[i];
                    break;
                }
            }
            if (!tab || tab.messages.length < 1) {
                return;
            }

            var lastUserMsg = null;
            var lastAssistantMsgIndex = -1;
            for (var i = tab.messages.length - 1; i >= 0; i--) {
                if (tab.messages[i].role === 'assistant') {
                    lastAssistantMsgIndex = i;
                    break;
                }
            }

            for (var i = tab.messages.length - 1; i >= 0; i--) {
                if (tab.messages[i].role === 'user') {
                    lastUserMsg = tab.messages[i];
                    break;
                }
            }
            if (!lastUserMsg) {
                return;
            }

            if (lastAssistantMsgIndex > -1) {
                tab.messages = tab.messages.slice(0, lastAssistantMsgIndex);
            }

            core.saveState();
            core.render();

            var input = widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
            if (input) {
                input.textContent = lastUserMsg.content;
                AIChatStreaming.sendMessage(widget, core, tabId);
            }
        }
    };

    window.AIChatClickHandlers = AIChatClickHandlers;

})();
