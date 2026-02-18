(function() {
    'use strict';

    var ZatoDropdown = {

        instances: {},

        init: function(selectElement, options) {
            if (!selectElement) {
                return null;
            }

            options = options || {};
            var theme = options.theme || 'dark';
            var container = this.createDropdown(selectElement, options);

            container.setAttribute('data-theme', theme);
            container.classList.add('zato-dropdown-theme-' + theme);

            this.bindEvents(container, selectElement, options);

            var instanceId = options.id || selectElement.id || ('dropdown-' + Date.now());
            container.setAttribute('data-instance-id', instanceId);
            this.instances[instanceId] = {
                container: container,
                selectElement: selectElement,
                options: options
            };

            return container;
        },

        createDropdown: function(selectElement, options) {
            var container = document.createElement('div');
            container.className = 'zato-dropdown';
            if (options.className) {
                container.className += ' ' + options.className;
            }

            var selectedOption = selectElement.options[selectElement.selectedIndex];
            var selectedText = selectedOption ? selectedOption.text : '';
            var selectedValue = selectedOption ? selectedOption.value : '';

            container.setAttribute('data-value', selectedValue);

            var trigger = document.createElement('div');
            trigger.className = 'zato-dropdown-trigger';

            if (options.tooltip) {
                trigger.setAttribute('data-tooltip', options.tooltip);
            }

            var text = document.createElement('span');
            text.className = 'zato-dropdown-text';
            text.textContent = selectedText;

            var arrow = document.createElement('span');
            arrow.className = 'zato-dropdown-arrow';
            arrow.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12"><path d="M7 10l5 5 5-5z"/></svg>';

            trigger.appendChild(text);
            trigger.appendChild(arrow);

            var menu = document.createElement('div');
            menu.className = 'zato-dropdown-menu';

            for (var i = 0; i < selectElement.options.length; i++) {
                var opt = selectElement.options[i];
                if (opt.getAttribute('data-separator') === 'true') {
                    var separator = document.createElement('div');
                    separator.className = 'zato-dropdown-separator';
                    menu.appendChild(separator);
                }
                var item = document.createElement('div');
                item.className = 'zato-dropdown-item';
                if (opt.value === selectedValue) {
                    item.classList.add('active');
                }
                if (opt.disabled || opt.getAttribute('data-disabled') === 'true') {
                    item.classList.add('disabled');
                }
                item.setAttribute('data-value', opt.value);
                item.textContent = opt.text;
                menu.appendChild(item);
            }

            container.appendChild(trigger);
            container.appendChild(menu);

            selectElement.style.display = 'none';
            selectElement.parentNode.insertBefore(container, selectElement.nextSibling);

            return container;
        },

        bindEvents: function(container, selectElement, options) {
            var trigger = container.querySelector('.zato-dropdown-trigger');
            var menu = container.querySelector('.zato-dropdown-menu');

            trigger.addEventListener('click', function(e) {
                e.stopPropagation();

                if (options.onBeforeOpen) {
                    options.onBeforeOpen(container);
                }

                var isOpen = container.classList.contains('open');
                ZatoDropdown.closeAll();
                if (!isOpen) {
                    container.classList.add('open');
                    if (options.onOpen) {
                        options.onOpen(container);
                    }
                }
            });

            menu.addEventListener('click', function(e) {
                var item = e.target.closest('.zato-dropdown-item');
                if (item) {
                    if (item.classList.contains('disabled')) {
                        e.stopPropagation();
                        return;
                    }

                    var value = item.getAttribute('data-value');
                    var text = item.textContent;

                    container.setAttribute('data-value', value);
                    container.querySelector('.zato-dropdown-text').textContent = text;

                    var items = menu.querySelectorAll('.zato-dropdown-item');
                    for (var i = 0; i < items.length; i++) {
                        items[i].classList.remove('active');
                    }
                    item.classList.add('active');

                    selectElement.value = value;
                    var event = document.createEvent('Event');
                    event.initEvent('change', true, true);
                    selectElement.dispatchEvent(event);

                    if (options.onChange) {
                        options.onChange(value, text, container);
                    }

                    ZatoDropdown.closeAll();
                    e.stopPropagation();
                }
            });

            document.addEventListener('click', function() {
                container.classList.remove('open');
            });
        },

        closeAll: function() {
            var openDropdowns = document.querySelectorAll('.zato-dropdown.open');
            for (var i = 0; i < openDropdowns.length; i++) {
                openDropdowns[i].classList.remove('open');
            }
        },

        getValue: function(container) {
            return container.getAttribute('data-value');
        },

        setValue: function(container, value) {
            var item = container.querySelector('.zato-dropdown-item[data-value="' + value + '"]');
            if (item) {
                var text = item.textContent;
                container.setAttribute('data-value', value);
                container.querySelector('.zato-dropdown-text').textContent = text;

                var items = container.querySelectorAll('.zato-dropdown-item');
                for (var i = 0; i < items.length; i++) {
                    items[i].classList.remove('active');
                }
                item.classList.add('active');
            }
        },

        setTheme: function(container, theme) {
            var currentTheme = container.getAttribute('data-theme');
            if (currentTheme) {
                container.classList.remove('zato-dropdown-theme-' + currentTheme);
            }
            container.setAttribute('data-theme', theme);
            container.classList.add('zato-dropdown-theme-' + theme);
        },

        getTheme: function(container) {
            return container.getAttribute('data-theme') || 'dark';
        },

        getInstance: function(instanceId) {
            return this.instances[instanceId] || null;
        },

        destroy: function(container) {
            var instanceId = container.getAttribute('data-instance-id');
            if (instanceId && this.instances[instanceId]) {
                var instance = this.instances[instanceId];
                instance.selectElement.style.display = '';
                container.parentNode.removeChild(container);
                delete this.instances[instanceId];
            }
        }
    };

    window.ZatoDropdown = ZatoDropdown;

})();
