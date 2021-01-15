from ...logic import datatypes, units
from . import excel_calculations

from sympy import sympify
import pint
import re

data = None


def calculate(formula: str, object_data: dict):
    #Ersetze Leerzeichen
    formula = formula.replace(" ", "")
    #Ersetze Komma
    formula = formula.replace(",", ".")

    global data
    data = object_data

    return brackets(formula)


def brackets(formula: str):
    excel = excel_calculations.Excel()
    method_list = [attribute for attribute in dir(excel_calculations.Excel) if callable(getattr(excel_calculations.Excel, attribute)) and attribute.startswith('__') is False]
    excel_pattern = r'^(.*)('+'|'.join(method_list)+r')$'

    pattern = r'^(.*)\((.*?)\)(.*)$'
    match = re.search(pattern, formula)

    while match is not None:
        before = match[1]
        inside = replace_variables(match[2])
        after = match[3]

        excel_match = re.search(excel_pattern, before)
        if excel_match is not None:
            before = excel_match[1]
            try:
                inside = getattr(excel, excel_match[2])(inside.split(';'))
            except:
                return 0
        else:
            inside = sympify(inside, evaluate=True)

        formula = before + str(inside) + after
        match = re.search(pattern, formula)

    return formula


def replace_variables(inp: str) -> str:
    return re.sub(r'([a-z]+[a-zA-Z0-9]*)', get_magnitude_for_varname, inp)


def get_magnitude_for_varname(matchobj: re.Match):
    varname = matchobj.group(1)
    field_data = data.get(varname)
    if field_data is None:
        return "0"

    if field_data.get('magnitude') is None:
        if field_data.get('magnitude_in_base_units') is None:
            return "0"
        else:
            if field_data.get('units') is None:
                return str(field_data.get('magnitude_in_base_units'))

            try:
                pint_units = units.ureg.Unit(field_data.get('units'))
            except (pint.errors.UndefinedUnitError, AttributeError):
                return "0"

            pint_base_units = units.ureg.Quantity(1, pint_units).to_base_units().units
            return str(units.ureg.Quantity(field_data.get('magnitude_in_base_units'), pint_base_units).to(pint_units).magnitude)
    else:
        return str(field_data.get('magnitude'))

