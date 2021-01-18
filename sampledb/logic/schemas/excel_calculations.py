import re

class Excel:
    def SUMME(self, param: list):
        sum = 0
        for var in param:
            sum += float(var)

        return sum

    def DIFFERENZ(self, param: list):
        dif = float(param[0])
        for var in range(1, len(param)):
            dif -= float(param[var])

        return dif

    def PRODUKT(self, param: list):
        prod = 1
        for var in param:
            prod *= float(var)

        return prod

    def DIVISION(self, param: list):
        div = 1
        for var in param:
            div /= float(var)
        div *= float(param[0])

        return div

    def MITTELWERT(self, param: list):
        mit = self.SUMME(param) / len(param)

        return mit

    def RUNDEN(self, param: list):
        if len(param) > 1:
            accuracy = float(param[1])
        else:
            accuracy = 2
        int_frac = int(float(param[0]) * (10 ** accuracy) + 0.5)

        return int_frac / 10**accuracy

    def WENN(self, param: list):
        r = re.compile('(.+)([<|>|=|<=|>=])(.+)')
        comp1 = r.match(param[0])[1]
        comp2 = r.match(param[0])[3]
        compoperator = r.match(param[0])[2]

        if len(param) < 3:
            raise AttributeError
        elif compoperator == '<' and comp1 < comp2:
            return param[1]
        elif compoperator == '>' and comp1 < comp2:
            return param[1]
        elif compoperator == '=' and comp1 == comp2:
            return param[1]
        elif compoperator == '<=' and comp1 <= comp2:
            return param[1]
        elif compoperator == '>=' and comp1 >= comp2:
            return param[1]
        else:
            return param[2]

    def MIN(self, param: list):
           return min(param)

    def MAX(self, param: list):
        return max(param)







