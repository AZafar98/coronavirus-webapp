$(document).ready(function () {

    let initDepression = depressionData;
    let initHeartDisease = heartDiseaseData;

    // Thanks to https://stackoverflow.com/a/2901298
    function numberWithCommas(x) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    document.getElementById("covidNumber").innerHTML = numberWithCommas(totalCases);
    document.getElementById("dataDate").innerHTML = "As of " + totalCasesDate;


    document.getElementById("timeRangeButton1").onclick = function () {
        document.getElementById("covidNumber").innerHTML = numberWithCommas(totalCases);
        document.getElementById("dataDate").innerHTML = "As of " + totalCasesDate;

        // Update the chart data and redraw
        heartDiseaseData = initHeartDisease;
        depressionData = initDepression;

        chart.options.data[0].dataPoints = [
            {y: heartDiseaseData, label: "Heart Disease"},
            {y: depressionData, label: "Depression"}
        ];
        chart.render();

    };

    document.getElementById("timeRangeButton2").onclick = function () {
        document.getElementById("covidNumber").innerHTML = numberWithCommas(cases7Days);
        document.getElementById("dataDate").innerHTML = "New cases in the 7 day period " + cases7DaysDate;

        // Update the chart data and redraw
        heartDiseaseData = Math.round(initHeartDisease * (7/365));
        depressionData = Math.round(initDepression * (7/365));

        chart.options.data[0].dataPoints = [
            {y: heartDiseaseData, label: "Heart Disease"},
            {y: depressionData, label: "Depression"}
            ];
        chart.render();
    };

    document.getElementById("timeRangeButton3").onclick = function () {
        document.getElementById("covidNumber").innerHTML = numberWithCommas(cases24H);
        document.getElementById("dataDate").innerHTML = "New cases in the 24H period " + cases24HDate;

        // Update the chart data and redraw
        heartDiseaseData = Math.round(initHeartDisease / 365);
        depressionData = Math.round(initDepression / 365);

        chart.options.data[0].dataPoints = [
            {y: heartDiseaseData, label: "Heart Disease"},
            {y: depressionData, label: "Depression"}
        ];
        chart.render();

    };

    CanvasJS.addColorSet("chartColors", ["#FF9D9E", "#D02F46"]);

    let chart = new CanvasJS.Chart("graphArea", {
        animationEnabled: true,
        theme: "light2", // "light1", "light2", "dark1", "dark2"
        backgroundColor: "#FFF8F6",
        colorSet: "chartColors",
        axisY: {
            title: "No. People"
        },
        data: [{
            type: "column",
            showInLegend: true,
            legendMarkerColor: "grey",
            legendText: "Source: Public Health England.",
            dataPoints: [
                {y: heartDiseaseData, label: "Heart Disease"},
                {y: depressionData, label: "Depression"}
            ]
        }]
    });
    chart.render();

});


