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
    get_filter_vals()
});

async function submit_filters(results_dict) {
    const response = await fetch('/filter', {
        method: 'POST',
        body: JSON.stringify(results_dict),
        headers: {
            'Content-Type': 'application/json',
        },
    })
    const data = await response.json()
    render(data)
    show_number_games(data)
    show_win_rate(data)
    if (data['messages'].length > 0) {
        setTimeout(function() {show_messages(data)},10)
    };
}

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
    window.processed_data = data['data'] // NEW
    set_trophy_slider(data['min_trophy'],
                      data['max_trophy'])
    create_fill_filters(data['your_team_cards'], '#your_team_filter', 8, true)
    create_fill_filters(data['opponent_team_cards'], '#opponent_team_filter', 8, true)
    create_fill_filters(data['game_modes'], '#game_mode_filter', Infinity, false)
    create_fill_filters(['Last Day', 'Last Week', 'Last Month'], '#battle_time_filter', 1, true)
};

function get_filter_vals() {
    var filter_names = [
        'your_team_filter',
        'opponent_team_filter',
        'game_mode_filter',
        'battle_time_filter'
    ]
    var result = {}
    for (i=0; i<filter_names.length; i++) {
        var selected_vals = []
        var children = $('#'+filter_names[i]).children()
        for (j=0; j<children.length; j++) {
            if (typeof children[j].attributes[2] !== 'undefined') {
                selected_vals.push(children[j].text);
            };
        };
        result[filter_names[i]] = selected_vals;
    }
    result['trophy_filter'] = document.getElementById('trophy_slider').value
    result['test_filter'] = document.getElementById('trophy_slider').value
    // result['data'] = window.processed_data
    result['data'] = document.getElementById('trophy_slider').value
    submit_filters(result)
};

$("#your_team_filter").on("change", function () {
    get_filter_vals()
});

$("#opponent_team_filter").on("change", function () {
    get_filter_vals()
});

$("#game_mode_filter").on("change", function () {
    get_filter_vals()
});

$("#battle_time_filter").on("change", function () {
    get_filter_vals()
});
