$(document).ready(function () {
    let initDepression = depressionData;
    let initHeartDisease = heartDiseaseData;
    let initDomesticAbuse = domesticAbuseData;
    let confirmedTimeSeries = JSON.parse(confirmedCovidTimeSeries);
    let deathTimeSeries = JSON.parse(deathCovidTimeSeries);
    let recoveredTimeSeries = JSON.parse(recoveredCovidTimeSeries);

    console.log(confirmedTimeSeries);

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

        barChart.data.datasets = [{
            label: '',
            data: [heartDiseaseData, depressionData, domesticAbuseData],
            backgroundColor: ['#FF9D9E', '#D02F46','#FF9D9E'],
            borderColor: ['#000000', '#000000', '#000000'],
            borderWidth: 1,
            hoverBorderWidth: 2
        }];

        barChart.options.annotation.annotations[0].value = totalCases;

        barChart.update();
    };

    document.getElementById("timeRangeButton2").onclick = function () {
        document.getElementById("covidNumber").innerHTML = numberWithCommas(cases7Days);
        document.getElementById("dataDate").innerHTML = "New cases in the 7 day period " + cases7DaysDate;

        // Update the chart data and redraw
        heartDiseaseData = Math.round(initHeartDisease * (7 / 365));
        depressionData = Math.round(initDepression * (7 / 365));
        domesticAbuseData = Math.round(initDomesticAbuse * (7 / 365));

        // Apparently, this should work. But just updating the chart data does not redraw the chart, hence we have the
        // Solution implemented below i.e. redefine the entire datasets option

        // barChart.data.datasets.data = [heartDiseaseData, depressionData, domesticAbuseData]


        barChart.data.datasets = [{
            label: '',
            data: [heartDiseaseData, depressionData, domesticAbuseData],
            backgroundColor: ['#FF9D9E', '#D02F46', '#FF9D9E'],
            borderColor: ['#000000', '#000000', '#000000'],
            borderWidth: 1,
            hoverBorderWidth: 2
        }];

        barChart.options.annotation.annotations[0].value = cases7Days;

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
            label: '',
            data: [heartDiseaseData, depressionData, domesticAbuseData],
            backgroundColor: ['#FF9D9E', '#D02F46', '#FF9D9E'],
            borderColor: ['#000000', '#000000', '#000000'],
            borderWidth: 1,
            hoverBorderWidth: 2
        }];

        barChart.options.annotation.annotations[0].value = cases24H;

        barChart.update();

    };


    let data = {
        labels: ['Heart Disease', 'Depression', 'Domestic Abuse'],
        datasets: [{
            label: '',
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
        annotation: {
        annotations: [{
            type: 'line',
            mode: 'horizontal',
            scaleID: 'y-axis-0',
            value: totalCases,
            borderColor: 'red',
            borderWidth: 2,
            label: {
                enabled: true,
                backgroundColor: '#3F054E',
                content: 'COVID Cases',
                fontSize: 10,
                fontColor: "#fff",
                position: 'center'
            }
        }]
    }
    };

    // We are going to use this variable for the data in all charts. When the user chooses a different data type, we
    // will just update this variable to have the correct data for simplicity.

    let baseCovidData = confirmedTimeSeries;

    $('#countrySelector').on('change', function (e) {
        let selectedItems = $('#countrySelector').val();
        dyGraphData(baseCovidData, selectedItems);
        covidGraph.updateOptions({
            'file': window.dyGraphData,
            'labels': window.dyGraphLabels
        })
    });

    $('#covidTypeSelect').on('change', function(e) {

        let typeSelected = $('#covidTypeSelect').val();
        let selectedItems = $('#countrySelector').val();

        if (typeSelected === 'confirmed') {
            baseCovidData = confirmedTimeSeries
        } else if (typeSelected === 'deaths') {
            baseCovidData = deathTimeSeries;
        } else {
            baseCovidData = recoveredTimeSeries
        }

        dyGraphData(baseCovidData, selectedItems);
        covidGraph.updateOptions({
            'file': window.dyGraphData,
            'labels': window.dyGraphLabels
        })
    });

    let barChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: options
    });

    function dyGraphData(data, countries) {
        window.dyGraphLabels = ["x"];
        window.dyGraphData = [];

        for (let i = 0; i < Object.keys(data['Date']).length; i++) {
            let tempGraphData = [new Date(data['Date'][i+1])];
            for (let j = 0; j < countries.length; j++) {
                let country = countries[j];
                window.dyGraphLabels[j + 1] = country;
                tempGraphData[j + 1] = data[country][i];
            }
            window.dyGraphData[i] = tempGraphData;
        }
    }

    // Set the defauly value to UK and render the graph with UK confirmed cases
    $('#countrySelector').selectpicker('val', 'United Kingdom');
    dyGraphData(confirmedTimeSeries, ['United Kingdom']);

    let covidGraph = new Dygraph(document.getElementById('covidTimeSeries'),
        window.dyGraphData,
        {
            labels: window.dyGraphLabels,
            showRangeSelector: true,
            legend: 'always',
            ylabel: 'Number of cases',
            title: 'Comparisons across countries',
            axes: {
                y: {
                    valueFormatter: function(x) {
                        return numberWithCommas(x)
                    },
                    axisLabelFormatter: function(x) {
                        return numberWithCommas(x)
                    }
                }
            }
        }
    );
});
