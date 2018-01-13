//Create object for numbering name attributes of lift and cardio rows
var nameNumberManager = {

    reNameNumberAll: function(){
        var liftRows = this.getLiftRows();
        this.reNameNumberLiftRows(liftRows);

        var cardioRows = this.getCardioRows();
        this.reNameNumberCardioRows(cardioRows);
    },
    getLiftRows: function(){
        var liftRows = document.getElementById("liftrows").querySelectorAll('.liftrow');
        return liftRows;
    },
    getCardioRows: function(){
        var cardioRows = document.getElementById("cardiorows").querySelectorAll('.cardiorow');
        return cardioRows;
    },
    reNameNumberLiftRows: function(liftRows){
        for(var i=0; i<liftRows.length; i++){
            var liftRow = liftRows[i];
            var liftNameField = liftRow.querySelectorAll('.liftname')[0];
            var setField = liftRow.querySelectorAll('.setfield')[0];
            var repFields = liftRow.querySelectorAll('.repfield');
            var weightFields = liftRow.querySelectorAll('.weightfield');

            liftNameField.name = 'lift_name'+i;
            setField.name = 'sets'+i;

            if(!repFields){
                continue;
            }
            for(var j=0; j<repFields.length; j++){
                repFields[j].name = 'reps'+i;
            }
            for(var j=0; j<weightFields.length; j++){
                weightFields[j].name = 'weight'+i;
            }

        }
    },
    reNameNumberCardioRows: function(cardioRows){
        for(var i=0; i<cardioRows.length; i++){
            console.log(i);
            var cardioRow = cardioRows[i];
            var activityField = cardioRow.querySelectorAll('.cardioname')[0];
            var minField = cardioRow.querySelectorAll('.minfield')[0];
            var distField = cardioRow.querySelectorAll('.distfield')[0];

            activityField.name = 'cardio_name'+i;
            minField.name = 'duration'+i;
            distField.name = 'distance'+i;
        }
    },
}

//Adding numbering of name attribute for fields onsubmit on form
var workoutform = document.getElementById('workoutform');
if(workoutform.addEventListener){
    workoutform.addEventListener('submit', function(event){
        event.preventDefault();
        nameNumberManager.reNameNumberAll();
        this.submit();
    }, true);
}

//Adding onkeyup event to textboxes
var dropdowns = document.getElementsByClassName("dropdowntextbox");
if(dropdowns){
    for (var i=0; i<dropdowns.length; i++){
        textbox = dropdowns[i].getElementsByTagName('input')[0];
        textbox.onkeyup = getDBMatches;
    }
}
//Adding onkeyup to setsfield
var setsFields = document.getElementsByClassName('setfield');
if(setsFields){
    for (var i=0; i<setsFields.length; i++){
        setsField = setsFields[i];
        setsField.onkeyup = setsField.onchange = insertRepAndWeightFields;
    }
}
//Adding onclick to buttons
var addLiftButton = document.getElementById('addliftbutton');
if(addLiftButton){
    addLiftButton.onclick = addLiftRow;
}
var addCardioButton = document.getElementById('addcardiobutton');
if(addCardioButton){
addCardioButton.onclick = addCardioRow;
}

//Adding event to back-to-calendar button
var calendarButton = document.getElementById('calendarbutton');
if(calendarButton){
    calendarButton.onclick = backToCalendar;
}

//Clicking away the dropdown menu in liftfield
window.onclick = function(event){
    t = event.target;
    dropdivs = document.getElementsByClassName('dropdowntextbox');

    // If we clicked into the dropdown, don't do anything
    for(var i=0; i<dropdivs.length; i++){
        if(dropdivs[i].contains(event.target)){
            return;
        }
    }

    // If we clicked into the textbox, also don't do anything
    if(t.matches('.dropdowntext')){
        return;
    }

    dropdowns = document.getElementsByClassName('dropdown-content');
    for(var i=0; i<dropdowns.length; i++){
        var dropdown = dropdowns[i];
        if(dropdown.classList.contains('show')){
            dropdown.classList.remove('show');
        }
    }
};

