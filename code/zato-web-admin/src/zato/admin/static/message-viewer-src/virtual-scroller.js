import { logger } from './logger-tree-view.js';

export class VirtualScroller {
    constructor(container, itemHeight, renderItemCallback) {
        this.container = container;
        this.itemHeight = itemHeight;
        this.renderItemCallback = renderItemCallback;
        
        this.items = [];
        this.visibleStart = 0;
        this.visibleEnd = 0;
        this.bufferSize = 5;
        this.delayedRenderTimeout = null;
        
        this.scrollContent = document.createElement('div');
        this.scrollContent.className = 'virtual-scroll-content';
        
        this.viewport = document.createElement('div');
        this.viewport.className = 'virtual-scroll-viewport';
        this.viewport.appendChild(this.scrollContent);
        
        this.container.appendChild(this.viewport);
        
        this.boundHandleScroll = this.handleScroll.bind(this);
        this.viewport.addEventListener('scroll', this.boundHandleScroll);
        
        const messageViewerContainer = document.getElementById('message-viewer-container');
        if (messageViewerContainer) {
            const resizeObserver = new ResizeObserver(entries => {
                for (const entry of entries) {
                    console.log('=== RESIZE OBSERVED ===', JSON.stringify({
                        target: entry.target.id || entry.target.className,
                        contentBoxSize: entry.contentBoxSize?.[0] ? {
                            blockSize: entry.contentBoxSize[0].blockSize,
                            inlineSize: entry.contentBoxSize[0].inlineSize
                        } : null,
                        borderBoxSize: entry.borderBoxSize?.[0] ? {
                            blockSize: entry.borderBoxSize[0].blockSize,
                            inlineSize: entry.borderBoxSize[0].inlineSize
                        } : null,
                        contentRect: {
                            width: entry.contentRect.width,
                            height: entry.contentRect.height
                        }
                    }));
                }
            });
            resizeObserver.observe(messageViewerContainer);
            resizeObserver.observe(this.container);
            resizeObserver.observe(this.viewport);
            resizeObserver.observe(this.scrollContent);
        }
        
        const mutationObserver = new MutationObserver(mutations => {
            for (const mutation of mutations) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    const target = mutation.target;
                    console.log('=== STYLE MUTATION ===', JSON.stringify({
                        targetId: target.id || target.className,
                        oldValue: mutation.oldValue,
                        newValue: target.getAttribute('style'),
                        computedHeight: getComputedStyle(target).height,
                        clientHeight: target.clientHeight
                    }));
                }
            }
        });
        mutationObserver.observe(this.scrollContent, {
            attributes: true,
            attributeOldValue: true,
            attributeFilter: ['style']
        });
        
        logger.info(`VirtualScroller: initialized, container clientHeight=${this.container.clientHeight}, viewport clientHeight=${this.viewport.clientHeight}`);
    }

    setItems(items) {
        const container = document.getElementById('message-viewer-container');
        const header = document.getElementById('message-viewer-header');
        
        console.log('=== setItems START ===', JSON.stringify({
            itemsLength: items.length,
            containerClientHeight: this.container.clientHeight,
            viewportClientHeight: this.viewport.clientHeight,
            messageViewerContainerHeight: container?.clientHeight,
            headerOffsetTop: header?.offsetTop
        }));
        
        logger.info(`VirtualScroller.setItems: setting ${items.length} items`);
        logger.info(`VirtualScroller.setItems: container clientHeight=${this.container.clientHeight}, viewport clientHeight=${this.viewport.clientHeight}`);
        this.items = items;
        
        console.log('=== BEFORE updateScrollHeight ===', JSON.stringify({
            containerHeight: container?.clientHeight,
            viewportHeight: this.viewport.clientHeight
        }));
        
        this.updateScrollHeight();
        
        console.log('=== AFTER updateScrollHeight ===', JSON.stringify({
            containerHeight: container?.clientHeight,
            viewportHeight: this.viewport.clientHeight,
            contentHeight: this.scrollContent.style.height
        }));
        
        this.render();
        
        console.log('=== AFTER render ===', JSON.stringify({
            containerHeight: container?.clientHeight,
            viewportHeight: this.viewport.clientHeight,
            headerOffsetTop: header?.offsetTop
        }));
        
        if (this.viewport.clientHeight === 0) {
            logger.warn('VirtualScroller.setItems: viewport height is 0, scheduling re-render in 100ms');
            if (this.delayedRenderTimeout) {
                clearTimeout(this.delayedRenderTimeout);
            }
            this.delayedRenderTimeout = setTimeout(() => {
                logger.info(`VirtualScroller.setItems: re-checking dimensions: viewport clientHeight=${this.viewport.clientHeight}`);
                if (this.viewport.clientHeight > 0) {
                    logger.info('VirtualScroller.setItems: viewport now has height, re-rendering');
                    this.render();
                }
                this.delayedRenderTimeout = null;
            }, 100);
        }
    }

    updateScrollHeight() {
        const container = document.getElementById('message-viewer-container');
        const viewport = this.viewport;
        
        console.log('=== updateScrollHeight START ===', JSON.stringify({
            itemsLength: this.items.length,
            itemHeight: this.itemHeight,
            containerHeight: container?.clientHeight,
            viewportHeight: viewport?.clientHeight,
            oldContentHeight: this.scrollContent.style.height
        }));
        
        const totalHeight = this.items.length * this.itemHeight;
        const minHeight = this.viewport.clientHeight + 20;
        const finalHeight = Math.max(totalHeight, minHeight);
        this.scrollContent.style.height = `${finalHeight}px`;
        
        console.log('=== updateScrollHeight END ===', JSON.stringify({
            newContentHeight: this.scrollContent.style.height,
            totalHeight: totalHeight,
            minHeight: minHeight,
            finalHeight: finalHeight,
            containerHeight: container?.clientHeight,
            viewportHeight: viewport?.clientHeight
        }));
        
        logger.info(`VirtualScroller.updateScrollHeight: total height=${finalHeight}px`);
    }

    handleScroll() {
        this.render();
    }

    calculateVisibleRange() {
        const scrollTop = this.viewport.scrollTop;
        const viewportHeight = this.viewport.clientHeight;
        
        logger.info(`VirtualScroller.calculateVisibleRange: scrollTop=${scrollTop}, viewportHeight=${viewportHeight}`);
        
        const start = Math.floor(scrollTop / this.itemHeight);
        const end = Math.ceil((scrollTop + viewportHeight) / this.itemHeight);
        
        this.visibleStart = Math.max(0, start - this.bufferSize);
        this.visibleEnd = Math.min(this.items.length, end + this.bufferSize);
        
        logger.info(`VirtualScroller.calculateVisibleRange: visibleStart=${this.visibleStart}, visibleEnd=${this.visibleEnd}`);
    }

    render() {
        this.calculateVisibleRange();
        
        logger.info(`VirtualScroller.render: rendering items ${this.visibleStart} to ${this.visibleEnd}`);
        
        const fragment = document.createDocumentFragment();
        const wrapper = document.createElement('div');
        wrapper.className = 'virtual-scroll-items';
        wrapper.style.transform = `translateY(${this.visibleStart * this.itemHeight}px)`;
        
        for (let i = this.visibleStart; i < this.visibleEnd; i++) {
            const item = this.items[i];
            if (item) {
                const itemElement = document.createElement('div');
                itemElement.className = 'virtual-scroll-item';
                itemElement.style.height = `${this.itemHeight}px`;
                itemElement.innerHTML = this.renderItemCallback(item, i + 1);
                wrapper.appendChild(itemElement);
            }
        }
        
        fragment.appendChild(wrapper);
        
        this.scrollContent.innerHTML = '';
        this.scrollContent.appendChild(fragment);
        
        logger.info(`VirtualScroller.render: rendered ${this.visibleEnd - this.visibleStart} DOM elements`);
    }

    scrollToIndex(index) {
        if (index < 0 || index >= this.items.length) {
            logger.warn(`VirtualScroller.scrollToIndex: invalid index=${index}`);
            return;
        }
        
        const scrollTop = index * this.itemHeight;
        this.viewport.scrollTop = scrollTop;
        
        logger.info(`VirtualScroller.scrollToIndex: scrolled to index=${index}, scrollTop=${scrollTop}`);
    }

    scrollToTop() {
        this.viewport.scrollTop = 0;
    }

    destroy() {
        this.viewport.removeEventListener('scroll', this.boundHandleScroll);
        this.container.innerHTML = '';
        logger.info('VirtualScroller: destroyed');
    }
}
