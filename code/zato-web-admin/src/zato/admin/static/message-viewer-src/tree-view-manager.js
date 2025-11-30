import { logger } from './logger-tree-view.js';
import { JsonTreeBuilder } from './json-tree-builder.js';
import { TreeRenderer } from './tree-renderer.js';
import { VirtualScroller } from './virtual-scroller.js';

export class TreeViewManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container with id "${containerId}" not found`);
        }

        this.data = null;
        this.tree = null;
        this.flatData = [];
        this.collapsedPaths = new Set();
        this.builder = new JsonTreeBuilder();
        this.renderer = new TreeRenderer();
        this.scroller = null;
        this.searchTerm = '';
        this.currentMatchIndex = undefined;
        this.itemHeight = 33;

        this.boundHandleToggle = this.handleToggle.bind(this);
        this.boundHandleKeyClick = this.handleKeyClick.bind(this);
        this.boundHandleContextMenu = this.handleContextMenu.bind(this);
        this.boundHandleNodeHover = this.handleNodeHover.bind(this);
        this.boundHandleNodeLeave = this.handleNodeLeave.bind(this);
        this.contextMenuOpen = false;
        this.contextMenuEvent = null;

        logger.info('TreeViewManager: initialized');
    }

    setData(jsonData) {
        logger.info('TreeViewManager.setData: building tree from JSON data');
        logger.info(`TreeViewManager.setData: container=${this.container.id}, clientHeight=${this.container.clientHeight}`);

        this.data = jsonData;
        this.tree = this.builder.buildTree(jsonData);
        this.flatData = this.builder.flattenTree(this.tree, this.collapsedPaths);

        logger.info(`TreeViewManager.setData: flat data has ${this.flatData.length} items`);

        if (!this.scroller) {
            logger.info('TreeViewManager.setData: creating new VirtualScroller');
            this.container.innerHTML = '';
            this.scroller = new VirtualScroller(
                this.container,
                this.itemHeight,
                (item, lineNumber) => this.renderer.renderTreeNode(item, lineNumber)
            );
        }

        this.scroller.setItems(this.flatData);
        this.attachEventListeners();

        logger.info(`TreeViewManager.setData: rendered ${this.flatData.length} nodes`);
    }

    search(term) {
        console.log('TreeViewManager.search called:', JSON.stringify({
            term: term,
            termLength: term ? term.length : 0,
            isEmpty: term === '',
            previousSearchTerm: this.searchTerm
        }));
        logger.info(`TreeViewManager.search: term="${term}"`);

        if (this.searchTerm !== term) {
            this.currentMatchIndex = undefined;
        }

        this.searchTerm = term;
        this.renderer.setSearch(term);
        this.shouldScrollToMatch = !!term;

        if (term) {
            console.log('TreeViewManager.search: expanding matching nodes');
            this.expandMatchingNodes(term);
        } else {
            console.log('TreeViewManager.search: term is empty, no expansion');
        }

        console.log('TreeViewManager.search: calling refresh');
        this.refresh();
        console.log('TreeViewManager.search: refresh complete');
    }

    scrollToFirstMatch() {
        const viewport = this.scroller?.viewport;
        if (!viewport) return;

        const itemHeight = this.itemHeight;
        const offset = itemHeight * 8;

        const matchIndices = this.getMatchIndices(this.searchTerm);
        if (matchIndices.length === 0) {
            logger.info('TreeViewManager.scrollToFirstMatch: no matches found');
            this.currentMatchIndex = undefined;
            return;
        }

        this.currentMatchIndex = 0;
        const targetIndex = matchIndices[0];
        const itemPosition = targetIndex * itemHeight;
        const scrollPosition = Math.max(0, itemPosition - offset);
        viewport.scrollTop = scrollPosition;

        logger.info(`TreeViewManager.scrollToFirstMatch: scrolled to match 1 of ${matchIndices.length} at index ${targetIndex}`);
    }

    getMatchIndices(searchTerm) {
        const matchIndices = [];

        if (!searchTerm.includes('=') && /^\d+$/.test(searchTerm)) {
            const lineNumber = parseInt(searchTerm, 10);
            const lineIndex = lineNumber - 1;
            if (lineIndex >= 0 && lineIndex < this.flatData.length) {
                matchIndices.push(lineIndex);
            }
        }

        for (let i = 0; i < this.flatData.length; i++) {
            const node = this.flatData[i];
            if (searchTerm.includes('=')) {
                const [key, value] = searchTerm.split('=');
                const trimmedKey = key.trim();
                const trimmedValue = value ? value.trim() : '';
                if (trimmedKey && trimmedValue) {
                    const keyMatch = node.key && node.key.toLowerCase() === trimmedKey.toLowerCase();
                    const valueMatch = node.value && String(node.value).toLowerCase().includes(trimmedValue.toLowerCase());
                    if (keyMatch && valueMatch) {
                        matchIndices.push(i);
                    }
                }
            } else if (searchTerm) {
                const lowerTerm = searchTerm.toLowerCase();
                const keyMatch = node.key && node.key.toLowerCase().includes(lowerTerm);
                const valueMatch = node.value && String(node.value).toLowerCase().includes(lowerTerm);
                if (keyMatch || valueMatch) {
                    if (!matchIndices.includes(i)) {
                        matchIndices.push(i);
                    }
                }
            }
        }
        return matchIndices;
    }

    getMatchCount(searchTerm) {
        if (!searchTerm) return 0;
        return this.getMatchIndices(searchTerm).length;
    }

    scrollToNextMatch() {
        const viewport = this.scroller?.viewport;
        if (!viewport) return;

        const itemHeight = this.itemHeight;
        const offset = itemHeight * 8;

        const matchIndices = this.getMatchIndices(this.searchTerm);

        if (matchIndices.length === 0) {
            logger.info('TreeViewManager.scrollToNextMatch: no matches found');
            this.currentMatchIndex = undefined;
            return;
        }

        if (this.currentMatchIndex === undefined) {
            this.currentMatchIndex = 0;
        } else {
            this.currentMatchIndex = (this.currentMatchIndex + 1) % matchIndices.length;
        }

        const targetIndex = matchIndices[this.currentMatchIndex];
        const itemPosition = targetIndex * itemHeight;
        const scrollPosition = Math.max(0, itemPosition - offset);
        viewport.scrollTop = scrollPosition;

        logger.info(`TreeViewManager.scrollToNextMatch: scrolled to match ${this.currentMatchIndex + 1} of ${matchIndices.length} at index ${targetIndex}`);
    }

    getCurrentMatchIndex() {
        return this.currentMatchIndex;
    }

    expandMatchingNodes(term) {
        const pathsToExpand = new Set();

        let keyPattern = null;
        let valuePattern = null;

        if (term.includes('=')) {
            const [key, value] = term.split('=');
            const trimmedKey = key.trim();
            const trimmedValue = value ? value.trim() : '';

            if (trimmedKey) {
                keyPattern = trimmedKey.toLowerCase();
            }
            if (trimmedValue) {
                valuePattern = trimmedValue.toLowerCase();
            }
        }

        const checkNode = (node) => {
            let isMatch = false;

            if (keyPattern && valuePattern) {
                const keyMatch = node.key && node.key.toLowerCase() === keyPattern;
                const valueMatch = node.value && String(node.value).toLowerCase().includes(valuePattern);
                isMatch = keyMatch && valueMatch;
            } else if (keyPattern) {
                isMatch = node.key && node.key.toLowerCase().includes(keyPattern);
            } else {
                const lowerTerm = term.toLowerCase();
                const keyMatch = node.key && node.key.toLowerCase().includes(lowerTerm);
                const valueMatch = node.value && String(node.value).toLowerCase().includes(lowerTerm);
                isMatch = keyMatch || valueMatch;
            }

            if (isMatch) {
                let currentPath = node.path;
                while (currentPath) {
                    const lastDotIndex = currentPath.lastIndexOf('.');
                    const lastBracketIndex = currentPath.lastIndexOf('[');
                    const lastIndex = Math.max(lastDotIndex, lastBracketIndex);

                    if (lastIndex === -1) break;

                    currentPath = currentPath.substring(0, lastIndex);
                    if (currentPath) {
                        pathsToExpand.add(currentPath);
                    }
                }
            }

            if (node.children) {
                for (const child of node.children) {
                    checkNode(child);
                }
            }
        };

        checkNode(this.tree);

        for (const path of pathsToExpand) {
            this.collapsedPaths.delete(path);
        }

        logger.info(`TreeViewManager.expandMatchingNodes: expanded ${pathsToExpand.size} parent nodes`);
    }

    handleToggle(event) {
        const toggleElement = event.target.closest('.tree-toggle');
        if (!toggleElement) return;

        const path = toggleElement.dataset.path || '';

        const container = document.getElementById('message-viewer-container');
        const header = document.getElementById('message-viewer-header');
        const viewport = this.scroller?.viewport;

        console.log('=== BEFORE TOGGLE ===', JSON.stringify({
            path: path,
            containerHeight: container?.clientHeight,
            containerScrollHeight: container?.scrollHeight,
            headerHeight: header?.clientHeight,
            headerOffsetTop: header?.offsetTop,
            viewportHeight: viewport?.clientHeight,
            viewportScrollHeight: viewport?.scrollHeight,
            flatDataLength: this.flatData.length,
            collapsedPathsCount: this.collapsedPaths.size
        }));

        logger.info(`TreeViewManager.handleToggle: path="${path}"`);

        if (this.collapsedPaths.has(path)) {
            this.collapsedPaths.delete(path);
            console.log('=== EXPANDING path ===', path);
        } else {
            this.collapsedPaths.add(path);
            console.log('=== COLLAPSING path ===', path);
        }

        this.refresh();

        setTimeout(() => {
            console.log('=== AFTER TOGGLE (async) ===', JSON.stringify({
                path: path,
                containerHeight: container?.clientHeight,
                containerScrollHeight: container?.scrollHeight,
                headerHeight: header?.clientHeight,
                headerOffsetTop: header?.offsetTop,
                viewportHeight: viewport?.clientHeight,
                viewportScrollHeight: viewport?.scrollHeight,
                flatDataLength: this.flatData.length,
                collapsedPathsCount: this.collapsedPaths.size
            }));
        }, 100);
    }

    refresh() {
        const container = document.getElementById('message-viewer-container');
        const header = document.getElementById('message-viewer-header');
        const viewport = this.scroller?.viewport;

        console.log('=== REFRESH START ===', JSON.stringify({
            containerHeight: container?.clientHeight,
            headerHeight: header?.clientHeight,
            headerOffsetTop: header?.offsetTop,
            viewportHeight: viewport?.clientHeight,
            currentFlatDataLength: this.flatData.length
        }));

        logger.info('TreeViewManager.refresh: rebuilding flat data');

        const scrollTop = this.scroller?.viewport?.scrollTop || 0;
        const shouldScrollToMatch = this.shouldScrollToMatch;
        this.shouldScrollToMatch = false;

        this.flatData = this.builder.flattenTree(this.tree, this.collapsedPaths);

        console.log('=== AFTER FLATTEN ===', JSON.stringify({
            newFlatDataLength: this.flatData.length,
            containerHeight: container?.clientHeight,
            headerOffsetTop: header?.offsetTop,
            viewportHeight: viewport?.clientHeight
        }));

        if (this.scroller) {
            console.log('=== BEFORE setItems ===', JSON.stringify({
                containerHeight: container?.clientHeight,
                viewportHeight: viewport?.clientHeight
            }));

            this.scroller.setItems(this.flatData);

            console.log('=== AFTER setItems ===', JSON.stringify({
                containerHeight: container?.clientHeight,
                viewportHeight: viewport?.clientHeight,
                headerOffsetTop: header?.offsetTop
            }));

            if (shouldScrollToMatch) {
                this.scrollToFirstMatch();
            } else {
                requestAnimationFrame(() => {
                    this.scroller.viewport.scrollTop = scrollTop;
                });
            }

            this.attachEventListeners();
        }
    }

    attachEventListeners() {
        this.container.removeEventListener('click', this.boundHandleToggle);
        this.container.addEventListener('click', this.boundHandleToggle);
        this.container.removeEventListener('click', this.boundHandleKeyClick);
        this.container.addEventListener('click', this.boundHandleKeyClick);
        this.container.removeEventListener('contextmenu', this.boundHandleContextMenu);
        this.container.addEventListener('contextmenu', this.boundHandleContextMenu);
        this.container.removeEventListener('mouseenter', this.boundHandleNodeHover, true);
        this.container.addEventListener('mouseenter', this.boundHandleNodeHover, true);
        this.container.removeEventListener('mouseleave', this.boundHandleNodeLeave, true);
        this.container.addEventListener('mouseleave', this.boundHandleNodeLeave, true);
    }

    handleNodeHover(event) {
        const nodeWrapper = event.target.closest('.tree-node-wrapper');
        if (!nodeWrapper) return;

        const nodeElement = nodeWrapper.querySelector('.tree-node');
        if (!nodeElement) return;

        const path = nodeElement.dataset.path;
        if (path === undefined || path === null) return;

        const node = this.flatData.find(n => n.path === path);
        if (!node) return;

        const lineNumber = nodeWrapper.querySelector('.tree-line-number')?.textContent || '';
        const displayPath = path === '' ? '/' : '/' + path.replace(/\.\[/g, '[').replace(/\./g, '/');
        const value = node.value !== undefined ? String(node.value) : '';
        const maxValueLength = 50;
        const truncatedValue = value.length > maxValueLength ? value.substring(0, maxValueLength) + '[...]' : value;

        const pathDisplay = document.getElementById('message-viewer-path-display');
        if (pathDisplay) {
            const prefix = '<span class="path-prefix">200 OK | 125 ms | 37.5 KB</span>';
            const separator = '<span class="path-separator">|</span>';
            if (node.collapsible) {
                pathDisplay.innerHTML = `${prefix} ${separator} <span class="path-value">${lineNumber} ${displayPath}</span>`;
            } else {
                pathDisplay.innerHTML = `${prefix} ${separator} <span class="path-value">${lineNumber} ${displayPath}: ${truncatedValue}</span>`;
            }
        }
    }

    handleNodeLeave(event) {
        const nodeWrapper = event.target.closest('.tree-node-wrapper');
        if (!nodeWrapper) return;

        const pathDisplay = document.getElementById('message-viewer-path-display');
        if (pathDisplay) {
            pathDisplay.innerHTML = '<span class="path-prefix">200 OK | 125 ms | 37.5 KB</span> <span class="path-separator">|</span>';
        }
    }

    clear() {
        if (this.scroller) {
            this.scroller.destroy();
            this.scroller = null;
        }

        this.container.removeEventListener('click', this.boundHandleToggle);
        this.container.removeEventListener('click', this.boundHandleKeyClick);
        this.container.removeEventListener('contextmenu', this.boundHandleContextMenu);
        this.container.removeEventListener('mouseenter', this.boundHandleNodeHover, true);
        this.container.removeEventListener('mouseleave', this.boundHandleNodeLeave, true);
        this.closeContextMenu();
        this.container.innerHTML = '';

        this.tree = null;
        this.flatData = [];
        this.collapsedPaths.clear();
        this.searchTerm = '';
        this.data = null;
        this.shouldScrollToMatch = false;

        logger.info('TreeViewManager.clear: cleared all data');
    }

    handleKeyClick(event) {
        const keyElement = event.target.closest('.tree-key');
        if (keyElement) {
            event.stopPropagation();
            const treeNode = keyElement.closest('.tree-node');
            const path = treeNode?.dataset.path || '';
            const flatNode = this.flatData.find(n => n.path === path);

            if (flatNode && flatNode.collapsible) {
                const data = this.getDataByPath(path);
                if (data !== undefined) {
                    const jsonText = JSON.stringify(data, null, 2);
                    navigator.clipboard.writeText(jsonText).then(() => {
                        logger.info(`TreeViewManager.handleKeyClick: copied children JSON for path "${path}"`);
                        this.showCopiedTooltip(event, 'JSON copied');
                    }).catch(err => {
                        logger.error(`TreeViewManager.handleKeyClick: copy failed - ${err.message}`);
                    });
                    return;
                }
            }

            const keyText = keyElement.textContent.trim();
            navigator.clipboard.writeText(keyText).then(() => {
                logger.info(`TreeViewManager.handleKeyClick: copied key "${keyText}"`);
                this.showCopiedTooltip(event, 'Key copied');
            }).catch(err => {
                logger.error(`TreeViewManager.handleKeyClick: copy failed - ${err.message}`);
            });
            return;
        }

        const valueElement = event.target.closest('.tree-value-string, .tree-value-number, .tree-value-boolean, .tree-value-null, .tree-value-undefined');
        if (valueElement) {
            event.stopPropagation();
            const valueText = valueElement.textContent.trim();
            navigator.clipboard.writeText(valueText).then(() => {
                logger.info(`TreeViewManager.handleKeyClick: copied value "${valueText}"`);
                this.showCopiedTooltip(event, 'Value copied');
            }).catch(err => {
                logger.error(`TreeViewManager.handleKeyClick: copy failed - ${err.message}`);
            });
            return;
        }
    }

    getDataByPath(path) {
        if (!this.data) return undefined;
        if (!path || path === '') return this.data;

        const parts = path.split(/\.|\[|\]/).filter(p => p !== '');
        let current = this.data;

        for (const part of parts) {
            if (current === null || current === undefined) return undefined;
            current = current[part];
        }

        return current;
    }

    handleContextMenu(event) {
        const keyElement = event.target.closest('.tree-key');
        if (!keyElement) return;

        const treeNode = keyElement.closest('.tree-node');
        if (!treeNode) return;

        event.preventDefault();
        event.stopPropagation();

        const path = treeNode.dataset.path || '';

        logger.info(`TreeViewManager.handleContextMenu: path="${path}"`);

        const flatNode = this.flatData.find(n => n.path === path);
        if (!flatNode) {
            logger.warn(`TreeViewManager.handleContextMenu: no flat node found for path="${path}"`);
            return;
        }

        this.showContextMenu(event, flatNode);
    }

    showContextMenu(event, node) {
        this.closeContextMenu();
        this.contextMenuEvent = event;

        const menu = document.createElement('div');
        menu.id = 'tree-context-menu';
        menu.className = 'tree-context-menu';

        const canExpand = node.collapsible && node.collapsed;
        const canCollapse = node.collapsible && !node.collapsed;

        const expandOption = document.createElement('div');
        expandOption.className = `tree-context-menu-item ${!canExpand ? 'disabled' : ''}`;
        expandOption.textContent = 'Expand';
        if (canExpand) {
            expandOption.addEventListener('click', () => {
                this.collapsedPaths.delete(node.path);
                this.refresh();
                this.closeContextMenu();
            });
        }

        const separator = document.createElement('div');
        separator.className = 'tree-context-menu-separator';

        const collapseOption = document.createElement('div');
        collapseOption.className = `tree-context-menu-item ${!canCollapse ? 'disabled' : ''}`;
        collapseOption.textContent = 'Collapse';
        if (canCollapse) {
            collapseOption.addEventListener('click', () => {
                this.collapsedPaths.add(node.path);
                this.refresh();
                this.closeContextMenu();
            });
        }

        const separator2 = document.createElement('div');
        separator2.className = 'tree-context-menu-separator';

        const copyPathOption = document.createElement('div');
        copyPathOption.className = 'tree-context-menu-item';
        copyPathOption.textContent = 'Copy path';
        copyPathOption.addEventListener('click', () => {
            const displayPath = node.path === '' ? '/' : '/' + node.path.replace(/\.\[/g, '[').replace(/\./g, '/');
            const savedEvent = this.contextMenuEvent;
            this.closeContextMenu();
            navigator.clipboard.writeText(displayPath).then(() => {
                this.showCopiedTooltip(savedEvent, 'Path copied');
            });
        });

        menu.appendChild(expandOption);
        menu.appendChild(separator);
        menu.appendChild(collapseOption);
        menu.appendChild(separator2);
        menu.appendChild(copyPathOption);

        menu.style.position = 'fixed';
        menu.style.left = `${event.clientX}px`;
        menu.style.top = `${event.clientY}px`;

        document.body.appendChild(menu);
        this.contextMenuOpen = true;

        const closeOnClick = (e) => {
            if (!e.target.closest('#tree-context-menu')) {
                this.closeContextMenu();
                document.removeEventListener('click', closeOnClick);
                document.removeEventListener('keydown', closeOnEscape);
            }
        };

        const closeOnEscape = (e) => {
            if (e.key === 'Escape') {
                this.closeContextMenu();
                document.removeEventListener('click', closeOnClick);
                document.removeEventListener('keydown', closeOnEscape);
            }
        };

        setTimeout(() => {
            document.addEventListener('click', closeOnClick);
            document.addEventListener('keydown', closeOnEscape);
        }, 0);
    }

    closeContextMenu() {
        const menu = document.getElementById('tree-context-menu');
        if (menu) {
            menu.remove();
        }
        this.contextMenuOpen = false;
        this.contextMenuEvent = null;
    }

    showCopiedTooltip(event, message) {
        if (!event) return;

        const tooltip = document.createElement('span');
        tooltip.className = 'invoker-copy-tooltip';
        tooltip.textContent = message;
        tooltip.style.position = 'fixed';
        tooltip.style.top = `${event.clientY - 32}px`;
        tooltip.style.left = `${event.clientX}px`;
        tooltip.style.transform = 'translateX(-50%)';
        document.body.appendChild(tooltip);

        setTimeout(() => {
            tooltip.remove();
        }, 800);
    }

    destroy() {
        this.clear();
        logger.info('TreeViewManager: destroyed');
    }
}
