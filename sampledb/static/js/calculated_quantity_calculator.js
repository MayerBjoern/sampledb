var func = [
    "PRODUKT", "SUMME", "DIFFERENZ", "DIVISION", "MITTELWERT", "RUNDEN", "WENN", "MIN", "MAX", "POTX"
]

var funcStr = "";

function replaceVariables(inp) {
    var variables = new RegExp("([a-z]+[a-zA-Z0-9]*)")
         while(variables.test(inp)) {
             var match = inp.match(variables)[1];
             var val = getValue(String("object__" + match + "__magnitude"));
             if (isNaN(val)) {
                 throw new Error("NEV");
             } else {
                 inp = String(inp).replace(match, val);
             }
         }
    return inp;
}

function BRACKETS(inp) {

    // RegExp zu dem Finden von Exponentialtermen
    var l = /([0-9\.]+[\e\-]+[0-9]+)/;
    // Matcht diesen Term
    var match = inp.match(l);

    // So lange Exponentialterme gefunden werden
    while(match != null) {

        // Ersetze Exponentialterm durch numerische Zeichen
        inp = inp.replace(match[0], Number(match[0]));
        // Match neu
        match = inp.match(l);

    }

    // Ersetzt alle Leerzeichen
    inp = inp.replace(" ", "");

    // RegExp zu der weiteren Verarbeitung
    var r = /(.*)(\(.*?\))(.*)/;

    // bestehender input zum Vergleichen
    var inpO = null;

    // Term der ueberprueft werden soll match enthaelt
    var match = null;

    while(match = inp.match(r) != null) {

        // Liest neuen Match ein
        match = inp.match(r);

        // Wenn der Input sich nicht geaendert hat
        if(inpO == inp && inp != "\(\)") {

            throw new Error("ERROR ES");
            break;

        }
        else {

            // Belegt alten inp mit derzeit akuellem
            inpO = inp;

            // Term vor Term mit Klammern
            var strBefore = match[1];

            // Term in Klammern
            var strIn = match[2];

            // Match der hinter innerstem Klammerterm steht
            var strAfter = match[3];

            // innerster Klammerterm ohne Variablen und grundlegende Rechenoperationen
            var strInAufgeloest = FIGURE(replaceVariables(strIn));

            if(funcStr.test(strBefore)) {

                // String in dem der Methodenaufruf mit vorher folgenden Termen steht
                var strBefMatch =  strBefore.match(funcStr);

                // Methoden werden ausgefuehrt
                runMethodString = runMethods(String(strBefMatch[2] + strInAufgeloest.replace("," , "")));

                // Erzeugt neuen inp
                inp = strBefMatch[1] + runMethodString + strAfter;

            }
            else {

                // Erzeugt neuen inp
                inp = strBefore + strInAufgeloest + strAfter;

            }

            // Ersetzt Klammern in denen nur Zahlenwerte stehen
            inp = lessBrackets(inp);

        }

    }

    return inp;

}

function lessBrackets(inp) {

    // RegExp die Klammern findet in denen nur noch Zahlen stehen
    var r = /(^|\W)(\([0-9\.\-e\;]+\))/;

    if(r.test(inp)) {

        // Sucht Klammern in denen nur noch Zahlen stehen
        var match = inp.match(r)[2];

        // Ersetzt in match die Klammern
        var matchAufgeloest = match.replace("\(", "");
        matchAufgeloest = matchAufgeloest.replace("\)", "");

        // Ersetzt in inp die Klammern
        inp = inp.replace(match, matchAufgeloest);

        }

    return(inp);

}

