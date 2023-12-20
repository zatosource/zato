
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new group', null);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.add_sortable = function(elem_id) {

    $('#listing-left').sortable({
        swapThreshold: 1,
        sort: false,
        animation: 150,
        multiDrag: true,
        selectedClass: 'selected',
        fallbackTolerance: 3,
        invertSwap: true,
        // handle: '.handle',
        // emptyInsertThreshold: 1,
        onEnd: $.fn.zato.groups.on_sortable_end,
        group: {
            name: "shared",
        }
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.on_sortable_end = function(e) {

    // We only need to handle when wrappers are different
    if(e.from.id != e.to.id) {

        //alert(e.item.id + " " + e.from.id + " " + e.to.id);

        var item = $("#" + e.item.id);

        var to_remove;
        var to_add;

        if(e.from.id == "listing-left") {
            to_remove = "left";
            to_add = "right";
        }
        else if(e.from.id == "listing-right") {
            to_remove = "right";
            to_add = "left";
        }

        $("#"+ e.to.id + "> .list-group-item").removeClass(to_remove).addClass(to_add);
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
