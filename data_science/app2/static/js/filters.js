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
    // set_filter_values(data['your_team_cards'],
    //     "your_team_cards_dropdown",
    //     "dropdown-item attrib-button")
    // set_filter_values(data['opponent_team_cards'],
    //     "opponent_team_cards_dropdown",
    //     "dropdown-item attrib-button")
    // set_filter_values(data['game_modes'],
    //     "game_mode_dropdown",
    //     "dropdown-item attrib-button")
    // set_filter_values(data['arenas'],
    //     "arena_dropdown",
    //     "dropdown-item attrib-button")
    set_trophy_slider(data['min_trophy'],
                      data['max_trophy'])
}



// NEW filters
function create_fill_filters(data, filter_id, limit, show_limit){
    var data_values = []
    for (i = 0; i < data.length; i++) {
        data_values.push({'value':data[i], 'text':data[i]});
    };
    tail.select(filter_id, {
        multiple:true,
        items:data_values,
        search: true,
        multiLimit:limit,
        multiContainer:true,
        multiPinSelected:true,
        multiShowCount:show_limit,
        multiShowLimit:true,
        deselect:true,
        searchMarked:false
    });
};

function create_filters(data){
    create_fill_filters(data['your_team_cards'], '#your_team_filter', 8, true)
    create_fill_filters(data['opponent_team_cards'], '#opponent_team_filter', 8, true)
    create_fill_filters(data['game_modes'], '#game_mode_filter', Infinity, false)
    create_fill_filters(data['arenas'], '#arena_filter', Infinity, false)
    create_fill_filters(['Last Day', 'Last Week', 'Last Month'], '#battle_time_filter', 1, true)
};

function get_filter_vals(filter_id) {
    var selected_vals = []
    var children = $(filter_id).children()
    for (i=0; i<children.length; i++) {
        if (typeof children[i].attributes[2] !== 'undefined') {
            selected_vals.push(children[i].text);
        };
    };
    console.log(selected_vals);

    // var filter_names = [
    //     'your_team_filter',
    //     'opponent_team_filter',
    //     'game_mode_filter',
    //     'arena_filter',
    //     'trophy_filter',
    //     'battle_time_filter'
    // ]
    // var result = {}
    // for (i=0; i<filter_names.length; i++) {
    //     var selected_vals = []
    //     var children = $('#'+filter_names[i]).children()
    //     for (j=0; j<children.length; j++) {
    //         if (typeof children[j].attributes[2] !== 'undefined') {
    //             selected_vals.push(children[j].text);
    //         };
    //     };
    //     result[filter_names[i]] = selected_vals;
    // }
    // console.log(result);
};

$("#your_team_filter").on("change", function () {
    get_filter_vals("#your_team_filter")
});

$("#opponent_team_filter").on("change", function () {
    get_filter_vals("#opponent_team_filter")
});

$("#game_mode_filter").on("change", function () {
    get_filter_vals("#game_mode_filter")
});

$("#arena_filter").on("change", function () {
    get_filter_vals("#arena_filter")
});

$("#battle_time_filter").on("change", function () {
    get_filter_vals("#battle_time_filter")
});
