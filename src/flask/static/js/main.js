console.log(String(totalCasesDate))
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

});

