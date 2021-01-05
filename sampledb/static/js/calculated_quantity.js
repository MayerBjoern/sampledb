var calculatedQuantityList = [];

function testIfCalculatedInput(inp) {

   if($('input[name="' + inp + '"]')[0].hasAttribute('formula')) {
        calculatedQuantityList.push(inp);
        setOnBlur(inp);
    }
}

function setOnBlur(inp) {
     var actualFormula = $('input[name="' + inp + '"]').attr('formula');
     var variables = new RegExp("([a-z]+[a-zA-Z0-9]*)")
     while(variables.test(actualFormula)) {
         var match  = actualFormula.match(variables)[1];
         var str = "";
         $('input[name^="object__' + match + '"]').each(function() {
             var name = $(this).attr('name');
             if(/.*__magnitude.*/.test(name)) {
                 $('input[name="' + name + '"]').blur(function() {
                    refresh()
                 });
                 str += name.match(/.*(object__)(.+)(__magnitude).*/)[2] + ';';
             }
             actualFormula = actualFormula.replace(match, "");
         });
         if(str != "") {
             $('input[name="' + inp + '"]').attr('formula', $('input[name="' + inp + '"]').attr('formula').replace(match, str));
         }
         $('input[name="object__' + match + '__magnitude"]').blur(function() {
             refresh()
         });
         actualFormula = actualFormula.replace(match, "");
     }
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





