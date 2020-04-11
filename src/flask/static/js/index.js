let initDepression = depressionData;
let initHeartDisease = heartDiseaseData;
let initDomesticAbuse = domesticAbuseData;
let confirmedTimeSeries = JSON.parse(confirmedCovidTimeSeries);
let deathTimeSeries = JSON.parse(deathCovidTimeSeries);
let recoveredTimeSeries = JSON.parse(recoveredCovidTimeSeries);
let confirmedTimeSeriesDiff = JSON.parse(confirmedCovidTimeSeriesDiff);
let deathTimeSeriesDiff = JSON.parse(deathCovidTimeSeriesDiff);
let recoveredTimeSeriesDiff = JSON.parse(recoveredCovidTimeSeriesDiff);

//There was a total of 170,993 casualties of all severities in reported road traffic accidents in 2017.
let initRoadCasualties = 170993;

// Thanks to https://stackoverflow.com/a/2901298
function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function setBaseCovidData(dataFreq, dataType) {
    if (dataFreq === 'total') {
        if (dataType === 'confirmed') {
            baseCovidData = confirmedTimeSeries
        } else if (dataType === 'deaths') {
            baseCovidData = deathTimeSeries;
        } else {
            baseCovidData = recoveredTimeSeries
        }
    } else if (dataFreq == 'new') {
        if (dataType === 'confirmed') {
            baseCovidData = confirmedTimeSeriesDiff
        } else if (dataType === 'deaths') {
            baseCovidData = deathTimeSeriesDiff;
        } else {
            baseCovidData = recoveredTimeSeriesDiff
        }
    } else {
        // Invalid dataFreq passed, so just set it to the confirmed data.
        baseCovidData = confirmedTimeSeries
    }
    return baseCovidData
}

function SetDyGraphData(data, countries) {
    let dyGraphLabels = ["Date"];
    let dyGraphData = [];

    for (let i = 0; i < Object.keys(data['Date']).length; i++) {
        let tempGraphData = [new Date(data['Date'][i])];
        for (let j = 0; j < countries.length; j++) {
            let country = countries[j];
            dyGraphLabels[j + 1] = country;
            tempGraphData[j + 1] = data[country][i];
        }
        dyGraphData[i] = tempGraphData;
    }
    return {
        Labels: dyGraphLabels,
        Data: dyGraphData
    }
}

function legendFormatter(data) {
    if (data.x == null) {
        // This happens when there's no selection and {legend: 'always'} is set.
        return '<br>' + data.series.map(function (series) {
            return series.dashHTML + ' ' + series.labelHTML
        }).join('<br>');
    }

    var html = this.getLabels()[0] + ': ' + data.xHTML;
    data.series.forEach(function (series) {
        if (!series.isVisible) return;
        var labeledData = series.labelHTML + ': ' + series.yHTML;
        if (series.isHighlighted) {
            labeledData = '<b>' + labeledData + '</b>';
        }
        html += '<br>' + series.dashHTML + ' ' + labeledData;
    });
    return html;
}

// Set the default values to UK and Total and render the graph with UK confirmed cases (COVID line graph)
function setDefaultPage() {
    $('#dataFreqSelect').selectpicker('val', 'total');
    $('#countrySelector').selectpicker('val', 'United Kingdom');
    document.getElementById("covidNumber").innerHTML = numberWithCommas(totalCases);
    // document.getElementById("dataDate").innerHTML = "As of " + totalCasesDate;
}

setDefaultPage();
let getDyGraphData = SetDyGraphData(confirmedTimeSeries, ['United Kingdom']);
let dyGraphLabels = getDyGraphData.Labels;
let dyGraphData = getDyGraphData.Data;

// Add styling to the selected button even when out of focus.
$(".timeRangeButton").on('click', function (e) {
    $(".timeRangeButton").removeClass('buttonActive');
    $(this).addClass('buttonActive');
});

//Clicking the 'Total' button
    document.getElementById("timeRangeButton1").onclick = function () {
    document.getElementById("covidNumber").innerHTML = numberWithCommas(totalCases);
    // document.getElementById("dataDate").innerHTML = "As of " + totalCasesDate;

    // Update the chart data and redraw
    // heartDiseaseData = initHeartDisease;
    // depressionData = initDepression;
    // domesticAbuseData = initDomesticAbuse;
    //
    // barChart.data.datasets = [{
    //     label: '',
    //     data: [heartDiseaseData, depressionData, domesticAbuseData],
    //     backgroundColor: ['#FF9D9E', '#D02F46', '#FF9D9E'],
    //     borderColor: ['#000000', '#000000', '#000000'],
    //     borderWidth: 1,
    //     hoverBorderWidth: 2
    // }];
    //
    // barChart.options.annotation.annotations[0].value = totalCases;
    //
    // barChart.update();
};

// Clicking the '7 Days' button
document.getElementById("timeRangeButton2").onclick = function () {
    document.getElementById("covidNumber").innerHTML = numberWithCommas(cases7Days);
    // document.getElementById("dataDate").innerHTML = "New cases in the 7 day period " + cases7DaysDate;

    // Update the chart data and redraw
    // heartDiseaseData = Math.round(initHeartDisease * (7 / 365));
    // depressionData = Math.round(initDepression * (7 / 365));
    // domesticAbuseData = Math.round(initDomesticAbuse * (7 / 365));

    // Apparently, this should work. But just updating the chart data does not redraw the chart, hence we have the
    // Solution implemented below i.e. redefine the entire datasets option

    // barChart.data.datasets.data = [heartDiseaseData, depressionData, domesticAbuseData]

    // barChart.data.datasets = [{
    //     label: '',
    //     data: [heartDiseaseData, depressionData, domesticAbuseData],
    //     backgroundColor: ['#FF9D9E', '#D02F46', '#FF9D9E'],
    //     borderColor: ['#000000', '#000000', '#000000'],
    //     borderWidth: 1,
    //     hoverBorderWidth: 2
    // }];
    //
    // barChart.options.annotation.annotations[0].value = cases7Days;
    //
    // barChart.update();
};

