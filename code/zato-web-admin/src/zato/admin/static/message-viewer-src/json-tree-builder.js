import { logger } from './logger-tree-view.js';

export class JsonTreeBuilder {
    constructor() {
        this.nodeCounter = 0;
    }

    buildTree(json, path = '', level = 0) {
        this.nodeCounter = 0;
        logger.info('JsonTreeBuilder.buildTree: starting tree build');
        
        const tree = this._buildNode(json, path, level);
        
        logger.info(`JsonTreeBuilder.buildTree: completed, total nodes=${this.nodeCounter}`);
        return tree;
    }

    _buildNode(value, path, level) {
        this.nodeCounter++;
        
        const node = {
            id: `node-${this.nodeCounter}`,
            path: path,
            level: level,
            type: this.getNodeType(value),
            collapsible: this.isCollapsible(value),
            children: []
        };

        if (node.type === 'object') {
            node.key = path.split('.').pop() || 'root';
            node.value = '(dict)';
            node.itemCount = Object.keys(value).length;
            
            for (const [key, val] of Object.entries(value)) {
                const childPath = path ? `${path}.${key}` : key;
                node.children.push(this._buildNode(val, childPath, level + 1));
            }
        } else if (node.type === 'array') {
            node.key = path.split('.').pop() || 'root';
            node.value = '(list)';
            node.itemCount = value.length;
            
            for (let i = 0; i < value.length; i++) {
                const childPath = `${path}[${i}]`;
                node.children.push(this._buildNode(value[i], childPath, level + 1));
            }
        } else {
            const pathParts = path.split('.');
            const lastPart = pathParts[pathParts.length - 1];
            
            if (lastPart.includes('[')) {
                node.key = lastPart;
            } else {
                node.key = lastPart;
            }
            
            node.value = value;
            node.valueType = typeof value;
        }

        return node;
    }

    flattenTree(tree, collapsedPaths = new Set()) {
        logger.info(`JsonTreeBuilder.flattenTree: flattening with ${collapsedPaths.size} collapsed paths`);
        
        const flatArray = [];
        this._flattenNode(tree, flatArray, collapsedPaths);
        
        logger.info(`JsonTreeBuilder.flattenTree: result has ${flatArray.length} visible nodes`);
        return flatArray;
    }

    _flattenNode(node, result, collapsedPaths) {
        result.push({
            id: node.id,
            path: node.path,
            level: node.level,
            key: node.key,
            value: node.value,
            valueType: node.valueType,
            type: node.type,
            collapsible: node.collapsible,
            collapsed: collapsedPaths.has(node.path),
            itemCount: node.itemCount
        });

        if (node.collapsible && !collapsedPaths.has(node.path)) {
            for (const child of node.children) {
                this._flattenNode(child, result, collapsedPaths);
            }
        }
    }

    getNodeType(value) {
        if (value === null) return 'null';
        if (value === undefined) return 'undefined';
        if (Array.isArray(value)) return 'array';
        if (typeof value === 'object') return 'object';
        if (typeof value === 'string') return 'string';
        if (typeof value === 'number') return 'number';
        if (typeof value === 'boolean') return 'boolean';
        return 'unknown';
    }

    isCollapsible(value) {
        if (value === null || value === undefined) return false;
        if (Array.isArray(value)) return value.length > 0;
        if (typeof value === 'object') return Object.keys(value).length > 0;
        return false;
    }
}
