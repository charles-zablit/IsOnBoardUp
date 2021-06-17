var PingChart = null;

function UpdateChart(timeframe) {
  query_length = timeframe.toString();
  query_url = ["/data/", query_length, "/"].join("");
  $.ajax({
    method: "GET",
    url: query_url,
    success: function (data) {
      PingChart = new Chart(document.getElementById("Ping Chart"), {
        type: "line",
        data: {
          labels: data.timestamps,
          datasets: [
            {
              label: "Seconds",
              backgroundColor: "rgba(34, 211, 90, 0.8)",
              borderColor: "rgba(34, 211, 90, 0.9)",
              pointRadius: false,
              pointColor: "#3b8bba",
              pointStrokeColor: "rgba(60,141,188,1)",
              pointHighlightFill: "#fff",
              pointHighlightStroke: "rgba(60,141,188,1)",
              fill: true,
              data: data.responsetime,
            },
            {
              label: "Number of attempts",
              backgroundColor: "rgba(66, 120, 255, 0)",
              borderColor: "rgba(66, 120, 255, 0)",
              pointRadius: false,
              pointColor: "#3b8bba",
              pointStrokeColor: "rgba(60,141,188,1)",
              pointHighlightFill: "#fff",
              pointHighlightStroke: "rgba(60,141,188,1)",
              fill: true,
              data: data.numberofattempts,
            },
          ],
        },
        options: {
          responsive: true,
          aspectRatio: 2.5,
          title: {
            display: false,
          },
          legend: {
            display: false,
          },
          tooltips: {
            mode: "index",
            intersect: false,
          },
          hover: {
            mode: "nearest",
            intersect: true,
          },
          scales: {
            xAxes: [
              {
                display: true,
                scaleLabel: {
                  display: true,
                  labelString: "Time of query",
                  fontColor: "#e3e3e3",
                },
                ticks: {
                  fontColor: "#e3e3e3",
                },
              },
            ],
            yAxes: [
              {
                display: true,
                scaleLabel: {
                  display: true,
                  labelString: "Response time (s)",
                  fontColor: "#e3e3e3",
                },
                ticks: {
                  beginAtZero: true, // minimum value will be 0.
                  fontColor: "#e3e3e3",
                },
              },
            ],
          },
        },
      });
    },
    error: function (data) {
      console.log("Error");
    },
  });
}

$(document).ready(function () {
  UpdateChart(0);
});

$(".timeframe-selector").change(function () {
	if(PingChart!=null){
		PingChart.destroy();
	}
  UpdateChart(this.value);
});
