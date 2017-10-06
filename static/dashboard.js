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