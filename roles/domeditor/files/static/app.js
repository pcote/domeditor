$(function(){

    /********** Utility functions for formatting dom numbers and getting/setting field vals********/
    var twoDigitFormat = function(num){
        strNum = String(num);
        if(strNum.length === 1){
            strNum = "0" + strNum;
        }
        return strNum;
    };

    var domNumberFormat = function(num){
        var num = twoDigitFormat(num);
        var digitMap = {"0":"O",
            "1":"A","2":"B", "3":"C",
            "4":"D", "5":"E", "6":"S",
            "7":"G", "8":"H", "9":"N"};

        var domNumber = "";
        domNumber = digitMap[num[0]];
        domNumber = domNumber + digitMap[num[1]];
        return domNumber;
    };

    var numberFromName = function(name){
        var numberLoc = name.search(/\d+/);
        var numberString = name.substring(numberLoc);
        var num = Number(numberString);
        return num;
    };

    var getFieldValue = function(fieldBase, fieldNum){
        var twoDigitNum = twoDigitFormat(fieldNum);
        var fieldId = "#" + fieldBase + twoDigitNum;
        return $(fieldId).val();
    };

    var setFieldValue = function(fieldBase, fieldNum, fieldVal){
        var twoDigitNum = twoDigitFormat(fieldNum);
        var fieldId = "#" + fieldBase + twoDigitNum;
        $(fieldId).val(fieldVal);
    };

    /************ end of do dom number utility functions **********************/


    /************** On page load, generate the base dom number table**************/
    var i;
    var numList = _.range(0,100);
    var domNumbers = [];
    for(i=0; i < numList.length; i++ ){
        var twoDigitNum = twoDigitFormat(numList[i]);
        var domNumForm = domNumberFormat(numList[i]);
        domNumbers = domNumbers.concat( {number: twoDigitNum, domNumber: domNumForm});
    }

    domNumbers = {"domNumbers": domNumbers};

    var templateText = $("#tableTemplate").html();
    var template = Handlebars.compile(templateText);
    var renderedText = template(domNumbers);
    var renderedDom = $(renderedText);
    $("#tableDiv").append(renderedDom);

    /***************** end base dom number table generation ********************/


    /************ ajax functions for saving and reverting dom numbers ***************/
    var getCreds = function(){
        var req = {
            url: "/usercreds",
            method: "get"
        };

        var promise = $.ajax(req);
        return promise;
    };

    var saveDomNumber = function(num, pers, act){
        var __callback = function(creds){
            var jsonOb = {number: num, person: pers, action: act};
            var authString = "Basic " + btoa(creds.username + ":" + creds.password);

            var req = {
                url: "/savedomnum",
                method: "post",
                headers: {
                    "Content-type": "application/json",
                    "Authorization": authString
                },
                data: JSON.stringify(jsonOb)
            };

            var promise = $.ajax(req);
            return promise;
        };

        return __callback;
    };


    var declareResult = function(data){
        alert(data);
    };

    var saveButtonHandler = function(evt){
        var btn = this;
        id = btn.getAttribute("id");
        var num = numberFromName(id);
        var person = getFieldValue("person", num);
        var action = getFieldValue("action", num);
        var credsPromise = getCreds();
        var saveDomCB = saveDomNumber(num, person, action);
        var saveDomPromise = credsPromise.then(saveDomCB);
        saveDomPromise.then(declareResult);
    };


    var revertDom = function(num){
        var __callback = function(creds){
            var uname = creds.username;
            var pw = creds.password;
            var authString = "Basic " + btoa(uname + ":" + pw);

            var req = {
                url: "/revert/" + num,
                method: "get",
                headers: {
                    "Authorization": authString
                }
            };

            var promise = $.ajax(req);
            return promise;
        };

        return __callback;
    };


    var updateDomFields = function(data){
        var num = data.number;
        var person = data.person;
        var action = data.action;
        setFieldValue("person", num, person);
        setFieldValue("action", num, action);
    };

    var revertButtonHandler = function(evt){
        var btn = this;
        id = btn.getAttribute("id");
        var num = numberFromName(id);
        var person = getFieldValue("person", num);
        var action = getFieldValue("action", num);
        var credsPromise = getCreds();
        var revertDomCB = revertDom(num);
        var revertDomPromise = credsPromise.then(revertDomCB);
        revertDomPromise.then(updateDomFields);

    };

    $(".table").on("click", ".saveButton", saveButtonHandler);

    $(".table").on("click", ".revertButton", revertButtonHandler);

    /********** end ajax functions for saving and reverting dom numbers **********/
     

    /************ LOAD UP HANDLERS FOR THE PAGE WITH CURRENT DOM NUMBERS FOR THIS USER ****************/
    var downloadDomSet = function(creds){
        var user = creds.username;
        var pw = creds.password;
        var authString = "Basic " + btoa(user + ":" + pw);

        var req = {
            url: "/alldoms",
            method: "get",
            headers: {
                "Authorization": authString
            }
        };

        var promise = $.ajax(req);
        return promise;
    };

    var updateAllFieldsCallback = function(data){
        var domNumbers = data.numbers;
        var i;
        var d;

        for(i=0; i < domNumbers.length; i++){
            d = domNumbers[i];
            setFieldValue("person", d.number, d.person);
            setFieldValue("action", d.number, d.action);
        }
        
    };

    /******************************** END LOADING UP OF DOM NUMBERS *******************/

    var btnResetHandler = function(evt){
        var credPromise = getCreds();
        var downloadPromise = credPromise.then(downloadDomSet);
        downloadPromise.then(updateAllFieldsCallback);
    };

    $("#resetAllButton").click(btnResetHandler);
    $("#resetAllButton").click(); // Done to do the initial value load on page load up.

});