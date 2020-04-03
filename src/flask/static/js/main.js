$(document).ready(function () {

    let initDepression = depressionData;
    let initHeartDisease = heartDiseaseData;
    let initDomesticAbuse = domesticAbuseData

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
        domesticAbuseData = initDomesticAbuse;

        // chart.options.data[0].dataPoints = [
        //     {y: heartDiseaseData, label: "Heart Disease"},
        //     {y: depressionData, label: "Depression"}
        // ];
        // chart.render();

        barChart.data.datasets = [{
            label: 'test',
            data: [heartDiseaseData, depressionData, domesticAbuseData],
            backgroundColor: ['#FF9D9E', '#D02F46','#FF9D9E'],
            borderColor: ['#000000', '#000000', '#000000'],
            borderWidth: 1,
            hoverBorderWidth: 2
        }];

        barChart.update();
    };

    document.getElementById("timeRangeButton2").onclick = function () {
        document.getElementById("covidNumber").innerHTML = numberWithCommas(cases7Days);
        document.getElementById("dataDate").innerHTML = "New cases in the 7 day period " + cases7DaysDate;

        // Update the chart data and redraw
        heartDiseaseData = Math.round(initHeartDisease * (7 / 365));
        depressionData = Math.round(initDepression * (7 / 365));
        domesticAbuseData = Math.round(initDomesticAbuse * (7 / 365));

        barChart.data.datasets = [{
            label: 'test',
            data: [heartDiseaseData, depressionData, domesticAbuseData],
            backgroundColor: ['#FF9D9E', '#D02F46', '#FF9D9E'],
            borderColor: ['#000000', '#000000', '#000000'],
            borderWidth: 1,
            hoverBorderWidth: 2
        }];

        barChart.update();
    };

    document.getElementById("timeRangeButton3").onclick = function () {
        document.getElementById("covidNumber").innerHTML = numberWithCommas(cases24H);
        document.getElementById("dataDate").innerHTML = "New cases in the 24H period " + cases24HDate;

        // Update the chart data and redraw
        heartDiseaseData = Math.round(initHeartDisease / 365);
        depressionData = Math.round(initDepression / 365);
        domesticAbuseData = Math.round(initDomesticAbuse / 365);


        barChart.data.datasets = [{
            label: 'test',
            data: [heartDiseaseData, depressionData, domesticAbuseData],
            backgroundColor: ['#FF9D9E', '#D02F46', '#FF9D9E'],
            borderColor: ['#000000', '#000000', '#000000'],
            borderWidth: 1,
            hoverBorderWidth: 2
        }];

        barChart.update();

    };


    let data = {
        labels: ['Heart Disease', 'Depression', 'Domestic Abuse'],
        datasets: [{
            label: 'test',
            data: [heartDiseaseData, depressionData, domesticAbuseData],
            backgroundColor: ['#FF9D9E', '#D02F46', '#FF9D9E'],
            borderColor: ['#000000', '#000000', '#000000'],
            borderWidth: 1,
            hoverBorderWidth: 2
        }]
    };

    let ctx = document.getElementById('graphArea');

    let options = {
        // For labelling the axes and tooltips properly:
        // https://stackoverflow.com/a/48996286

        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                    callback: function (value) {
                        return numberWithCommas(value);
                    }
                }
            }]
        },
        tooltips: {
            callbacks: {
                label: function (tooltipItem, chart) {
                    let datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                    return datasetLabel + ': ' + numberWithCommas(tooltipItem.yLabel);

                }
            }
        },
        responsive: true,
        maintainAspectRatio: false,
    };

    let barChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: options
    })
});


