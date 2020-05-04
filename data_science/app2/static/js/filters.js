$(document).on("click", ".attrib-button", function() {
    var clicked_attrib = this.innerHTML;
    var this_dropdown = $(this).parent()[0].parentElement.children[0];
    var this_dropdown_text = this_dropdown.innerHTML.split(": ")[0]
    var this_dropdown_attrib = this_dropdown.innerHTML.split(": ")[1]
    var this_dropdown_attrib_list = this_dropdown.innerHTML.split(": ")[1].split(", ")
    if (this_dropdown_attrib == "No Filter") {
        this_dropdown.innerHTML = this_dropdown_text + ": " + clicked_attrib
    } else if (this_dropdown_attrib_list.indexOf(clicked_attrib) != -1) {
        for (var i = 0; i < this_dropdown_attrib_list.length; i++) {
           if (this_dropdown_attrib_list[i] === clicked_attrib) {
             this_dropdown_attrib_list.splice(i, 1);
           }
        }
        this_dropdown.innerHTML = this_dropdown_text + ": " + this_dropdown_attrib_list.join(", ")
        if (this_dropdown.innerHTML.split(": ")[1] == "") {
            this_dropdown.innerHTML = this_dropdown.innerHTML + "No Filter"
        }
    } else {
        this_dropdown.innerHTML = this_dropdown.innerHTML + ", " + clicked_attrib;
    }
    submit_filters()
});

$(document).on("click", ".attrib-button-single", function() {
    var clicked_attrib = this.innerHTML;
    var this_dropdown = $(this).parent()[0].parentElement.children[0];
    var this_dropdown_text = this_dropdown.innerHTML.split(": ")[0]
    var this_dropdown_attrib = this_dropdown.innerHTML.split(": ")[1]
    var this_dropdown_attrib_list = this_dropdown.innerHTML.split(": ")[1].split(", ")
    if (this_dropdown_attrib == "No Filter") {
        this_dropdown.innerHTML = this_dropdown_text + ": " + clicked_attrib
    } else if (this_dropdown_attrib_list.indexOf(clicked_attrib) != -1) {
        for (var i = 0; i < this_dropdown_attrib_list.length; i++) {
           if (this_dropdown_attrib_list[i] === clicked_attrib) {
             this_dropdown_attrib_list.splice(i, 1);
           }
        }
        this_dropdown.innerHTML = this_dropdown_text + ": " + this_dropdown_attrib_list.join(", ")
        if (this_dropdown.innerHTML.split(": ")[1] == "") {
            this_dropdown.innerHTML = this_dropdown.innerHTML + "No Filter"
        }
    } else {
        this_dropdown.innerHTML = this_dropdown_text + ": " + clicked_attrib;
    }
    submit_filters()
});

function set_trophy_slider (min_val, max_val) {
    $("#trophy_slider").ionRangeSlider({
        type: "double",
        grid: true,
        min: min_val,
        max: max_val,
        from: min_val,
        to: max_val,
        prefix: ""
    });
}

$("#trophy_slider").on("change", function () {
    submit_filters()
});

async function submit_filters() {
    const response = await fetch('/filter', {
        method: 'POST',
        body: JSON.stringify({
            your_team_filter: document.getElementById("your_team_filter").children[0].innerHTML,
            opponent_team_filter: document.getElementById("opponent_team_filter").children[0].innerHTML,
            game_mode_filter: document.getElementById("game_mode_filter").children[0].innerHTML,
            arena_filter: document.getElementById("arena_filter").children[0].innerHTML,
            trophy_filter: document.getElementById('trophy_slider').value,
            battle_time_filter: document.getElementById("battle_time_filter").children[0].innerHTML
        }),
        headers: {
            'Content-Type': 'application/json',
        },
    })
    const data = await response.json()
    render(data)
    show_messages(data)
    show_number_games(data)
    show_win_rate(data)
}

function set_filter_values (values_list, dropdown_id, classes) {
    result = ""
    for (i = 0; i < values_list.length; i+=1) {
        result += "<li class=\""+classes+"\">"+values_list[i]+"</li>"
    };
    document.getElementById(dropdown_id).innerHTML += result
};

function fill_filters(data) {
    set_filter_values(data['your_team_cards'],
        "your_team_cards_dropdown",
        "dropdown-item attrib-button")
    set_filter_values(data['opponent_team_cards'],
        "opponent_team_cards_dropdown",
        "dropdown-item attrib-button")
    set_filter_values(data['game_modes'],
        "game_mode_dropdown",
        "dropdown-item attrib-button")
    set_filter_values(data['arenas'],
        "arena_dropdown",
        "dropdown-item attrib-button")
    set_trophy_slider(data['min_trophy'],
                      data['max_trophy'])
}


// NEW filters
$('#select-country-index').selectize({
	sortField: 'text',
	maxItems: 1,
	onChange: function () {
        // trigger filters on change with current values
    }
});

// take this out of a function so it just gets triggered like the trophy filter
function create_selectize_menu_index(destinations){
    for (i = 0; i < destinations.length; i++) {
        $("#select-country-index")[0].selectize.addOption({value:destinations[i],
                                                           text:destinations[i]});
    };
};