function FIGURE(inp) {

    // Sucht nach 'Punkt' Operationen
    var s = /([0-9\.\-]+)([\*\/])([0-9\.\-]+)/;

    while (s.test(inp)) {

        var match = inp.match(s)[0];
        var z1 = Number(inp.match(s)[1]);
        var z2 = Number(inp.match(s)[3]);
        var operator = inp.match(s)[2];

        // Errechnet Einzelterme
        if(z1 == null || z2 == null) {
          return 0;
        }
        if (operator == "\/") {
            inp = inp.replace(match, z1 / z2);
        }
        else if (operator == "\*") {
            inp = inp.replace(match, z1 * z2);
        }

    }

    // Sucht nach 'Strich' Operationen
    var r = /([0-9\.\-]+)([\+|\-])([0-9\.\-]+)/

    while (r.test(inp)) {

        var match = inp.match(r)[0];
        var s1 = Number(inp.match(r)[1]);
        var s2 = Number(inp.match(r)[3]);
        var soperand = inp.match(r)[2];

        // Errechnet Einzelterme
        if (soperand == "-") {
            inp = inp.replace(match, s1 - s2);
        }
        else if (soperand == "+") {
            inp = inp.replace(match, s1 + s2);
        }

    }

    return (inp);

}

function getValue(inp) {

    // Sucht das uebergebene Variablenfeld in HTML Dokument
    var ret = $('input[name="' + inp + '"]').html();

    // Wenn vorhanden gibt es zurueck
    if (String(ret).length <= 0) {
        ret = $('input[name="' + inp + '"]').val();
    }

    // Wird als Number zurueckgegeben
    return (Number(ret));
}

function PRODUKT(inp) {

    // Aufbau Eingabe: PRODUKT(faktor1; faktor2; faktor3; .... )

    var a = String(inp).split('\;');
    var prod = 1;
    for (i = 0; i < a.length; i++) {
        prod *= a[i];
    }
    return (prod);
}

function DIVISION(inp) {

    // Aufbau Eingabe: DIVISION(Divident; Divisor1; Divisor2; .... )

    var a = String(inp).split('\;');
    var d1, d2;
    d1 = Number(a[0]);
    d2 = Number(a[1]);
    if (d2 > 1E-10 && d2 < -1E-10) {
        return (0);
    }
    return (Number(d1) / Number(d2));
}

function DIFFERENZ(inp) {

    // Aufbau Eingabe: DIFFERENZ(Subtrahend; Minuend1; Minuend2; .... )

    var a = String(inp).split('\;');
    var dif = a[0];
    for (var i = 1; i < a.length; i++) {
        dif -= a[i];
    }
    return (dif);
}

function SUMME(inp) {

    // Aufbau Eingabe: SUMME(Summand1; Summand2; Summand3; .... )

    var a = String(inp).split('\;');
    var sum = 0;
    for (var i = 0; i < a.length; i++) {
        sum += Number(a[i]);
    }
    return (sum);
}

function MITTELWERT(inp) {

    // Aufbau Eingabe: MITTELWERT(Wert1; Wert2; .... )

    var a = String(inp).split('\;');
    var sum = SUMME(inp);
    var mittel = Number(sum / (a.length));
    return mittel;
}

function RUNDEN(inp) {

    // Aufbau Eingabe: RUNDEN(Wert; Nachkommastellen)
    var a = inp.split(";");

    if(a.length > 1) {
        inp = parseInt(Number(a[0]) * Math.pow(10, Number(a[1])) + 0.5) / Math.pow(10, Number(a[1]));
    }
    else {
        inp = parseInt((Number(a[0]) * 100) + 0.5) / 100;
    }
    return inp;

}

