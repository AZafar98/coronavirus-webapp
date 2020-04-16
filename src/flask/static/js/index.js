let initDepression = depressionData;
let initHeartDisease = heartDiseaseData;
let initDomesticAbuse = domesticAbuseData;
const confirmedTimeSeries = JSON.parse(confirmedCovidTimeSeries);
const deathTimeSeries = JSON.parse(deathCovidTimeSeries);
const recoveredTimeSeries = JSON.parse(recoveredCovidTimeSeries);
const confirmedTimeSeriesDiff = JSON.parse(confirmedCovidTimeSeriesDiff);
const deathTimeSeriesDiff = JSON.parse(deathCovidTimeSeriesDiff);
const recoveredTimeSeriesDiff = JSON.parse(recoveredCovidTimeSeriesDiff);

//There was a total of 170,993 casualties of all severities in reported road traffic accidents in 2017.
const initRoadCasualties = 170993;
//https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland
const ukAdultPopulationEstimate = 50528421;
//https://www.ons.gov.uk/peoplepopulationandcommunity/wellbeing/articles/lonelinesswhatcharacteristicsandcircumstancesareassociatedwithfeelinglonely/2018-04-10
//Figure 1 shows that in 2016 to 2017, there were 5% of adults (aged 16 years and over) in England reporting feeling lonely “often/always”
const percentLonely = 0.05;
const initLoneliness = Math.round(ukAdultPopulationEstimate*percentLonely);

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
    } else if (dataFreq === 'new') {
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
            labeledData = '<strong>' + labeledData + '</strong>';
        }
        html += '<br>' + series.dashHTML + ' ' + labeledData;
    });
    return html;
}

function zoomGraphX(minDate, maxDate) {
    covidGraph.updateOptions({
        dateWindow: [minDate, maxDate]
    })
}

// Set the default values to UK and Total and render the graph with UK confirmed cases (COVID line graph)
function setDefaultPage() {
    $('#dataFreqSelect').selectpicker('val', 'total');
    $('#covidTypeSelect').selectpicker('val', 'confirmed');
    $('#countrySelector').selectpicker('val', 'United Kingdom');
    document.getElementById("covidNumber").innerHTML = numberWithCommas(totalCases);
    // document.getElementById("dataDate").innerHTML = "As of " + totalCasesDate;
}

// Populate the dropdown with all the countries
countryOptions = [];
countriesList.forEach(function(country) {
    const option = "<option " + "value='" + country + "'>" + country + "</option>";
    countryOptions.push(option)
});

$('select[name=countries]').html(countryOptions);
$('.selectpicker').selectpicker('refresh');

// $('#test').qtip({
//     content: {
//         text: 'I have a nice little callout pointer... nifty huh?'
//     }
// });

//Initialise tooltips
$(function () {
  $('[data-toggle="tooltip"]').tooltip({html:true,
      trigger: 'hover focus',
      delay: {"show": 500, "hide": 1000 }})
});

setDefaultPage();
let getDyGraphData = SetDyGraphData(confirmedTimeSeries, ['United Kingdom']);
let dyGraphLabels = getDyGraphData.Labels;
let dyGraphData = getDyGraphData.Data;


//Thanks to https://github.com/JZafar1/Static-Analysis-of-Smart-Contracts/blob/master/src/main/java/ui/js/generateUI.js
/**
 *
 * @param classID the class of the div the tooltip is to be added to
 * @param hiddenDivID the class of the div containing the text to be added to tooltip
 */
