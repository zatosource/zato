// /////////////////////////////////////////////////////////////////////////////
// Multi-checkbox component with tri-state support
// /////////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.multi_checkbox');

    var State = {
        Off: 0,
        On: 1,
        Disabled: 2
    };

    $.fn.zato.multi_checkbox.State = State;

    // Set up tri-state behavior on a checkbox element
    function setupTriState(checkbox) {
        var $checkbox = $(checkbox);

        if ($checkbox.data('tri-state-initialized')) {
            return;
        }

        var initialState;
        if ($checkbox.hasClass('indeterminate')) {
            initialState = State.Disabled;
        } else if ($checkbox.prop('checked')) {
            initialState = State.On;
        } else {
            initialState = State.Off;
        }

        $checkbox.data('tri-state', initialState);
        $checkbox.data('tri-state-initialized', true);

        $checkbox.off('click.tristate mousedown.tristate');

        $checkbox.on('mousedown.tristate', function(e) {
            e.preventDefault();
            e.stopPropagation();

            var currentState = $checkbox.data('tri-state');
            var actualChecked = $checkbox.prop('checked');
            var actualIndeterminate = $checkbox.hasClass('indeterminate');

            var actualState = currentState;
            if (actualIndeterminate) {
                actualState = State.Disabled;
            } else if (actualChecked) {
                actualState = State.On;
            } else {
                actualState = State.Off;
            }

            if (actualState !== currentState) {
                $checkbox.data('tri-state', actualState);
                currentState = actualState;
            }

            var newState = (currentState + 1) % 3;
            $checkbox.data('tri-state', newState);
            $checkbox.removeClass('indeterminate');

            switch (newState) {
                case State.Off:
                    $checkbox.prop('checked', false);
                    break;
                case State.On:
                    $checkbox.prop('checked', true);
                    break;
                case State.Disabled:
                    $checkbox.prop('checked', false);
                    $checkbox.addClass('indeterminate');
                    break;
            }

            $checkbox.trigger('statechange', [newState]);
            return false;
        });

        $checkbox.on('click.tristate', function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        });
    }

    $.fn.zato.multi_checkbox.setupTriState = setupTriState;

    // Get current state of a checkbox
    function getState(checkbox) {
        var $checkbox = $(checkbox);
        return $checkbox.data('tri-state');
    }

    $.fn.zato.multi_checkbox.getState = getState;

    // Set state of a checkbox
    function setState(checkbox, state) {
        var $checkbox = $(checkbox);

        $checkbox.data('tri-state', state);
        $checkbox.removeClass('indeterminate');

        switch (state) {
            case State.Off:
                $checkbox.prop('checked', false);
                break;
            case State.On:
                $checkbox.prop('checked', true);
                break;
            case State.Disabled:
                $checkbox.prop('checked', false);
                $checkbox.addClass('indeterminate');
                break;
        }
    }

    $.fn.zato.multi_checkbox.setState = setState;

    // Render the multi-checkbox component
    // config: {
    //   containerId: string - id of container element
    //   items: array of {
    //     id: string or number - unique identifier
    //     state: number - State.Off, State.On, or State.Disabled
    //     link: string - url for the link
    //     linkText: string - text displayed as link
    //     description: string - optional description text
    //   }
    //   inputName: string - name attribute for checkbox inputs
    //   emptyMessage: string - message when no items
    //   onStateChange: function(itemId, newState) - callback when state changes
    // }
    function render(config) {
        var containerId = config.containerId;
        var items = config.items || [];
        var inputName = config.inputName || 'item_name';
        var emptyMessage = config.emptyMessage || 'No items available';
        var onStateChange = config.onStateChange;

        var $container = $('#' + containerId);
        if ($container.length === 0) {
            console.log('multi_checkbox.render: container not found, id=' + containerId);
            return;
        }

        if (items.length === 0) {
            var emptyHtml = '<table class="multi-select-table">' +
                '<tr><td colspan="2"><span class="multi-select-message">' +
                emptyMessage + '</span></td></tr></table>';
            $container.html(emptyHtml);
            return;
        }

        var filterId = containerId + '_filter';
        var html = '<table class="multi-select-table"><tbody>';
        html += '<tr class="multi-checkbox-filter-row"><td colspan="2"><input type="text" id="' + filterId + '" class="multi-checkbox-filter" placeholder="Filter..."></td></tr>';

        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            var checkboxId = 'item_checkbox_' + item.id;
            var indeterminateClass = item.state === State.Disabled ? ' indeterminate' : '';
            var checkedAttr = item.state === State.On ? ' checked' : '';
            var linkTextLower = (item.linkText || '').toLowerCase();
            var descriptionLower = (item.description || '').toLowerCase();

            html += '<tr class="multi-checkbox-row" data-checkbox-id="' + checkboxId + '" data-link-text="' + linkTextLower + '" data-description="' + descriptionLower + '">';
            html += '<td><input type="checkbox" id="' + checkboxId + '" name="' + inputName + '" value="' + item.id + '" class="tri-state' + indeterminateClass + '"' + checkedAttr + '></td>';
            html += '<td>';

            if (item.link) {
                html += '<a href="' + item.link + '" target="_blank" class="multi-checkbox-link">' + item.linkText + '</a>';
            } else {
                html += '<span class="multi-checkbox-text">' + item.linkText + '</span>';
            }

            if (item.description) {
                html += ' <span class="item-description">(' + item.description + ')</span>';
            }

            html += '</td>';
            html += '</tr>';
        }

        html += '</tbody></table>';
        $container.html(html);

        // Set up filter functionality
        $('#' + filterId).on('input', function() {
            var filterValue = $(this).val().toLowerCase().trim();
            var words = filterValue.split(/\s+/).filter(function(w) { return w.length > 0; });

            $container.find('.multi-checkbox-row').each(function() {
                var $row = $(this);
                var linkText = $row.data('link-text') || '';
                var description = $row.data('description') || '';
                var combined = linkText + ' ' + description;

                var matches = true;
                for (var i = 0; i < words.length; i++) {
                    if (combined.indexOf(words[i]) === -1) {
                        matches = false;
                        break;
                    }
                }

                if (matches) {
                    $row.show();
                } else {
                    $row.hide();
                }
            });
        });

        // Initialize tri-state on all checkboxes
        $container.find('input[name="' + inputName + '"]').each(function() {
            var $checkbox = $(this);
            setupTriState(this);

            if (onStateChange) {
                $checkbox.on('statechange', function(e, newState) {
                    var itemId = $checkbox.val();
                    onStateChange(itemId, newState);
                });
            }
        });

        // Make entire row clickable except for links
        $container.find('.multi-checkbox-row').on('click', function(e) {
            if ($(e.target).hasClass('multi-checkbox-link') || $(e.target).closest('.multi-checkbox-link').length) {
                return;
            }

            var checkboxId = $(this).data('checkbox-id');
            var $checkbox = $('#' + checkboxId);

            if ($checkbox.length) {
                $checkbox.trigger('mousedown.tristate');
            }
        });
    }

    $.fn.zato.multi_checkbox.render = render;

    // Get all selected items (state is On or Disabled)
    // Returns array of { id, state }
    function getSelectedItems(containerId, inputName) {
        var $container = $('#' + containerId);
        var result = [];

        $container.find('input[name="' + inputName + '"]').each(function() {
            var $checkbox = $(this);
            var state = $checkbox.data('tri-state');

            if (state === State.On || state === State.Disabled) {
                result.push({
                    id: $checkbox.val(),
                    state: state
                });
            }
        });

        return result;
    }

    $.fn.zato.multi_checkbox.getSelectedItems = getSelectedItems;

    // Get all items with their current state
    function getAllItems(containerId, inputName) {
        var $container = $('#' + containerId);
        var result = [];

        $container.find('input[name="' + inputName + '"]').each(function() {
            var $checkbox = $(this);
            result.push({
                id: $checkbox.val(),
                state: $checkbox.data('tri-state')
            });
        });

        return result;
    }

    $.fn.zato.multi_checkbox.getAllItems = getAllItems;

    // Set items by id to a specific state
    function setItemStates(containerId, inputName, itemStates) {
        var $container = $('#' + containerId);

        for (var i = 0; i < itemStates.length; i++) {
            var itemState = itemStates[i];
            var $checkbox = $container.find('input[name="' + inputName + '"][value="' + itemState.id + '"]');

            if ($checkbox.length) {
                setState($checkbox[0], itemState.state);
            }
        }
    }

    $.fn.zato.multi_checkbox.setItemStates = setItemStates;

})(jQuery);