function WENN(inp) {

    // Aufbau Eingabe: "WENN(var1 '<' var2; wennWahr; wennFalsch)"

    // Teile Term in Stuecke
    var a = String(inp).split("\;");

    // Term muss aus 3 Teilen bestehen
    if(a.length != 3) {
        throw new Error("ERROR WI");
    }

    // Untersuche die einzelnen Teile
    var r = /([0-9\.\-]+)(\<|\>|\=|\<\=|\>\=)([0-9\.\-]+)/;

    var vergleich = String(a[0]).match(r)[2];
    var z1 = Number(String(a[0]).match(r)[1]);
    var z2 = Number(String(a[0]).match(r)[3]);

    switch(String(vergleich)) {
        case "\<":
            if(z1 < z2) {
                return a[1];
            }
            else {
                return(a[2]);
            }
            break;
        case "\>":
            if(z1 > z2) {
                return a[1];
            }
            else {
               return(a[2]);
            }
            break;
        case "\=":
            if(z1 == z2) {
                return a[1];
            }
            else {
                return a[2];
            }
        case "\<\=":
            if(z1 <= z2) {
                return a[1];
            }
            else {
                return a[2];
            }
        case "\>\=":
            if(z1 >= z2) {
                return a[1];
            }
            else {
                return a[2];
            }
        default: return 0;
    }

}

function MIN(inp) {

    // Aufbau Eingabe: MIN(Wert1; Wert2; Wert3; .... )

    a = String(inp).split("\;");

    var min = Number.MAX_VALUE;
    for(var i = 0; i < a.length; i++) {

        if(Number(a[i]) < min) {
            min = Number(a[i]);
        }

    }

    return(min);

}

function MAX(inp) {


    // Aufbau Eingabe: MAX(Wert1; Wert2; Wert3; .... )

    a = String(inp).split("\;");

    var max = Number.MIN_VALUE;
    for(var i = 0; i < a.length; i++) {

        if(Number(a[i]) > max) {
            max = Number(a[i]);
        }

    }

    return(max);

}

function POTX(inp) {

    var counter = 0;
    inp = Number(inp);
    if(inp >= 1) {
        while(inp >= 10) {
            inp /= 10;
            counter++;
        }
        inp = inp + "e" + counter;
    }
    else {
        while(inp < 1) {
            inp *= 10;
            counter++;
        }
        inp = String(inp + "e-" + counter);
    }

    return String(inp);

}



function runMethods(inp) {

    inp = String(inp);
    var s = /(\w+)\(([0-9\;\-\.\<\>\=]+?)\)/;

    var match = inp.match(s)[0];
    // Funktionsname
    var functionA = inp.match(s)[1];
    // Parameteruebergabe
    var functionP = inp.match(s)[2];

    //"PRODUKT", "SUMME", "DIFFERENZ", "DIVISION", "MITTELWERT", "RUNDEN", WENN", "MIN", "MAX", "POTX"
    switch (functionA) {
        case "PRODUKT": inp = PRODUKT(String(functionP)); break;
        case "SUMME": inp = SUMME(String(functionP)); break;
        case "DIFFERENZ": inp = DIFFERENZ(String(functionP)); break;
        case "DIVISION": inp = DIVISION(String(functionP)); break;
        case "MITTELWERT": inp = MITTELWERT(String(functionP)); break;
        case "RUNDEN": inp = RUNDEN(String(functionP)); break;
        case "WENN": inp = WENN(String(functionP)); break;
        case "MIN": inp = MIN(String(functionP)); break;
        case "MAX": inp = MAX(String(functionP)); break;
        case "POTX": inp = POTX(String(functionP)); return inp; break;
        default: break;
    }

    return Number(inp);

}

function CALCULATOR(inp) {

    // Ersetze Leerzeichen
    inp = String(inp).replace(" ", "");

    // Ersetze Komma
    inp = inp.replace("\,", "\.");

    // Variable, um RegExp auf zu erstellen
    var str = "\(.*\)\(";

    if(inp == "") {
        return " ";
    }

    for(var i = 0; i < func.length; i++) {

        if(i != 0) {

            str += "\|";

        }

        str += String(func[i]);

    }

    // Erstelle neue RegExp
    funcStr = new RegExp(String(str + "\)\$"));

    // Versuche Berechnung durchzufuehren gib Fehler bei Fehler aus
     try {

        inp = BRACKETS("\(" + inp + "\)");
        return inp;

      } catch (err) {

         return (err);

      }

}