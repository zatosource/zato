import { logger } from './logger-tree-view.js';

export class TreeRenderer {
    constructor() {
        this.searchTerm = '';
    }

    setSearch(term) {
        console.log('TreeRenderer.setSearch called:', JSON.stringify({
            previousTerm: this.searchTerm,
            newTerm: term,
            termLength: term ? term.length : 0
        }));
        this.searchTerm = term;
    }

    renderTreeNode(node, lineNumber) {
        const indent = this.getIndentation(node.level);
        const html = [];
        
        const keyMatches = this.nodeHasKeyMatch(node);
        const valueMatches = this.nodeHasValueMatch(node);
        const lineNumberMatches = !this.searchTerm.includes('=') && this.searchTerm && String(lineNumber).includes(this.searchTerm);
        const hasMatch = this.searchTerm.includes('=') ? valueMatches : (keyMatches || valueMatches || lineNumberMatches);
        const lineNumberClass = hasMatch ? 'tree-line-number tree-line-number-match' : 'tree-line-number';
        
        if (lineNumber === 1) {
            console.log('TreeRenderer.renderTreeNode (first node):', JSON.stringify({
                searchTerm: this.searchTerm,
                searchTermLength: this.searchTerm ? this.searchTerm.length : 0,
                hasMatch: hasMatch,
                lineNumberClass: lineNumberClass
            }));
        }

        html.push(`<div class="tree-node-wrapper">`);
        html.push(`<span class="${lineNumberClass}">${lineNumber}</span>`);
        html.push(`<div class="tree-node" data-path="${this.escapeHtml(node.path)}" style="margin-left: ${indent}px">`);
        
        if (node.collapsible) {
            const chevronClass = node.collapsed ? 'collapsed' : '';
            html.push(`
                <span class="tree-toggle" data-path="${this.escapeHtml(node.path)}">
                    <i class="tree-chevron ${chevronClass}">▼</i>
                </span>
            `);
        } else {
            html.push('<span class="tree-toggle-placeholder"></span>');
        }

        const hasKeyMatch = this.searchTerm.includes('=') ? this.nodeHasValueMatch(node) : this.nodeHasKeyMatch(node);
        const keyClass = hasKeyMatch ? 'tree-key tree-match-key' : 'tree-key';
        const keyHtml = hasKeyMatch ? this.highlightSearchInKey(this.escapeHtml(node.key), this.searchTerm) : this.escapeHtml(node.key);
        html.push(`<span class="${keyClass}">${keyHtml}</span>`);

        if (!node.collapsible) {
            html.push(' ');
            const hasValueMatch = this.nodeHasValueMatch(node);
            console.log('renderTreeNode value rendering:', JSON.stringify({
                nodeKey: node.key,
                nodeValue: node.value,
                hasKeyMatch: hasKeyMatch,
                hasValueMatch: hasValueMatch
            }));
            const valueHtml = this.applySyntaxHighlighting(node.value, node.valueType, hasValueMatch);
            html.push(valueHtml);
        }

        html.push('</div>');
        html.push('</div>');
        
        return html.join('');
    }

    nodeHasKeyMatch(node) {
        if (!this.searchTerm) return false;
        
        if (this.searchTerm.includes('=')) {
            const [key] = this.searchTerm.split('=');
            const trimmedKey = key.trim();
            
            if (trimmedKey) {
                const result = node.key && node.key.toLowerCase() === trimmedKey.toLowerCase();
                console.log('nodeHasKeyMatch (=):', JSON.stringify({
                    nodeKey: node.key,
                    trimmedKey: trimmedKey,
                    result: result
                }));
                return result;
            }
        } else {
            const lowerTerm = this.searchTerm.toLowerCase();
            return node.key && node.key.toLowerCase().includes(lowerTerm);
        }
        
        return false;
    }

    nodeHasValueMatch(node) {
        if (!this.searchTerm) return false;
        
        let valuePattern;
        
        if (this.searchTerm.includes('=')) {
            const [key, value] = this.searchTerm.split('=');
            const trimmedKey = key.trim();
            const trimmedValue = value ? value.trim() : '';
            
            if (trimmedKey && trimmedValue) {
                const keyMatch = node.key && node.key.toLowerCase() === trimmedKey.toLowerCase();
                const valueMatch = node.value && String(node.value).toLowerCase().includes(trimmedValue.toLowerCase());
                const result = keyMatch && valueMatch;
                console.log('nodeHasValueMatch (=):', JSON.stringify({
                    nodeKey: node.key,
                    nodeValue: node.value,
                    trimmedKey: trimmedKey,
                    trimmedValue: trimmedValue,
                    keyMatch: keyMatch,
                    valueMatch: valueMatch,
                    result: result
                }));
                return result;
            }
        } else {
            const lowerTerm = this.searchTerm.toLowerCase();
            return node.value && String(node.value).toLowerCase().includes(lowerTerm);
        }
        
        return false;
    }

    applySyntaxHighlighting(value, type, hasValueMatch) {
        let displayValue;
        let className = `tree-value tree-value-${type}`;
        
        if (hasValueMatch) {
            className += ' tree-match-value';
        }

        if (type === 'string') {
            const escapedValue = this.escapeHtml(value);
            const highlighted = hasValueMatch ? this.highlightSearchInValue(escapedValue, this.searchTerm) : escapedValue;
            displayValue = highlighted;
        } else if (type === 'null') {
            displayValue = 'null';
        } else if (type === 'undefined') {
            displayValue = 'undefined';
        } else if (type === 'boolean') {
            displayValue = value ? 'true' : 'false';
        } else if (type === 'number') {
            displayValue = String(value);
        } else {
            displayValue = this.escapeHtml(String(value));
        }

        if (type !== 'string' && hasValueMatch) {
            displayValue = this.highlightSearchInValue(displayValue, this.searchTerm);
        }
        
        return `<span class="${className}">${displayValue}</span>`;
    }

    highlightSearchInKey(text, searchTerm) {
        if (!searchTerm || !text) return text;

        let searchPattern;
        
        if (searchTerm.includes('=')) {
            const [key] = searchTerm.split('=');
            const trimmedKey = key.trim();
            
            if (trimmedKey) {
                searchPattern = trimmedKey;
            }
        } else {
            searchPattern = searchTerm;
        }
        
        if (!searchPattern) return text;
        
        const escapedPattern = searchPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escapedPattern})`, 'gi');
        
        return text.replace(regex, '<span class="tree-search-highlight">$1</span>');
    }

    highlightSearchInValue(text, searchTerm) {
        if (!searchTerm || !text) return text;

        let searchPattern;
        
        if (searchTerm.includes('=')) {
            const [, value] = searchTerm.split('=');
            const trimmedValue = value ? value.trim() : '';
            
            if (trimmedValue) {
                searchPattern = trimmedValue;
            }
        } else {
            searchPattern = searchTerm;
        }
        
        if (!searchPattern) return text;
        
        const escapedPattern = searchPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escapedPattern})`, 'gi');
        
        return text.replace(regex, '<span class="tree-search-highlight">$1</span>');
    }

    getIndentation(level) {
        return level * 20;
    }

    escapeHtml(text) {
        if (text === null || text === undefined) return '';
        const div = document.createElement('div');
        div.textContent = String(text);
        return div.innerHTML;
    }
}
