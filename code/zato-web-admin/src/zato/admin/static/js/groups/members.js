
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $.fn.zato.groups.add_sortable("listing-left");
    $.fn.zato.groups.add_sortable("listing-right");

    $("#search-form").on("submit", function(e) {

        let sec_type = $("#search-form-sec-type").val()
        let query = $("#search-form-query").val()

        $.fn.zato.groups.members.on_search_form_submitted(sec_type, query)
        e.preventDefault();
    });

})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.members.populate_security_list = function(security_list) {

    // First, we always remove any items already displayed
    $(".list-group-item.left").remove();

    // We go here if we have anything to show ..
    if(security_list.length) {

        var listing_left = $("#listing-left");
        $.fn.zato.toggle_visible_hidden("#listing-left-empty", false);

        $.each(security_list, function(idx, elem) {
            /*
            <div id="{{ item.sec_type }}-{{ item.id }}" class="list-group-item left">
                <div class="sec-type">{{ item.sec_type_name }}</div>
                <div class="sec-name"><a href="#">{{ item.name }}</a></div>
                <div class="handle"></div>
            </div>
            */

            //
            // Root item div elem
            //
            let div_item = $("<div/>");
            let div_item_id = String.format("{0}-{1}", elem.sec_type, elem.id);

            div_item.attr("id", div_item_id);
            div_item.attr("class", "list-group-item left");

            //
            // Sec type div elem
            //
            let div_sec_type = $("<div/>");
            div_sec_type.attr("class", "sec-type");
            div_sec_type.text(elem.sec_type_name);

            //
            // Sec name div elem
            //
            let div_sec_name = $("<div/>");
            div_sec_name.attr("class", "sec-name");

            //
            // Sec name div elem - link
            //
            let a_sec_name = $("<a/>");
            a_sec_name.attr("href", "QQQ");
            a_sec_name.text(elem.name);

            //
            // Handle div elem
            //
            let div_handle = $("<div/>");
            div_handle.attr("class", "handle");

            listing_left.append(div_item);
            div_item.append(div_sec_type);
            div_item.append(div_sec_name);
            div_sec_name.append(a_sec_name);
            div_item.append(div_handle);

        })
    }
    // .. otherwise, we indicate that there are no results
    else {
        $.fn.zato.toggle_visible_hidden("#listing-left-empty", true);
    };

    //alert(security_list);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.members.on_search_form_submitted = function(sec_type, query) {

    var callback = function(data, status) {
        var success = status == "success";
        if(success) {
            var data = $.parseJSON(data.responseText)
            $.fn.zato.groups.members.populate_security_list(data);
        }
        else {
            $.fn.zato.user_message(false, data.responseText);
        }
    }

    let url = String.format("/zato/groups/get-security-list/?sec_type={0}&query={1}", sec_type, query);
    let data = "";
    let data_type = "json";
    let suppress_user_message = true;

    $.fn.zato.post(url, callback, data, data_type, suppress_user_message);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.add_sortable = function(elem_id) {

    $("#" + elem_id).sortable({
        swapThreshold: 1,
        sort: false,
        animation: 150,
        multiDrag: true,
        selectedClass: "selected",
        fallbackTolerance: 3,
        invertSwap: true,
        handle: ".list-group-item .handle",
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
