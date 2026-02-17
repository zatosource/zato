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

            var diffCopyBtn = target.closest('.ai-diff-copy');
            if (diffCopyBtn) {
                this.handleDiffCopy(diffCopyBtn);
                return;
            }

            var diffTag = target.closest('.ai-tool-tag[data-diff]');
            if (diffTag) {
                console.log('[DIFF-CLICK] diffTag found:', diffTag);
                this.handleDiffTagClick(diffTag);
                return;
            }

            var anyTag = target.closest('.ai-tool-tag');
            if (anyTag) {
                console.log('[DIFF-CLICK] anyTag found but no data-diff:', anyTag, 'data-diff:', anyTag.getAttribute('data-diff'));
            }

            var showBtn = target.closest('.ai-tool-show-btn');
            if (showBtn) {
                this.handleShowItems(showBtn);
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

            if (target.id === 'ai-chat-tab-add') {
                AIChatTabActions.addTab(widget, core);
                return;
            }

            if (target.classList.contains('ai-chat-tab-close')) {
                var tabId = target.getAttribute('data-tab-id');
                AIChatTabActions.closeTab(widget, core, tabId);
                e.stopPropagation();
                return;
            }

            var tabElement = target.closest('.ai-chat-tab');
            if (tabElement && !target.classList.contains('ai-chat-tab-close')) {
                var tabId = tabElement.getAttribute('data-tab-id');
                AIChatTabActions.switchTab(widget, core, tabId);
                return;
            }

            if (target.classList.contains('ai-chat-send-button') || target.closest('.ai-chat-send-button')) {
                var button = target.classList.contains('ai-chat-send-button') ? target : target.closest('.ai-chat-send-button');
                var tabId = button.getAttribute('data-tab-id');
                if (button.classList.contains('ai-chat-stop-button')) {
                    AIChatStreaming.stopMessage(widget, core, tabId);
                } else {
                    AIChatStreaming.sendMessage(widget, core, tabId);
                }
                return;
            }

            if (target.classList.contains('ai-chat-options-button') || target.closest('.ai-chat-options-button')) {
                var optionsBtn = target.classList.contains('ai-chat-options-button') ? target : target.closest('.ai-chat-options-button');
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
                AIChatSettings.handleBackClick(core.configMode, core.cameFromChat, core.hadKeyOnEntry, {
                    onReturnToChat: function() {
                        core.cameFromChat = false;
                        core.needsConfig = false;
                        core.configMode = 'providers';
                        AIChatConfig.selectedProvider = null;
                        core.render();
                    },
                    onShowProviders: function() {
                        core.needsConfig = true;
                        core.configMode = 'providers';
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
                AIChatConfig.selectedProvider = providerId;
                core.render();
                return;
            }

            var configKeyEdit = target.closest('.ai-chat-config-key-edit');
            if (configKeyEdit) {
                var providerId = configKeyEdit.getAttribute('data-item-id');
                core.needsConfig = true;
                core.configMode = 'key-input';
                AIChatConfig.selectedProvider = providerId;
                core.render();
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
            console.log('[DIFF-CLICK] handleDiffTagClick called, fileName:', fileName);
            
            var progressEl = tag.closest('.ai-tool-progress');
            console.log('[DIFF-CLICK] progressEl:', progressEl);
            if (!progressEl) {
                console.log('[DIFF-CLICK] no progressEl found');
                return;
            }

            var diffWrapper = progressEl.querySelector('.ai-diff-wrapper[data-file="' + fileName + '"]');
            console.log('[DIFF-CLICK] diffWrapper:', diffWrapper, 'selector:', '.ai-diff-wrapper[data-file="' + fileName + '"]');
            if (!diffWrapper) {
                console.log('[DIFF-CLICK] no diffWrapper found, all wrappers:', progressEl.querySelectorAll('.ai-diff-wrapper'));
                return;
            }

            var isActive = tag.classList.contains('active');
            console.log('[DIFF-CLICK] isActive:', isActive);

            if (isActive) {
                tag.classList.remove('active');
                diffWrapper.style.display = 'none';
                console.log('[DIFF-CLICK] hiding diff');
            } else {
                tag.classList.add('active');
                diffWrapper.style.display = 'block';
                console.log('[DIFF-CLICK] showing diff');

                var isNewFile = diffWrapper.querySelector('.ai-diff-new');
                if (!isNewFile) {
                    var firstChange = diffWrapper.querySelector('.ai-diff-added, .ai-diff-removed');
                    if (firstChange) {
                        var allLines = diffWrapper.querySelectorAll('.ai-diff-line');
                        var changeIndex = Array.prototype.indexOf.call(allLines, firstChange);
                        var scrollToIndex = Math.max(0, changeIndex - 4);
                        var scrollTarget = allLines[scrollToIndex];
                        if (scrollTarget) {
                            scrollTarget.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                    }
                }
            }
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
        }
    };

    window.AIChatClickHandlers = AIChatClickHandlers;

})();
