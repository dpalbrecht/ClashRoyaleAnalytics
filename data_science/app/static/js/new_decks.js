$("#possible_cards_filter").on("change", function () {
    var selected_cards = []
    var selected_cards_html = ``
    var children = $('#possible_cards_filter').children()
    for (j=0; j<children.length; j++) {
        if (typeof children[j].attributes[2] !== 'undefined') {
            var selected_card = children[j].text
            selected_cards.push(selected_card);
            selected_cards_html += `<div class="col result_box">
                                        <div>`+selected_card+`</div>
                                        <div><img id="results_image" src=`+window.card_images_dict[selected_card]+`></div>
                                    </div>`
        };
    };
    document.getElementById("base_deck_div").innerHTML = selected_cards_html

    if (selected_cards.length==8) {
        window.selected_cards = selected_cards
        $("#submit_new_decks").prop('disabled', false);
    } else {
        $("#submit_new_decks").prop('disabled', true);
    }
;});

$("#submit_new_decks").on("click", function () {
    $.ajax({
	        type: 'POST',
	        url: '/find_new_decks',
	        contentType: 'application/json; charset=utf-8',
	        data: JSON.stringify({selected_cards: window.selected_cards}),
            success: function (data) {
                var data = data['new_decks']
                var out = ``
                for (i=0; i<data.length; i++) {
                    var new_cards = data[i]
                    var row_num = i+1;
                    out += `<div class="row">
                    <div class = "col" id="num_result_box">`+row_num+'.'+`</div>`
                    for (j=0; j<new_cards.length; j++) {
                        out += `<div class="col result_box">
                                    <div>`+new_cards[j]+`</div>
                                    <div><img id="results_image" src=`+window.card_images_dict[new_cards[j]]+`></div>
                                </div>`
                    }
                    out += `</div><div id="new_decks_spacer"></div>`
                }
                document.getElementById("show_new_deck_container").innerHTML = out
            }
	    });
});