function createXHR(){
    if (typeof XMLHttpRequest !== "undefined"){
        return new XMLHttpRequest;
    } else if (typeof createXHR.activeXString != "string"){
        var versions = ["MSXML2.XMLHttp.6.0","MSXML2.XMLHttp.3.0","MSXML2.XMLHttp"],
        i, len;

        for(i=0, len=versions.length; i < len; i++){
            try {
                createXHR.activeXString = versions[i];
                return new ActiveXObject(versions[i]);
            } catch(ex){
                createXHR.activeXString=undefined;
            }
        }

        throw new Error("No XHR available");
    } else {
        return new ActiveXObject(createXHR.activeXString);
    }
}

function addURLParam(url, name, value){
    url += (url.indexOf("?") == -1 ? "?" : "&");
    url += encodeURIComponent(name) + "=" + encodeURIComponent(value);
    return url;
}

function getDBMatches(){// This should only return an array with the matches from the db. Nothing else
    var xhr = createXHR();

    xhr.dropdown = this.parentNode.parentNode.getElementsByClassName("dropdown-content")[0];
    xhr.dropdown.innerHTML = "";
    if(!xhr.dropdown.classList.contains('show')){
        xhr.dropdown.classList.add('show');
    }

    xhr.onreadystatechange = function(){
        if (this.value == ""){
            return;
        }
        if (xhr.readyState == 4){
            if ((xhr.status >= 200 && xhr.status < 300) || xhr.status == 304){

                var xhrResponse = xhr.responseText;

                var dbMatches = JSON.parse(xhrResponse);

                for(var i = 0; i < dbMatches.length; i++){
                    var link = document.createElement("a");
                    link.innerHTML = dbMatches[i]["fields"]["name"];
                    link.onclick = function(){
                        var textbox = link.parentNode.parentNode.getElementsByTagName('input')[0];
                        textbox.value = link.innerHTML;
                        xhr.dropdown.innerHTML = "";
                    };
                    xhr.dropdown.appendChild(link);
                }
            } else {
                document.getElementById("xhrPar").innerHTML = "Request was unsuccessful: "+xhr.status;
            }
        }
    };

    var url = "http://localhost:8000/workoutcal/";
    if (this.name == "lift_name"){
        url += "get_lifts";
    } else if (this.name == "cardio_name"){
        url += "get_cardio";
    } else {
        throw "proper url could not be constructed";
    }
    url = addURLParam(url, this.name, this.value);
    xhr.open("get", url, false);
    xhr.send(null);

}

function insertRepAndWeightFields(){ // Implement removal of boxes if number is lowered, and addition of new boxed (without removing old box values) if number is increased

    //rowDiv = this.parentNode.parentNode.parentNode;
    //var repFieldDiv = document.createElement('div');
    //repFieldDiv.classList.add('col-xs-4 repfields');

    if(this.value < 0){
        return;
    }

    var repFieldsDiv = this.parentNode.parentNode.parentNode.getElementsByClassName('repfields')[0];
    var rowNode = this.parentNode.parentNode.parentNode;
    if(!repFieldsDiv){

        var repFieldsDiv = document.createElement('div');
        var bootstrapClasses = ['col-xs-3', 'col-sm-3', 'col-md-3', 'col-lg-3'];
        addListToClassList(repFieldsDiv, bootstrapClasses.concat(['repfields']));

        var weightFieldsDiv = document.createElement('div');
        addListToClassList(weightFieldsDiv, bootstrapClasses.concat(['weightfields']));

        addInputColumn(this.value, rowNode, "Weight (kg):", weightFieldsDiv, "number", "weight", ["weightfield"], {"step":"0.05"});
        addInputColumn(this.value, rowNode, "No of reps:", repFieldsDiv, "number", "reps", ["repfield"]);

        return;
    }

    var repFieldsCollection = repFieldsDiv.getElementsByTagName('input');
    var noOfRepsFields = repFieldsCollection.length;

    var weightFieldsDiv = this.parentNode.parentNode.parentNode.getElementsByClassName('weightfields')[0];

    if(noOfRepsFields < this.value){
        var diff = this.value - noOfRepsFields;

        for(var i=0; i<diff; i++){
            var repField = createInputField("number", "reps", ["repfield"]);
            var weightField = createInputField("number", "weight", ["weightfield"], {"step":"0.05"});
            repFieldsDiv.getElementsByTagName('label')[0].appendChild(repField);
            weightFieldsDiv.getElementsByTagName('label')[0].appendChild(weightField);
        }
    } else if(noOfRepsFields > this.value){
        var diff = noOfRepsFields - this.value;

        var repLabel = repFieldsDiv.getElementsByTagName('label')[0];
        var weightLabel = weightFieldsDiv.getElementsByTagName('label')[0];
        for(var i=0; i<diff; i++){
            repLabel.removeChild(repLabel.lastChild);
            weightLabel.removeChild(weightLabel.lastChild);
        }
    }
}

