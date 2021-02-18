/***
 * This function uses the JSON-String which is given to her by an 'onClick-Function' to put the plots of the given data to the 'div ' on the object-page.
 *
 * The function makes it possible to get more information about the plot data or to hide
 * @param json_string
 */
function plotlyPlot(json_string) {
    var plot_div = $('#plotly_plot_div');
    var plot_info_link = $('#plot_info_link');
    if(/display:none/.test(plot_div.attr('style'))) {
        plot_div.attr('style', 'height:40vh')
        plot_info_link.html('less info')
        plot(json_string);
    } else {
        plot_div.attr('style', 'display:none');
        plot_info_link.html('more info')
    }

}

/**
 * Help function of plotlyPlot
 * The function gets an JSON-String and plots the different data to a div.
 * The different data for the plots is given as keys in the JSON-String so that it can be chosen.
 * @param json_string
 */
function plot(json_string) {
    var json_string_key_list = Object.keys(json_string);
    Plotly.newPlot('plotly_plot_div');
    var layout = {layout: {barmode: 'stack'}};
    if(json_string_key_list.includes("layout")) {
        layout_string = json_string["layout"];
    }
    for(var i in json_string_key_list) {
        var json_data = json_string[json_string_key_list[i]]
        Plotly.plot('plotly_plot_div', {data: [json_string[json_string_key_list[i]]], 'layout': { layout } });
    }
}
