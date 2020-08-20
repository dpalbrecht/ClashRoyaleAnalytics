$("#home_button").on("click", function () {
    window.location.href = '/'
});

$("#deck_rec_button").on("click", function () {
    window.location.href = '/new_decks'
});

$(document).on('submit', '#form', (event) => {
    event.preventDefault()
    const seedValue = $('#seedInput').val()
    get_data(seedValue)
})

function get_data(seedValue) {
    document.getElementById("results_loading_div").style.display = "flex";
    $.ajax({
	        type: 'POST',
	        url: '/process/'+seedValue,
	        contentType: 'application/json; charset=utf-8',
	        data: JSON.stringify({player_tag: seedValue}),
            success: function (template, status, jqXHR) {
                if (jqXHR.status == 200) {
                    window.location.href = '/process/' + seedValue
                } else {
                    alert(`Oh no! This player tag has an error :(
                          // Player tags should only contain these characters:
                          // Numbers: 0, 2, 8, 9
                          // Letters: P, Y, L, Q, G, R, J, C, U, V`);
                    window.location.href = '/'
                }
            }
	    });
};

function render(data) {
    // Show results
    var cards = data['cards']
    var play_counts = data['play_counts']
    var win_percents = data['win_percents']
    var url_dict = data['card_images_dict']

    var result = "<div id=\"row results_table\"><div id=\"results_div\">"
    for (i = 0; i < cards.length; i+=1) {
        if (typeof url_dict[cards[i]] !== 'undefined') {
            result += "<div class=\"col result_box\"><div>"+cards[i]+"</div>"
            result += "<div><img id=\"results_image\" src="+url_dict[cards[i]]+"></div>"
            result += "<div>Play Count: "+play_counts[i]+"</div>"
            result += "<div>Win Rate: "+win_percents[i]+"%</div></div>"
        }
    }
    result += "</div></div>"

    document.getElementById("stats_results").innerHTML = result
};

function show_messages(messages) {
    console.log(messages);
    result = "Oh no! Problem with these filter values:\r\n"
    for (i = 0; i < messages.length; i++) {
        result += "\u2022 "+messages[i]+"\r\n"
    }
    alert(result);
};

function show_number_games(data) {
    document.getElementById("num_games_div").innerHTML = data['num_battles']
};

function show_win_rate(data) {
    document.getElementById("win_rate_div").innerHTML = data['total_win_rate'] + "%"
};
