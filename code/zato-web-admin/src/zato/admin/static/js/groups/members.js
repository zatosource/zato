
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {

    $.fn.zato.groups.add_sortable("listing-left");
    $.fn.zato.groups.add_sortable("listing-right");

    let search_form = $("#search-form");

    search_form.on("submit", function(e) {

        let sec_type = $("#search-form-sec-type").val()
        let query = $("#search-form-query").val()

        $.fn.zato.groups.members.on_search_form_submitted(sec_type, query)
        e.preventDefault();
    });

    search_form.on("change", function(e) {
        search_form.submit();
    });

    $("#groups-form").on("change", function(e) {

        let group_type = $("#group_type").val()
        let group_id = $("#groups-form-group-id").val()

        $.fn.zato.groups.members.on_groups_form_changed(group_type, group_id)
        e.preventDefault();
    });

})


// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.members.add_listing_empty = function(side, text) {
    var listing_left = $("#listing-" + side);

    let div_empty = $("<div/>");

    div_empty.attr("id", "listing-"+ side +"-empty");
    div_empty.text(text);

    listing_left.append(div_empty);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.members.remove_listing_empty = function(side) {
    $("#listing-"+ side +"-empty").remove();
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.members.add_listing_left_empty = function() {

    $.fn.zato.groups.members.add_listing_empty("left", "No results");
}
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.members.add_listing_right_empty = function() {

    $.fn.zato.groups.members.add_listing_empty("right", "No members in group");
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.members.remove_listing_left_empty = function() {
    $.fn.zato.groups.members.remove_listing_empty("left");
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.members.remove_listing_right_empty = function() {
    $.fn.zato.groups.members.remove_listing_empty("right");
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.members.populate_list = function(
    item_list,
    listing_id,
    item_list_class,
    add_listing_empty_func,
    remove_listing_empty_func,
    use_security_id_for_id,
) {

    // First, we always remove any items already displayed
    $(".list-group-item." + item_list_class).remove();
    remove_listing_empty_func();

    // We go here if we have something to show ..
    if(item_list.length) {

        var listing = $("#" + listing_id);

        $.each(item_list, function(idx, elem) {

            //
            // Root item div elem
            //
            let elem_id = use_security_id_for_id ? elem.security_id : elem.id;
            let div_item = $("<div/>");
            let div_item_id = String.format("{0}-{1}", elem.sec_type, elem_id);

            div_item.attr("id", div_item_id);
            div_item.attr("class", "list-group-item " + item_list_class);

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
            let href_sec_type = elem.sec_type == "basic_auth" ? "basic-auth" : "apikey";
            let href_template = "/zato/security/{0}/?cluster=1&query={1}";
            let href = String.format(href_template, href_sec_type, elem.name)
            a_sec_name.attr("href", href);
            a_sec_name.text(elem.name);

            //
            // Handle div elem
            //
            let div_handle = $("<div/>");
            div_handle.attr("class", "handle");

            listing.append(div_item);
            div_item.append(div_sec_type);
            div_item.append(div_sec_name);
            div_sec_name.append(a_sec_name);
            div_item.append(div_handle);

        })
    }
    // .. we go here if we have no results to show.
    else {
        add_listing_empty_func();
    };
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.members.populate_security_list = function(item_list) {
    let listing_id = "listing-left";
    let item_list_class = "left";
    let main_func = $.fn.zato.groups.members.populate_list;
    let add_listing_empty_func = $.fn.zato.groups.members.add_listing_left_empty;
    let remove_listing_empty_func = $.fn.zato.groups.members.remove_listing_left_empty;
    let use_security_id_for_id = false;
    main_func(item_list, listing_id, item_list_class, add_listing_empty_func, remove_listing_empty_func, use_security_id_for_id);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.members.populate_member_list = function(item_list) {
    let listing_id = "listing-right";
    let item_list_class = "right";
    let main_func = $.fn.zato.groups.members.populate_list;
    let add_listing_empty_func = $.fn.zato.groups.members.add_listing_right_empty;
    let remove_listing_empty_func = $.fn.zato.groups.members.remove_listing_right_empty;
    let use_security_id_for_id = true;
    main_func(item_list, listing_id, item_list_class, add_listing_empty_func, remove_listing_empty_func, use_security_id_for_id);
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

    let group_type = $("#group_type").val()
    let group_id = $("#groups-form-group-id").val()

    let template = "/zato/groups/get-security-list/?sec_type={0}&query={1}&group_type={2}&group_id={3}"
    let url = String.format(template, sec_type, query, group_type, group_id);
    let data = "";
    let data_type = "json";
    let suppress_user_message = true;

    $.fn.zato.post(url, callback, data, data_type, suppress_user_message);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.members.on_groups_form_changed = function(group_type, group_id) {

    var callback = function(data, status) {
        var success = status == "success";
        if(success) {
            var data = $.parseJSON(data.responseText)

            let sec_type = $("#search-form-sec-type").val()
            let query = $("#search-form-query").val()

            $.fn.zato.groups.members.populate_member_list(data);
            $.fn.zato.groups.members.on_search_form_submitted(sec_type, query)
        }
        else {
            $.fn.zato.user_message(false, data.responseText);
        }
    }

    let template = "/zato/groups/get-member-list/?group_type={0}&group_id={1}";
    let url = String.format(template, group_type, group_id);
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
        onEnd: $.fn.zato.groups.on_sortable_end,
        group: {
            name: "shared",
        }
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.on_group_members_moved = function(item_id_list, group_id, is_add) {

    var callback = function(data, status) {
        var success = status == "success" || status == "parsererror";
        if(success) {
            // $.fn.zato.user_message(true, status + " " + data.responseText);
        }
        else {
            $.fn.zato.user_message(false, status + " " + data.responseText);
        }
    }

    var action = is_add ? "add" : "remove";
    let template = "/zato/groups/members/action/{0}/group/{1}/id-list/{2}/";
    let url = String.format(template, action, group_id, item_id_list);
    let data = "";
    let data_type = "json";
    let suppress_user_message = true;

    $.fn.zato.post(url, callback, data, data_type, suppress_user_message);

}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.on_sortable_end = function(e) {

    // We only need to handle when wrappers are different
    if(e.from.id != e.to.id) {

        var to_remove;
        var to_add;
        var add_listing_empty_func;

        if(e.from.id == "listing-left") {
            to_remove = "left";
            to_add = "right";
            add_listing_empty_func = $.fn.zato.groups.members.add_listing_left_empty;
            $.fn.zato.groups.members.remove_listing_right_empty();
        }
        else if(e.from.id == "listing-right") {
            to_remove = "right";
            to_add = "left";
            add_listing_empty_func = $.fn.zato.groups.members.add_listing_right_empty;
            $.fn.zato.groups.members.remove_listing_left_empty();
        }
        $("#"+ e.to.id + "> .list-group-item").removeClass(to_remove).addClass(to_add);

        //
        // Extract IDs of elements that have been moved
        //
        var item_id_list = [];

        if(e.zato_item_id_list.length) {
            item_id_list = e.zato_item_id_list;
        }
        else {
            item_id_list.push(e.item.id)
        }

        //
        // Invoke the function that will actually move the items between groups
        //
        var is_add_to_group = to_add == "right";
        group_id = $("#groups-form-group-id").val()
        $.fn.zato.groups.on_group_members_moved(item_id_list, group_id, is_add_to_group);

        //
        // Add an indicator that a given lis is empty
        //
        let len_elems = $(".list-group-item." + to_remove).length;
        if(len_elems == 0) {
            add_listing_empty_func();
        }
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
