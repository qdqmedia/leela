from unittest import TestCase

from custom.filters import datetimeformat, localize_money


class LocalizeMoneyTest(TestCase):
    def test_localize_money_no_thousand_no_decimal(self):
        value = 250
        self.assertEqual('250', localize_money(value, 'es'))

    def test_localize_money_thousand_no_decimal(self):
        value = 2500400
        self.assertEqual('2.500.400', localize_money(value, 'es'))

    def test_localize_money_no_thousand_decimal(self):
        value = 250.34
        self.assertEqual('250,34', localize_money(value, 'es'))

    def test_localize_money_thousand_decimal(self):
        value = 2500400.34
        self.assertEqual('2.500.400,34', localize_money(value, 'es'))


class DateTimeFormat(TestCase):
    def test_format_good_timestamp(self):
        value = 1284286794
        self.assertEqual('12/09/2010 10:19', datetimeformat(value))

    def test_format_str_timestamp(self):
        value = '1284286794'
        self.assertEqual('12/09/2010 10:19', datetimeformat(value))