function addToolTip(classID, hiddenDivID) {
    //Create a tooltip for each line of output
    $("#" + classID).qtip({
        content: {
            //Get text content from hidden div
            text: $("#" + hiddenDivID)
        },
        show: {
            event: 'mouseover'
        },
        hide: {
            fixed: true,
            delay: 500
        },
        effect: {
            function(pos) {
                $(this).animate(pos, {
                    duration: 1000,
                    queue: false
                });
            }
        },
        position: {
            my: 'top left',
            at: 'bottom right',
            target: $('#' + classID),
            viewport: $(window),
            adjust: {
                method: 'shift flipinvert'
            }
        },
        adjust: {
            mouse: true,
            resize: true
        },
        style: {
            classes: 'qtip-bootstrap qtip-rounded',
            tip: {
                corner: 'top left',
                mimic: 'left'
            }
        }
    })
        .attr('title', 'Help');
}

addToolTip('tooltip1', 'tooltipText1');
addToolTip('tooltip2', 'tooltipText2');
addToolTip('tooltip3', 'tooltipText3');

// Add styling to the selected button even when out of focus.
$(".timeRangeButton").on('click', function (e) {
    $(".timeRangeButton").removeClass('buttonActive');
    $(this).addClass('buttonActive');
});

//Clicking the 'Total' button
    document.getElementById("timeRangeButton1").onclick = function () {
    document.getElementById("covidNumber").innerHTML = numberWithCommas(totalCases);
    // document.getElementById("dataDate").innerHTML = "As of " + totalCasesDate;
};

// Clicking the '7 Days' button
document.getElementById("timeRangeButton2").onclick = function () {
    document.getElementById("covidNumber").innerHTML = numberWithCommas(cases7Days);
    // document.getElementById("dataDate").innerHTML = "New cases in the 7 day period " + cases7DaysDate;
};

//Clicking the '24 hours' button.
document.getElementById("timeRangeButton3").onclick = function () {
    document.getElementById("covidNumber").innerHTML = numberWithCommas(cases24H);
    // document.getElementById("dataDate").innerHTML = "New cases in the 24H period " + cases24HDate;
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


// Bar chart data
let data = {
    labels: ['Depression', 'Domestic Abuse', 'Heart Disease', 'Loneliness', 'Road Casualties'],
    datasets: [{
        label: '',
        data: [initDepression, initDomesticAbuse, initHeartDisease, initLoneliness, initRoadCasualties],
        backgroundColor: ['#FF9D9E', '#FF9D9E', '#FF9D9E', '#FF9D9E', '#FF9D9E'],
        borderColor: ['#D02F46', '#D02F46', '#D02F46', '#D02F46', '#D02F46'],
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
    title: {
        display: true,
        position: 'top',
        fontSize: 20,
        fontFamily: "'Inter', 'Helvetica Neue'",
        padding: 15,
        text: 'What else is bad in the world?'
    },
    responsive: true,
    maintainAspectRatio: false
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
        //Allow drag to zoom as well as range selector
        interactionModel: Dygraph.defaultInteractionModel,
        legend: 'always',
        // ylabel: 'Number of cases',
        title: 'COVID-19 Comparisons',
        axes: {
            y: {
                valueFormatter: function (x) {
                    return numberWithCommas(x)
                },
                axisLabelFormatter: function (x) {
                    return numberWithCommas(x)
                },
                drawGrid: true
            },
            x: {
                valueFormatter: function (d) {
                    return new Date(d).toLocaleDateString();
                },
                drawGrid: false
            }
        },
        highlightSeriesOpts: {'strokeWidth': 3},
        strokeWidth: 2,
        strokeBorderWidth: 1,
        legendFormatter: legendFormatter,
        labelsDiv: document.getElementById('covidLegend'),
        hideOverlayOnMouseOut: true,
        labelsSeparateLines: true,
        xRangePad: 50,
        titleHeight: 50,
        colors: ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6']

    }
);

let maxDate = new Date();
// let minDate = new Date();
//Show data from 7th March. For most countries, the data is very flat and uninteresting before this date.
let minDate = Date.parse('03/07/20');
//Since we only have data up to the previous day, max date is yesterday
maxDate.setDate(maxDate.getDate() - 1 );
//Show the last 3 weeks of data by default
// minDate.setDate(maxDate.getDate() - 21);
zoomGraphX(minDate, maxDate);