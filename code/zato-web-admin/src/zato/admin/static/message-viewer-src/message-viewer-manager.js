import { getModuleLogger, LOG_LEVEL } from './debug-utils.js';
import { sampleMessage } from './sample-response.js';

const logger = getModuleLogger('message-viewer');
logger.setLevel(LOG_LEVEL.INFO);

export class MessageViewerManager {
    constructor() {
        this.searchDebounceTimer = null;
        this.lastSearchTerm = null;
        this.currentMatchIndex = undefined;
        this.messageData = null;
        this.boundSetDynamicHeight = this.setDynamicHeight.bind(this);
    }

    initialize(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            logger.error(`MessageViewerManager.initialize: container ${containerId} not found`);
            return;
        }

        const existingViewer = document.getElementById('message-viewer-panel');
        if (existingViewer) {
            logger.info('MessageViewerManager.initialize: viewer already exists');
            return;
        }

        const viewerPanel = document.createElement('div');
        viewerPanel.id = 'message-viewer-panel';
        viewerPanel.style.display = 'flex';
        viewerPanel.style.flexDirection = 'column';
        viewerPanel.style.flex = '1';
        viewerPanel.style.minHeight = '0';
        viewerPanel.innerHTML = `
            <div id="message-viewer-header">
                <div class="invoker-search-wrapper">
                    <input type="text" id="message-viewer-search" placeholder="Search message" class="invoker-message-search-input">
                    <span id="message-viewer-search-counter" class="invoker-search-counter"></span>
                </div>
                <input type="button" id="message-viewer-copy-btn" value="Copy" title="Copy to clipboard">
            </div>
            <div id="message-viewer-container" style="flex: 1; min-height: 0; display: flex; flex-direction: column;"></div>
        `;

