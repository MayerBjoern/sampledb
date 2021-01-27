# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 15:32:24 2020
@author: b.mayer
This validation preprocessor extends submitted update data silently if possible.
So that partial updates or redundant field  definitions like pint's dimensionality do not have to be submitted everytime.
"""

import flask

from ...logic import objects, datatypes, errors, units
from .utils import units_are_valid, get_dimensionality_for_units
from .quantity_calculations import calculate


def _validation_preprocessor_quantity(instance: dict, schema: dict) -> None:
    """
    Extends the json to update a quantity object by the unit from the schema,
    the dimensionality and either the magnitude or the magnitute_in_base_units parameter

    :param instance: the sample object
    :param schema: the valid sampledb object schema
    """

    if not isinstance(instance, dict):
        return instance
    if '_type' not in instance:
        return instance  # maybe set to schema type?
    if 'units' not in instance:
        instance['units'] = schema['units']

    magnitude_datatype = None
    magnitude_base_datatype = None
    if 'magnitude' in instance:
        magnitude_datatype = datatypes.Quantity(instance['magnitude'], units=instance['units'],
                                                already_in_base_units=False)
    if 'magnitude_in_base_units' in instance:
        magnitude_base_datatype = datatypes.Quantity(instance['magnitude_in_base_units'], units=instance['units'],
                                                     already_in_base_units=True)

    if magnitude_datatype is not None and magnitude_base_datatype is not None \
            and magnitude_datatype.magnitude != magnitude_base_datatype.magnitude:
        raise errors.ValidationError(
            'magnitude and magnitude_in_base_units do not match, either set only one or make sure both match', None)
    elif magnitude_datatype is None:
        magnitude_datatype = magnitude_base_datatype

    instance.update(magnitude_datatype.to_json())


def _validation_preprocessor_calculatedquantity(instance: dict, schema: dict, object_data: dict) -> None:
    if object_data is None:
        return None

    formula = schema['formula']
    magnitude = calculate(formula, object_data)

    c_quantity = datatypes.CalculatedQuantity(magnitude, formula, schema['units'])

    instance.update(c_quantity.to_json())