function addLiftRow(){
    var liftRowElements = document.getElementById('liftrows');

    var hidden_liftrow = document.getElementById('hidden').querySelectorAll('.liftrow')[0];
    var new_liftrow = hidden_liftrow.cloneNode(true);

    var setField = new_liftrow.getElementsByClassName('setfield')[0];
    setField.onkeyup = setField.onchange = insertRepAndWeightFields;

    liftRowElements.appendChild(new_liftrow);
}

function addCardioRow(){
    var cardiorows = document.getElementById('cardiorows');

    var hidden_cardiorow = document.getElementById('hidden').querySelectorAll('.cardiorow')[0];
    var new_cardiorow = hidden_cardiorow.cloneNode(true);

    cardiorows.appendChild(new_cardiorow);
}

function createObjectFromInputs(){
    var workoutObject = {
        "date":document.getElementById('date').valueAsDate.toJSON()
    };

    //Lifts
    var liftRowElements = document.getElementsByClassName('container')[0].getElementsByClassName('lift');
    for(var i=0; i<liftRowElements.length; i++){
        row = liftRowElements[i];
        var setList = []; //A list with the number of reps for each set
        repFieldsElement = row.getElementsByClassName('repfields')[0];
        if (!repFieldsElement){
            continue;
        }
        repInputElements = repFieldsElement.getElementsByTagName('input');

        for(var i=0; i<repInputElements.length; i++){
            setList.push(repInputElements[i].value);
        }
        var liftName = row.getElementsByClassName('lift')[0].value;
        Object.defineProperty(workoutObject, liftName, {
            value:setList,
            enumerable:true
        });
    }
    //Cardio
    var cardioRowElements = document.getElementsByClassName('container')[0].getElementsByClassName('cardio');
    for(var i=0; i<cardioRowElements.length; i++){
        var row = cardioRowElements[i];
        var cardioActivityElement = row.getElementsByClassName('cardio')[0]
        if(!cardioActivityElement){
            continue
        }
        cardioActivityName = cardioActivityElement.value;
        var noOfMinutes = row.getElementsByClassName('minfield')[0].value;
        var distance = row.getElementsByClassName('distfield')[0].value;
        Object.defineProperty(workoutObject, cardioActivityName, {
            "minutes": noOfMinutes,
            "distance": distance
        });
    }
    return workoutObject;
}

function sendWorkout(){
    var workoutObject = createObjectFromInputs();
}

function backToCalendar(){
    var date = document.getElementById('date').textContent;
    var re = /([0-9]+)-([0-9][0-9]?)\-[0-9][0-9]?/;
    result = re.exec(date);
    var year = result[1];
    var month = result[2];

    url = "/workoutcal/"+year+"/"+month;
    window.location = url;
}

function createInputField(type, name, classList = [], optional = {}){
    var input = document.createElement('input');

    input.type = type;
    input.name = name;
    input.min = 0;

    for(var key in optional){
        var value = optional[key];
        input.setAttribute(key, value);
    }

    for(var i=0; i<classList.length; i++){
        input.classList.add(classList[i]);
    }
    return input;
}

function addListToClassList(node, list){
    for(var i=0; i<list.length; i++){
        node.classList.add(list[i]);
    }
}

function addInputColumn(noOfInputs, parent, header, fieldsDiv, inputType, inputName, inputClassList, optional={}){
    var label = document.createElement('label');
    var labelText = document.createTextNode(header);
    label.appendChild(labelText);
    var br = document.createElement('br');
    label.appendChild(br);

    for (var i=0; i<noOfInputs; i++){
            var inputField = createInputField(inputType, inputName, inputClassList, optional);
            label.appendChild(inputField);
    }

    fieldsDiv.appendChild(label);

    parent.appendChild(fieldsDiv);
}

