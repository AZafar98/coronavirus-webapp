console.log(cases24H)
$(document).ready(function () {

    function numberWithCommas(x) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    document.getElementById("covidNumber").innerHTML = numberWithCommas(totalCases);

    document.getElementById("timeRangeButton1").onclick = function () {
        document.getElementById("covidNumber").innerHTML = numberWithCommas(totalCases);
    }

    document.getElementById("timeRangeButton2").onclick = function () {
        document.getElementById("covidNumber").innerHTML = numberWithCommas(cases7Days);
    }

    document.getElementById("timeRangeButton3").onclick = function () {
        document.getElementById("covidNumber").innerHTML = numberWithCommas(cases24H);
    }

});

