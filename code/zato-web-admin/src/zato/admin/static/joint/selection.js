// selection.js - Element selection functionality based on JointJS best practices

class Selection {
    constructor(graph, paper) {
        this.graph = graph;
        this.paper = paper;
        this.selectedElements = [];
        this.isPanning = false;
        this.eventProxies = [];

        // Add CSS styles for selection highlighting
        const color = "#2196F3";
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            .joint-element .selection-highlight {
                stroke: ${color};
                stroke-width: G3px;
                stroke-dasharray: 5,5;
            }
            .joint-link .selection-highlight {
                stroke: ${color};
                stroke-dasharray: 5,5;
                stroke-dashoffset: 10;
                animation: dash 0.5s infinite linear;
            }
            @keyframes dash {
                to {
                    stroke-dashoffset: 0;
                }
            }
        `;
        document.head.appendChild(styleElement);

        this.setupEventListeners();
        console.log("Selection manager initialized");
    }

    /**
     * Set up the event listeners for selection functionality
     */
    setupEventListeners() {
        // Selection on element click
        const handleElementClick = (elementView, evt) => {
            console.log("Element clicked:", elementView.model.id);
            const multiSelect = evt.ctrlKey || evt.shiftKey;
            this.selectElement(elementView.model, multiSelect);
            evt.stopPropagation(); // Prevent bubble to paper blank click
        };

        // Clear selection on blank click
        const handleBlankClick = () => {
            console.log("Blank area clicked, clearing selection");
            this.clearSelection();
        };

        // Keyboard shortcuts
        const handleKeyDown = (evt) => {
            // Ctrl+A to select all
            if ((evt.ctrlKey || evt.metaKey) && evt.key === 'a') {
                console.log("Select all shortcut");
                evt.preventDefault();
                this.selectAll();
            }

            // Delete or Backspace to remove selected elements
            if ((evt.key === 'Delete' || evt.key === 'Backspace') && this.selectedElements.length > 0) {
                console.log("Delete selection shortcut");
                evt.preventDefault();
                this.removeSelected();
            }

            // Escape to clear selection
            if (evt.key === 'Escape') {
                console.log("Clear selection shortcut");
                evt.preventDefault();
                this.clearSelection();
            }
        };

        // Register event handlers
        this.paper.on('element:pointerclick', handleElementClick);
        this.paper.on('blank:pointerclick', handleBlankClick);
        document.addEventListener('keydown', handleKeyDown);

        // Store proxies for cleanup
        this.eventProxies = [
            { target: this.paper, event: 'element:pointerclick', handler: handleElementClick },
            { target: this.paper, event: 'blank:pointerclick', handler: handleBlankClick },
            { target: document, event: 'keydown', handler: handleKeyDown }
        ];

        console.log("Event listeners set up");
    }

    /**
     * Select an element
     * @param {Object} element - The element to select
     * @param {boolean} multiSelect - Whether to add to existing selection
     */
    selectElement(element, multiSelect = false) {
        console.log("Selecting element", element.id, "multiSelect:", multiSelect);

        if (!element) return;

        // Check if element exists in graph
        if (!this.graph.getElements().find(el => el.id === element.id)) {
            console.log("Element not found in graph");
            return;
        }

        // For single select, clear previous selection
        if (!multiSelect) {
            this.clearSelection();
        }

        // Check if already selected
        if (this.selectedElements.some(el => el.id === element.id)) {
            if (multiSelect) {
                // If multiSelect, toggle the selection off
                console.log("Element already selected, removing from selection");
                this.unselectElement(element);
            }
            return;
        }

        // Add to selection and highlight
        this.selectedElements.push(element);
        this.highlightElement(element);
        console.log("Element selected, total selection:", this.selectedElements.length);
    }

    /**
     * Unselect a specific element
     * @param {Object} element - The element to unselect
     */
    unselectElement(element) {
        const index = this.selectedElements.findIndex(el => el.id === element.id);
        if (index !== -1) {
            console.log("Unselecting element:", element.id);
            this.unhighlightElement(element);
            this.selectedElements.splice(index, 1);
            console.log("Element unselected, remaining:", this.selectedElements.length);
        }
    }

    /**
     * Clear all selections
     */
    clearSelection() {
        console.log("Clearing all selections, count:", this.selectedElements.length);

        // Make a copy to avoid issues during iteration
        const elements = [...this.selectedElements];

        // Clear the array first to prevent any recursive issues
        this.selectedElements = [];

        // Then unhighlight all elements
        elements.forEach(element => {
            this.unhighlightElement(element);
        });

        console.log("All selections cleared");
    }

    /**
     * Select all elements in the graph
     */
    selectAll() {
        console.log("Selecting all elements");
        this.clearSelection();

        const elements = this.graph.getElements();
        console.log("Found elements:", elements.length);

        elements.forEach(element => {
            this.selectedElements.push(element);
            this.highlightElement(element);
        });

        console.log("All elements selected, count:", this.selectedElements.length);
    }

    /**
     * Remove selected elements
     */
    removeSelected() {
        if (this.selectedElements.length === 0) return;

        console.log("Removing selected elements, count:", this.selectedElements.length);

        if (confirm(`Delete ${this.selectedElements.length} selected element(s)?`)) {
            const elements = [...this.selectedElements];
            this.selectedElements = []; // Clear first to avoid callbacks issues

            elements.forEach(element => {
                console.log("Removing element:", element.id);
                element.remove();
            });

            console.log("Elements removed");
        }
    }

    /**
     * Highlight an element using the highlighters API
     * @param {Object} element - The element to highlight
     */
    highlightElement(element) {
        if (!element || !element.id) return;

        console.log("Highlighting element:", element.id);
        const view = element.findView(this.paper);

        if (!view) {
            console.log("View not found for element:", element.id);
            return;
        }

        // Use the highlighters API instead of view.highlight
        joint.highlighters.addClass.add(
            view,
            element.isElement() ? 'body' : 'line',
            'selection-highlight',
            { className: 'selection-highlight' }
        );
    }

    /**
     * Unhighlight an element
     * @param {Object} element - The element to unhighlight
     */
    unhighlightElement(element) {
        if (!element || !element.id) return;

        console.log("Unhighlighting element:", element.id);
        const view = element.findView(this.paper);

        if (!view) {
            console.log("View not found for element:", element.id);
            return;
        }

        // Use the highlighters API to remove the highlight
        joint.highlighters.addClass.remove(
            view,
            'selection-highlight'
        );
    }

    /**
     * Set panning mode
     * @param {boolean} isPanning - Whether panning is active
     */
    setPanningMode(isPanning) {
        console.log("Setting panning mode:", isPanning);
        this.isPanning = isPanning;

        // In panning mode, we might want to disable selection
        if (isPanning) {
            this.clearSelection();
        }
    }

    /**
     * Clean up event listeners
     */
    destroy() {
        console.log("Destroying selection manager");

        // Remove all event listeners
        this.eventProxies.forEach(proxy => {
            if (proxy.target.off) {
                proxy.target.off(proxy.event, proxy.handler);
            } else {
                proxy.target.removeEventListener(proxy.event, proxy.handler);
            }
        });

        // Clear selections
        this.clearSelection();
        this.eventProxies = [];

        console.log("Selection manager destroyed");
    }
}

// Function to register selection with panning mode
function registerSelectionWithPanMode(selection, panButton) {
    if (!selection || !panButton) {
        console.log("Cannot register selection with pan mode: missing parameters");
        return;
    }

    console.log("Registering selection with pan mode");
    const originalClickHandler = panButton.onclick;

    panButton.onclick = function(event) {
        // Call the original handler if it exists
        if (originalClickHandler) {
            originalClickHandler.call(this, event);
        }

        // Update the Selection instance's panning state
        const isPanning = this.textContent === 'Selection Mode';
        console.log("Pan button clicked, setting panning mode:", isPanning);
        selection.setPanningMode(isPanning);
    };
}
