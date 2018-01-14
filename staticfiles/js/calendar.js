document.getElementById("backbutton").onclick = previousMonth;
document.getElementById("forwardbutton").onclick = nextMonth;

var pageYear = document.getElementById('pageyear').value;
var pageMonth = document.getElementById('pagemonth').value;

function previousMonth(){

    if(pageMonth > 1){
        var month = pageMonth - 1;
        var year = pageYear;
    }
    else if(pageMonth == 1){
        var month = 12;
        var year = pageYear - 1;
    }
    window.location = "/workoutcal/"+year+"/"+month;
}

function nextMonth(){

    if(pageMonth < 12){
        var month = Number(pageMonth) + 1;
        var year = pageYear;
    }
    else if(pageMonth == 12){
        var month = 1;
        var year = Number(pageYear) + 1;
    }
    window.location = "/workoutcal/"+year+"/"+month;
}