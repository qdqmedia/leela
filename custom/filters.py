import datetime


def datetimeformat(value, format='%d/%m/%Y %H:%M'):
    """Formats a datetime given the format string"""
    dt = datetime.datetime.fromtimestamp(int(value))
    return dt.strftime(format)

def localize_money(value, language='es'):
    """Localizes a money quantity"""
    decimal_chars = {
        'es': ','
    }
    thousand_chars = {
        'es': '.'
    }

    dchar = decimal_chars.get(language, 'es')
    tchar = thousand_chars.get(language, 'es')
    value = str(value)
    value_list = value.split('.')
    if len(value_list) > 1:
        integer_part, decimal_part = value_list
    else:
        integer_part, decimal_part = value, None

    new_integer_part = ''; index=0;
    for cipher in integer_part[::-1]:
        if index == 3:
            new_integer_part = tchar + new_integer_part
            index = 0
        new_integer_part = cipher + new_integer_part
        index += 1

    if decimal_part:
        return new_integer_part + dchar + decimal_part
    else:
        return new_integer_part
