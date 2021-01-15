class Excel:
    def SUMME(self, param: list):
        sum = 0
        for var in param:
            sum += float(var)

        return sum
