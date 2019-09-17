from __future__ import (nested_scopes, generators, division, absolute_import,
                        print_function, unicode_literals)
from six import string_types, integer_types
from six.moves import range
import sys
from numpy import float32, isnan


def print_scientific_8(value):
    """
    Prints a value in 8-character scientific notation.
    This is a sub-method and shouldnt typically be called

    .. seealso:: :func: `print_float_8` for a better method
    """
    if value == 0.0:
        return '%8s' % '0.'

    python_value = '%8.11e' % value
    svalue, sexponent = python_value.strip().split('e')
    exponent = int(sexponent)  # removes 0s

    sign = '-' if abs(value) < 1. else '+'

    # the exponent will be added later...
    exp2 = str(exponent).strip('-+')
    value2 = float(svalue)

    leftover = 5 - len(exp2)

    if value < 0:
        fmt = "%%1.%sf" % (leftover - 1)
    else:
        fmt = "%%1.%sf" % leftover

    svalue3 = fmt % value2
    svalue4 = svalue3.strip('0')
    field = "%8s" % (svalue4 + sign + exp2)
    return field


def print_float_8(value):
    """
    Prints a float in nastran 8-character width syntax using the
    highest precision possbile.
    """
    if isnan(value):
        return '        '
    elif value == 0.0:
        return '%8s' % '0.'
    elif value > 0.:  # positive, not perfect...
        if value < 5e-8:
            field = print_scientific_8(value)
            return field
        elif value < 0.001:
            field = print_scientific_8(value)
            field2 = "%8.7f" % value  # small value
            field2 = field2.strip('0 ')

            field1 = field.replace('-', 'e-')

            if field2 == '.':
                return print_scientific_8(value)
            if len(field2) <= 8 and float(field1) == float(field2):
                field = field2
                field = field.strip(' 0')
        elif value < 0.1:
            field = "%8.7f" % value
        elif value < 1.:
            field = "%8.7f" % value  # same as before...
        elif value < 10.:
            field = "%8.6f" % value
        elif value < 100.:
            field = "%8.5f" % value
        elif value < 1000.:
            field = "%8.4f" % value
        elif value < 10000.:
            field = "%8.3f" % value
        elif value < 100000.:
            field = "%8.2f" % value
        elif value < 1000000.:
            field = "%8.1f" % value
        else:  # big value
            field = "%8.1f" % value
            if field.index('.') < 8:
                field = '%8.1f' % round(value)
                field = field[0:8]
                # assert '.' != field[0], field
            else:
                field = print_scientific_8(value)
            return field
    else:
        if value > -5e-7:
            field = print_scientific_8(value)
            return field
        elif value > -0.01:  # -0.001
            field = print_scientific_8(value)
            field2 = "%8.6f" % value  # small value
            field2 = field2.strip('0 ')

            # get rid of the first minus sign, add it on afterwards
            field1 = '-' + field.strip(' 0-').replace('-', 'e-')

            if len(field2) <= 8 and float(field1) == float(field2):
                field = field2.rstrip(' 0')
                field = field.replace('-0.', '-.')

        elif value > -0.1:
            # -0.01 >x>-0.1...should be 5 (maybe scientific...)
            field = "%8.6f" % value
            field = field.replace('-0.', '-.')
        elif value > -1.:
            # -0.1  >x>-1.....should be 6, but the baseline 0 is kept...
            field = "%8.6f" % value
            field = field.replace('-0.', '-.')
        elif value > -10.:
            field = "%8.5f" % value  # -1    >x>-10
        elif value > -100.:
            field = "%8.4f" % value  # -10   >x>-100
        elif value > -1000.:
            field = "%8.3f" % value  # -100  >x>-1000
        elif value > -10000.:
            field = "%8.2f" % value  # -1000 >x>-10000
        elif value > -100000.:
            field = "%8.1f" % value  # -10000>x>-100000
        else:
            field = "%8.1f" % value
            try:
                ifield = field.index('.')
            except ValueError:
                raise ValueError('error printing float; cant find decimal; field=%r value=%s' % (field, value))
            if ifield < 8:
                field = '%7s.' % int(round(value, 0))
                # assert '.' != field[0], field
            else:
                field = print_scientific_8(value)
            return field
    field = field.strip(' 0')
    field = '%8s' % field

    # assert len(field) == 8, ('value=|%s| field=|%s| is not 8 characters '
    #                         'long, its %s' % (value, field, len(field)))
    return field


if __name__ == '__main__':
    value = ''
    value_1 = print_float_8(value)
    print(value_1)
