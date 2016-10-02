$(function(){
    // temp numbers
    var numbers = {domNumbers: [
        {number: 0, domNumber: "OO"},
        {number: 1, domNumber: "OA"},
        {number: 2, domNumber: "OB"},
        {number: 3, domNumber: "OC"}
    ]
    };

    var templateText = $("#tableTemplate").html();
    var template = Handlebars.compile(templateText);
    var renderedText = template(numbers);
    var renderedDom = $(renderedText);
    $("#tableDiv").append(renderedDom);

});