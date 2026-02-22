(function() {
    'use strict';

    var ZatoIDEExplorer = {

        instances: {},

        create: function(containerId, options) {
            options = options || {};

            var container = document.getElementById(containerId);
            if (!container) {
                return null;
            }

            var instance = {
                id: containerId,
                container: container,
                rootPath: options.rootPath || '~',
                currentPath: options.rootPath || '~',
                expandedPaths: {},
                onFileSelect: options.onFileSelect || null,
                onFileDoubleClick: options.onFileDoubleClick || null
            };

            this.instances[containerId] = instance;
            this.render(instance);
            this.loadDirectory(instance, instance.rootPath);

            return instance;
        },

        getInstance: function(containerId) {
            return this.instances[containerId] || null;
        },

        render: function(instance) {
            var html = '';
            html += '<div class="zato-ide-explorer">';
            html += '<div class="zato-ide-explorer-header">';
            html += '<span class="zato-ide-explorer-title">Explorer</span>';
            html += '</div>';
            html += '<div class="zato-ide-explorer-tree" id="' + instance.id + '-tree">';
            html += '</div>';
            html += '</div>';
            instance.container.innerHTML = html;
        },

        loadDirectory: function(instance, path, parentElement, indent) {
            var self = this;
            indent = indent || 0;

            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/zato/ide/explorer/list/?path=' + encodeURIComponent(path), true);
            xhr.setRequestHeader('Content-Type', 'application/json');

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        var response = JSON.parse(xhr.responseText);
                        if (response.success) {
                            self.renderItems(instance, response.items, parentElement, indent, response.path);
                        }
                    }
                }
            };

            xhr.send();
        },

        renderItems: function(instance, items, parentElement, indent, currentPath) {
            var self = this;
            var treeContainer = parentElement || document.getElementById(instance.id + '-tree');

            if (!parentElement) {
                treeContainer.innerHTML = '';
            }

            items.forEach(function(item) {
                var itemDiv = document.createElement('div');
                itemDiv.className = 'zato-ide-explorer-item';
                itemDiv.setAttribute('data-path', item.path);
                itemDiv.setAttribute('data-is-dir', item.is_dir ? 'true' : 'false');

                var contentDiv = document.createElement('div');
                contentDiv.className = 'zato-ide-explorer-item-content';
                contentDiv.style.paddingLeft = (indent * 16 + 4) + 'px';

                if (item.is_dir) {
                    var arrow = document.createElement('span');
                    arrow.className = 'zato-ide-explorer-arrow';
                    arrow.innerHTML = '&#9654;';
                    contentDiv.appendChild(arrow);
                } else {
                    var spacer = document.createElement('span');
                    spacer.className = 'zato-ide-explorer-arrow-spacer';
                    contentDiv.appendChild(spacer);
                }

                var icon = document.createElement('img');
                icon.className = 'zato-ide-explorer-icon';
                var iconBasePath = item.is_dir ? '/static/ide-icons/icons/' : '/static/ide-icons/icons/';
                icon.src = iconBasePath + item.icon;
                icon.setAttribute('data-expanded-icon', iconBasePath + (item.icon_expanded || item.icon));
                icon.setAttribute('data-collapsed-icon', iconBasePath + item.icon);
                contentDiv.appendChild(icon);

                var name = document.createElement('span');
                name.className = 'zato-ide-explorer-name';
                name.textContent = item.name;
                contentDiv.appendChild(name);

                itemDiv.appendChild(contentDiv);

                var childrenDiv = document.createElement('div');
                childrenDiv.className = 'zato-ide-explorer-children';
                childrenDiv.style.display = 'none';
                itemDiv.appendChild(childrenDiv);

                treeContainer.appendChild(itemDiv);

                contentDiv.addEventListener('click', function(e) {
                    e.stopPropagation();
                    self.handleItemClick(instance, item, itemDiv, childrenDiv, indent);
                });

                contentDiv.addEventListener('dblclick', function(e) {
                    e.stopPropagation();
                    if (!item.is_dir && instance.onFileDoubleClick) {
                        instance.onFileDoubleClick(item);
                    }
                });
            });
        },

        handleItemClick: function(instance, item, itemDiv, childrenDiv, indent) {
            var self = this;

            if (item.is_dir) {
                var isExpanded = itemDiv.classList.contains('expanded');
                var arrow = itemDiv.querySelector('.zato-ide-explorer-arrow');
                var icon = itemDiv.querySelector('.zato-ide-explorer-icon');

                if (isExpanded) {
                    itemDiv.classList.remove('expanded');
                    childrenDiv.style.display = 'none';
                    if (arrow) {
                        arrow.innerHTML = '&#9654;';
                    }
                    if (icon) {
                        icon.src = icon.getAttribute('data-collapsed-icon');
                    }
                    delete instance.expandedPaths[item.path];
                } else {
                    itemDiv.classList.add('expanded');
                    childrenDiv.style.display = 'block';
                    if (arrow) {
                        arrow.innerHTML = '&#9660;';
                    }
                    if (icon) {
                        icon.src = icon.getAttribute('data-expanded-icon');
                    }
                    instance.expandedPaths[item.path] = true;

                    if (childrenDiv.children.length === 0) {
                        self.loadDirectory(instance, item.path, childrenDiv, indent + 1);
                    }
                }
            } else {
                var allItems = instance.container.querySelectorAll('.zato-ide-explorer-item-content');
                allItems.forEach(function(el) {
                    el.classList.remove('selected');
                });

                var contentDiv = itemDiv.querySelector('.zato-ide-explorer-item-content');
                if (contentDiv) {
                    contentDiv.classList.add('selected');
                }

                if (instance.onFileSelect) {
                    instance.onFileSelect(item);
                }
            }
        },

        refresh: function(instance) {
            instance.expandedPaths = {};
            this.loadDirectory(instance, instance.rootPath);
        },

        setRootPath: function(instance, path) {
            instance.rootPath = path;
            instance.currentPath = path;
            instance.expandedPaths = {};
            this.loadDirectory(instance, path);
        },

        destroy: function(containerId) {
            var instance = this.instances[containerId];
            if (instance) {
                instance.container.innerHTML = '';
                delete this.instances[containerId];
            }
        }
    };

    window.ZatoIDEExplorer = ZatoIDEExplorer;

})();
