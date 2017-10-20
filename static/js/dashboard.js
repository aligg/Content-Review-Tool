var options = {
    responsive: true,
    scales: {
            yAxes: [{ display: true, ticks: { beginAtZero: true
                                             } 
                    }]
            },
    title: {
            display: true,
            text: 'Daily total reviews, last 30 days',
            fontSize: 18,
            fontColor: "rgb(72,72,72)",
            padding: 20
        },
    legend: {
        display: false,
    }
};

var optionsagr = {
    responsive: true,
    scales: {
            yAxes: [{ display: true, ticks: { beginAtZero: true,
                                            callback: function(value){return value+ "%"}
                                             } 
                    }]
            },
    title: {
        display: true,
        text: 'Daily reviewer agreement rate, last 30 days',
        fontSize: 18,
        fontColor: "rgb(72,72,72)",
        padding: 20
        },
    legend: {
        display: false,
    }
};

var optionsaut = {
    responsive: true,
    scales: {
            yAxes: [{ display: true, ticks: { beginAtZero: true,
                                            callback: function(value){return value+ "%"}
                                            
                                             } 
                    }]
            },
    title: {
        display: true,
        text: 'Automation Rate',
        fontSize: 18,
        fontColor: "rgb(72,72,72)",
        padding: 20
        },
    legend: {
        display: true,
    }
};

var ctx_line = $("#dailiesChart").get(0).getContext("2d");

$.get("/dashboard-line-dailies.json", function (data) {
  var myLineChart = Chart.Line(ctx_line, {
                                data: data,
                                options: options
                            });
});


var ctx_line_a = $("#agreementChart").get(0).getContext("2d");

$.get("/dashboard-line-agreement.json", function (data) {
  var myLineChart = Chart.Line(ctx_line_a, {
                                data: data,
                                options: optionsagr
                            });
});

var ctx_line_aut = $("#automationChart").get(0).getContext("2d");

$.get("/dashboard-automation-rate.json", function (data) {
  var myLineChart = Chart.Line(ctx_line_aut, {
                                data: data,
                                options: optionsaut
                            });
});