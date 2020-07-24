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
        setTimeout(function() {show_messages(data['messages'])},10)
    };
}

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
    result['data'] = window.processed_data
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
