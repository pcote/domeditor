$(function(){

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


    var saveButtonHandler = function(evt){
        var btn = this;
        console.log(btn);
    };

    var revertButtonHandler = function(evt){
        var btn = this;
        console.log(btn);
    };

    $(".table").on("click", ".saveButton", saveButtonHandler);

    $(".table").on("click", ".revertButton", revertButtonHandler);

});