//Clicking the '24 hours' button.
document.getElementById("timeRangeButton3").onclick = function () {
    document.getElementById("covidNumber").innerHTML = numberWithCommas(cases24H);
    // document.getElementById("dataDate").innerHTML = "New cases in the 24H period " + cases24HDate;

    // Update the chart data and redraw
    // heartDiseaseData = Math.round(initHeartDisease / 365);
    // depressionData = Math.round(initDepression / 365);
    // domesticAbuseData = Math.round(initDomesticAbuse / 365);
    //
    //
    // barChart.data.datasets = [{
    //     label: '',
    //     data: [heartDiseaseData, depressionData, domesticAbuseData],
    //     backgroundColor: ['#FF9D9E', '#D02F46', '#FF9D9E'],
    //     borderColor: ['#000000', '#000000', '#000000'],
    //     borderWidth: 1,
    //     hoverBorderWidth: 2
    // }];
    //
    // barChart.options.annotation.annotations[0].value = cases24H;
    //
    // barChart.update();

};

// We are going to use this variable for the data in all charts. When the user chooses a different data type, we
// will just update this variable to have the correct data for simplicity.

let baseCovidData = confirmedTimeSeries;

//Changing the countries to see data for in line chart

$('#countrySelector').on('change', function (e) {
    let selectedItems = $('#countrySelector').val();

    let getDyGraphData = SetDyGraphData(baseCovidData, selectedItems);
    let dyGraphLabels = getDyGraphData.Labels;
    let dyGraphData = getDyGraphData.Data;
    covidGraph.updateOptions({
        'file': dyGraphData,
        'labels': dyGraphLabels
    })
});

//Changing the data type for line graph

$('#covidTypeSelect').on('change', function (e) {
    let typeSelected = $('#covidTypeSelect').val();
    let selectedItems = $('#countrySelector').val();
    let dataTypeSelected = $('#dataFreqSelect').val();

    baseCovidData = setBaseCovidData(dataTypeSelected, typeSelected);

    let getDyGraphData = SetDyGraphData(baseCovidData, selectedItems);
    let dyGraphLabels = getDyGraphData.Labels;
    let dyGraphData = getDyGraphData.Data;

    covidGraph.updateOptions({
        'file': dyGraphData,
        'labels': dyGraphLabels
    })
});

//Changing the data frequency for the line graph

$('#dataFreqSelect').on('change', function (e) {
    let dataTypeSelected = $('#dataFreqSelect').val();
    let typeSelected = $('#covidTypeSelect').val();
    let selectedItems = $('#countrySelector').val();

    baseCovidData = setBaseCovidData(dataTypeSelected, typeSelected);

    let getDyGraphData = SetDyGraphData(baseCovidData, selectedItems);
    let dyGraphLabels = getDyGraphData.Labels;
    let dyGraphData = getDyGraphData.Data;

    covidGraph.updateOptions({
        'file': dyGraphData,
        'labels': dyGraphLabels
    })
});


// Define data for the graphs and render them below.

// Bar chart data
let data = {
    labels: ['Domestic Abuse', 'Depression', 'Road Casualties'],
    datasets: [{
        label: '',
        data: [initDomesticAbuse, initDepression, initRoadCasualties],
        backgroundColor: ['#FF9D9E', '#FF9D9E', '#FF9D9E'],
        borderColor: ['#D02F46', '#D02F46', '#D02F46'],
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
        }],
        xAxes: [{
            gridLines: {
                display: false
            }
        }]
    },
    legend: {
        display: false
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
    maintainAspectRatio: false
    // annotation: {
    //     annotations: [{
    //         type: 'line',
    //         mode: 'horizontal',
    //         scaleID: 'y-axis-0',
    //         value: totalCases,
    //         borderColor: 'red',
    //         borderWidth: 2,
    //         label: {
    //             enabled: true,
    //             backgroundColor: '#3F054E',
    //             content: 'COVID Cases',
    //             fontSize: 10,
    //             fontColor: "#fff",
    //             position: 'center'
    //         }
    //     }]
    // }
};

let barChart = new Chart(ctx, {
    type: 'bar',
    data: data,
    options: options
});

// Line graph for COVID cases
let covidGraph = new Dygraph(document.getElementById('covidTimeSeries'),
    dyGraphData,
    {
        labels: dyGraphLabels,
        showRangeSelector: true,
        legend: 'always',
        // ylabel: 'Number of cases',
        title: 'Comparisons across countries',
        axes: {
            y: {
                valueFormatter: function (x) {
                    return numberWithCommas(x)
                },
                axisLabelFormatter: function (x) {
                    return numberWithCommas(x)
                }
            },
            x: {
                valueFormatter: function (d) {
                    return new Date(d).toLocaleDateString();
                }
            }
        },
        highlightSeriesOpts: {'strokeWidth': 2},
        legendFormatter: legendFormatter,
        labelsDiv: document.getElementById('covidLegend'),
        hideOverlayOnMouseOut: true,
        labelsSeparateLines: true,
        xRangePad: 50,
        titleHeight: 50,
        colors: ['#49006a', '#7a0177', '#ae017e', '#dd3497', '#f768a1', '#fa9fb5', '#fcc5c0', '#fde0dd', '#fff7f3']
    }
);
