/***
 * This script should be able to recognize which input fields have the opportunity to figure out a term that is given as an attribute.
 * To make this possible there are the following steps:
 *  1. check every input field if ist has got the attribute 'formula' (testIfCalculatedInput())
 *  2. if the input field has got this attribute find the variables in the term and set an onblur so that if the user actualizes the variable the field will be actualized too (setOnBlur())
 * @param inp
 */

var calculatedQuantityList = [];

function testIfCalculatedInput(inp) {

   if($('input[name="' + inp + '"]')[0].hasAttribute('formula')) {
        calculatedQuantityList.push(inp);
        setOnBlur(inp);
    }
}

function setOnBlur(inp) {
     var actualFormula = $('input[name="' + inp + '"]').attr('formula');

     var variables = new RegExp("([a-z]+[a-zA-Z0-9]*)");
     while(variables.test(actualFormula)) {
         var match  = actualFormula.match(variables)[1];
         var str = "";
         var counter = 0;
         $('input[name^="object__' + match + '"]').each(function() {
             var name = $(this).attr('name');
             if(/.*__magnitude.*/.test(name)) {
                 $('input[name="' + name + '"]').blur(function() {
                    refresh()
                 });
                 if(counter == 0) {
                     str += name.match(/.*(object__)(.+)(__magnitude).*/)[2];
                 } else {
                     str += ";" + name.match(/.*(object__)(.+)(__magnitude).*/)[2];
                 }
                 counter ++;
             }
             actualFormula = actualFormula.replace(match, "");
         });
         $('input[name="object__' + match + '__magnitude"]').blur(function() {
             refresh()
         });
         actualFormula = actualFormula.replace(match, "");
     }
     actualFormula = $('input[name="' + inp + '"]').attr('formula');
     refresh();
}

function refresh() {
    for(var i = 0; i < calculatedQuantityList.length; i++) {
        $('input[name="' + calculatedQuantityList[i]).val(CALCULATOR($('input[name="' + calculatedQuantityList[i]).attr('formula')));
    }
}

$('input').each(function() {
    testIfCalculatedInput($(this).attr('name'));
});