        container.appendChild(viewerPanel);
        this.initializeControls();
        requestAnimationFrame(() => {
            this.setDynamicHeight();
        });
        window.addEventListener('resize', this.boundSetDynamicHeight);
        logger.info('MessageViewerManager.initialize: viewer initialized');
    }

    setDynamicHeight() {
        const wrapper = document.getElementById('message-viewer-wrapper');
        if (!wrapper) return;

        const rect = wrapper.getBoundingClientRect();
        const scrollbarMargin = 50;
        const maxHeight = window.innerHeight - rect.top - scrollbarMargin;
        
        wrapper.style.maxHeight = `${maxHeight}px`;
        logger.info(`MessageViewerManager.setDynamicHeight: set wrapper maxHeight to ${maxHeight}px (wrapper.top=${rect.top})`);
    }

    initializeControls() {
        const copyBtn = document.getElementById('message-viewer-copy-btn');
        const searchInput = document.getElementById('message-viewer-search');

        const savedSearchTerm = localStorage.getItem('message-viewer-search-term');

        if (savedSearchTerm && searchInput) {
            searchInput.value = savedSearchTerm;
            logger.info(`MessageViewerManager.initializeControls: restored search term="${savedSearchTerm}"`);
        }

        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                if (!this.messageData) return;
                const jsonText = JSON.stringify(this.messageData, null, 2);
                navigator.clipboard.writeText(jsonText).then(() => {
                    logger.info('MessageViewerManager.initializeControls: copied to clipboard');
                    
                    const btnRect = copyBtn.getBoundingClientRect();
                    const tooltip = document.createElement('span');
                    tooltip.className = 'invoker-copy-tooltip';
                    tooltip.textContent = 'Copied';
                    tooltip.style.position = 'fixed';
                    tooltip.style.top = `${btnRect.top - 32}px`;
                    tooltip.style.right = `${window.innerWidth - btnRect.right}px`;
                    document.body.appendChild(tooltip);
                    
                    setTimeout(() => {
                        tooltip.remove();
                    }, 800);
                }).catch(err => {
                    logger.error(`MessageViewerManager.initializeControls: copy failed - ${err.message}`);
                });
            });
        }

        if (searchInput) {
            searchInput.addEventListener('input', (event) => {
                const currentValue = event.target.value.trim();
                logger.info(`MessageViewerManager: input event: value="${currentValue}"`);
                
                this.updateMatchCounter(currentValue);
                
                if (this.searchDebounceTimer) {
                    clearTimeout(this.searchDebounceTimer);
                }
                
                this.searchDebounceTimer = setTimeout(() => {
                    localStorage.setItem('message-viewer-search-term', currentValue);
                    logger.info(`MessageViewerManager: saved search term="${currentValue}"`);
                    this.renderMessage();
                }, 100);
            });

            searchInput.addEventListener('keydown', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    const searchTerm = searchInput.value.trim();
                    if (searchTerm) {
                        this.scrollToNextMatch();
                    }
                }
                
                if (event.key === 'Escape') {
                    event.preventDefault();
                    event.stopPropagation();
                    searchInput.value = '';
                    localStorage.setItem('message-viewer-search-term', '');
                    this.lastSearchTerm = null;
                    this.currentMatchIndex = undefined;
                    this.updateMatchCounter('');
                    this.renderMessage();
                    logger.info('MessageViewerManager: cleared search term via Escape');
                }
            });
        }
    }

    setMessage(data) {
        this.messageData = data;
        this.renderMessage();
        requestAnimationFrame(() => {
            this.setDynamicHeight();
        });
    }

    renderMessage() {
        const container = document.getElementById('message-viewer-container');
        const searchInput = document.getElementById('message-viewer-search');
        if (!container) {
            logger.info('MessageViewerManager.renderMessage: container not found');
            return;
        }

        if (!this.messageData) {
            logger.info('MessageViewerManager.renderMessage: no message data');
            return;
        }

        const jsonText = JSON.stringify(this.messageData, null, 2);
        const searchTerm = searchInput ? searchInput.value.trim() : '';
        logger.info(`MessageViewerManager.renderMessage: searchTerm="${searchTerm}"`);
        
        if (searchTerm === this.lastSearchTerm) {
            logger.info(`MessageViewerManager.renderMessage: search term unchanged, skipping render`);
            return;
        }
        
        this.currentMatchIndex = undefined;
        this.lastSearchTerm = searchTerm;
        let displayText;

        if (searchTerm) {
            displayText = this.highlightSearchTerm(jsonText, searchTerm);
        } else {
            displayText = this.applySyntaxHighlighting(jsonText);
        }
        
        let display = document.getElementById('message-viewer-json-display');
        const preserveScroll = display ? display.scrollTop : 0;
        
        if (!display) {
            container.innerHTML = `<pre id="message-viewer-json-display">${displayText}</pre>`;
        } else {
            display.innerHTML = displayText;
            if (!searchTerm) {
                display.scrollTop = preserveScroll;
            }
        }
        
        if (searchTerm) {
            this.scrollToFirstMatch();
        }
    }

    updateMatchCounter(searchTerm) {
        const counter = document.getElementById('message-viewer-search-counter');
        const searchInput = document.getElementById('message-viewer-search');
        if (!counter) return;

        if (!searchTerm) {
            counter.textContent = '';
            return;
        }

        let matchCount = 0;
        let currentIndex = undefined;

        const jsonText = JSON.stringify(this.messageData, null, 2);
        let searchRegex;

        if (searchTerm.includes('=')) {
            const [key, value] = searchTerm.split('=');
            const trimmedKey = key.trim();
            const trimmedValue = value ? value.trim() : '';
            
            if (trimmedKey && trimmedValue) {
                const escapedKey = trimmedKey.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                const escapedValue = trimmedValue.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                
                const patterns = [
                    `"${escapedKey}"\\s*:\\s*"[^"]*${escapedValue}[^"]*"`,
                    `"${escapedKey}"\\s*:\\s*[^,\\n\\}]*${escapedValue}[^,\\n\\}]*`
                ];
                
                searchRegex = new RegExp(`(${patterns.join('|')})`, 'gi');
            } else if (trimmedKey) {
                const escapedKey = trimmedKey.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                searchRegex = new RegExp(`("${escapedKey}")`, 'gi');
            }
        } else {
            const escapedSearchForRegex = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            searchRegex = new RegExp(`(${escapedSearchForRegex})`, 'gi');
        }

        if (searchRegex) {
            const matches = jsonText.match(searchRegex);
            matchCount = matches ? matches.length : 0;
        }
        
        currentIndex = this.currentMatchIndex;

        let counterText;
        if (matchCount === 0) {
            counterText = ' (0 matches)';
        } else if (matchCount === 1) {
            counterText = ' (1 match)';
        } else if (currentIndex !== undefined) {
            counterText = ` (${currentIndex + 1} / ${matchCount} matches)`;
        } else {
            counterText = ` (${matchCount} matches)`;
        }
        
        counter.textContent = counterText;
        
        if (searchInput) {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            const computedStyle = window.getComputedStyle(searchInput);
            context.font = computedStyle.fontSize + ' ' + computedStyle.fontFamily;
            const textWidth = context.measureText(searchTerm).width;
            const paddingLeft = parseFloat(computedStyle.paddingLeft) || 0;
            counter.style.left = `${paddingLeft + textWidth + 8}px`;
        }
    }

    scrollToFirstMatch() {
        const container = document.getElementById('message-viewer-container');
        const display = document.getElementById('message-viewer-json-display');
        const firstMatch = display?.querySelector('.search-highlight');
        const searchInput = document.getElementById('message-viewer-search');
        const searchTerm = searchInput ? searchInput.value.trim() : '';
        
        if (firstMatch && container && display) {
            this.currentMatchIndex = 0;
            const displayRect = display.getBoundingClientRect();
            const matchRect = firstMatch.getBoundingClientRect();
            const lineHeight = parseFloat(getComputedStyle(display).lineHeight) || 20;
            const offset = lineHeight * 8;
            
            const relativeTop = matchRect.top - displayRect.top + display.scrollTop;
            const scrollPosition = Math.max(0, relativeTop - offset);
            
            display.scrollTop = scrollPosition;
            this.updateMatchCounter(searchTerm);
        }
    }

    scrollToNextMatch() {
        const searchInput = document.getElementById('message-viewer-search');
        const searchTerm = searchInput ? searchInput.value.trim() : '';
        
        const display = document.getElementById('message-viewer-json-display');
        const matches = display?.querySelectorAll('.search-highlight');
        
        if (!matches || matches.length === 0) return;
        
        if (this.currentMatchIndex === undefined) {
            this.currentMatchIndex = 0;
        } else {
            this.currentMatchIndex = (this.currentMatchIndex + 1) % matches.length;
        }
        
        const currentMatch = matches[this.currentMatchIndex];
        const displayRect = display.getBoundingClientRect();
        const matchRect = currentMatch.getBoundingClientRect();
        const lineHeight = parseFloat(getComputedStyle(display).lineHeight) || 20;
        const offset = lineHeight * 8;
        
        const relativeTop = matchRect.top - displayRect.top + display.scrollTop;
        const scrollPosition = Math.max(0, relativeTop - offset);
        
        display.scrollTop = scrollPosition;
        
        logger.info(`scrollToNextMatch: scrolled to match ${this.currentMatchIndex + 1} of ${matches.length}`);
        this.updateMatchCounter(searchTerm);
    }

    applySyntaxHighlighting(text, wrapMatchLines = false, matchIndices = []) {
        const lines = text.split('\n');
        
        return lines.map((line, index) => {
            let highlighted = this.escapeHtml(line);
            
            highlighted = highlighted.replace(/"([^"]+)"(\s*):/g, '<span class="json-key">"$1"</span>$2:');
            
            const stringPattern = /:\s*"([^"]*)"/g;
            highlighted = highlighted.replace(stringPattern, ': <span class="json-string">"$1"</span>');
            
            if (!highlighted.includes('json-string')) {
                highlighted = highlighted.replace(/:\s*(-?\d+\.?\d*)([,\s\r}]|$)/g, ': <span class="json-number">$1</span>$2');
                highlighted = highlighted.replace(/:\s*(true|false)([,\s\r}]|$)/g, ': <span class="json-boolean">$1</span>$2');
                highlighted = highlighted.replace(/:\s*(null)([,\s\r}]|$)/g, ': <span class="json-null">$1</span>$2');
            }
            
            if (wrapMatchLines && matchIndices.includes(index)) {
                highlighted = `<span class="match-line">${highlighted}</span>`;
            }
            
            return highlighted;
        }).join('\n');
    }

    highlightSearchTerm(text, searchTerm) {
        if (!searchTerm) return this.applySyntaxHighlighting(text);

        const lines = text.split('\n');
        const matchingLineIndices = [];
        let searchRegex;

        if (searchTerm.includes('=')) {
            const [key, value] = searchTerm.split('=');
            const trimmedKey = key.trim();
            const trimmedValue = value ? value.trim() : '';
            
            if (trimmedKey && trimmedValue) {
                const escapedKey = trimmedKey.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                const escapedValue = trimmedValue.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                
                const patterns = [
                    `"${escapedKey}"\\s*:\\s*"[^"]*${escapedValue}[^"]*"`,
                    `"${escapedKey}"\\s*:\\s*[^,\\n\\}]*${escapedValue}[^,\\n\\}]*`
                ];
                
                searchRegex = new RegExp(`(${patterns.join('|')})`, 'gi');
            } else if (trimmedKey) {
                const escapedKey = trimmedKey.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                searchRegex = new RegExp(`("${escapedKey}")`, 'gi');
            }
        } else {
            const escapedSearchForRegex = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            searchRegex = new RegExp(`(${escapedSearchForRegex})`, 'gi');
        }

        if (!searchRegex) return this.applySyntaxHighlighting(text);

        lines.forEach((line, index) => {
            if (searchRegex.test(line)) {
                matchingLineIndices.push(index);
            }
            searchRegex.lastIndex = 0;
        });

        const highlightedLines = lines.map((line, index) => {
            const parts = line.split(searchRegex);
            
            const highlighted = parts.map((part, partIndex) => {
                if (partIndex % 2 === 1) {
                    return `<span class="search-highlight">${this.applySyntaxHighlighting(part)}</span>`;
                }
                return this.applySyntaxHighlighting(part);
            }).join('');
            
            if (matchingLineIndices.includes(index)) {
                return `<span class="match-line">${highlighted}</span>`;
            }
            
            return highlighted;
        });

        return highlightedLines.join('\n');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
