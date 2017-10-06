var options = {
    responsive: true,
    scales: {
            yAxes: [{ display: true, ticks: { beginAtZero: true } }]
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
                                options: options
                            });
});