

var options = {
    responsive: false,
    scales: {
            xAxes: [{ display: true, 
                        ticks: { beginAtZero: true,
                                callback: function(value){return value+ "%"} },
                        position: 'top',
                    }],
            yAxes: [{ barPercentage: 1,
                        categoryPercentage: .9,
                        maxBarThickness: 30,
                        ticks: {
                            fontSize: 15
                        }
                    }]
            },
    title: {
            display: true,
            text: 'Safety Scores by Subreddit',
            fontSize: 18,
            fontColor: "rgb(72,72,72)",
            padding: 20
        },
    legend: {
        display: false,
    }
};



var insights_bar = $("#insightsChart").get(0).getContext("2d");

$.get("/dashboard-sub-safety-scores.json", function (data) {
  var myBarChart = new Chart(insights_bar, {
                                type: 'horizontalBar',
                                data: data,
                                options: options
                            });
});

