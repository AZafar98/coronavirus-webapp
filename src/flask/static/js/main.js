$(document).ready(function () {

    // Thanks to https://stackoverflow.com/a/2901298
    function numberWithCommas(x) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    document.getElementById("covidNumber").innerHTML = numberWithCommas(totalCases);
    document.getElementById("dataDate").innerHTML = totalCasesDate;


    document.getElementById("timeRangeButton1").onclick = function () {
        document.getElementById("covidNumber").innerHTML = numberWithCommas(totalCases);
        document.getElementById("dataDate").innerHTML = totalCasesDate;
    };

    document.getElementById("timeRangeButton2").onclick = function () {
        document.getElementById("covidNumber").innerHTML = numberWithCommas(cases7Days);
        document.getElementById("dataDate").innerHTML = cases7DaysDate;

    };

    document.getElementById("timeRangeButton3").onclick = function () {
        document.getElementById("covidNumber").innerHTML = numberWithCommas(cases24H);
        document.getElementById("dataDate").innerHTML = cases24HDate;

    };
    //
    // let graphData = [{
    //     x: ['Heart Disease', 'Depression'],
    //     y: [heartDiseaseData, depressionData],
    //     type: 'bar'
    //     }
    // ];

    // Plotly.newPlot('graphArea', graphData);

    var chart = new CanvasJS.Chart("graphArea", {
	animationEnabled: true,
	theme: "light2", // "light1", "light2", "dark1", "dark2"
    backgroundColor: "#FFF8F6",
	axisY: {
		title: "No. People"
	},
	data: [{
		type: "column",
		showInLegend: true,
		legendMarkerColor: "grey",
		legendText: "Source: Public Health England.",
		dataPoints: [
			{ y: heartDiseaseData, label: "Heart Disease" },
			{ y: depressionData,  label: "Depression" }
		]
	}]
});
chart.render();

});


