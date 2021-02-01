import unittest
from datetime import datetime
from handy_functions import turn_first_datetime_string_into_time_format

class TEST_HANDY(unittest.TestCase):

    def test_turn_first_datetime_string_into_time_format(self):
        dt1 = '2021-02-01:2,3,4,5;'
        self.assertEqual(
            turn_first_datetime_string_into_time_format(dt1),
            datetime(2021, 2, 1, 1, 0))

        dt2 = '2021-02-03:0;'
        self.assertEqual(
            turn_first_datetime_string_into_time_format(dt2),
            datetime(2021, 2, 3, 0, 0))

        dt3 = '2021-02-01:47'
        self.assertEqual(
            turn_first_datetime_string_into_time_format(dt3),
            datetime(2021, 2, 1, 23, 30))

        dt4 = '2021-02-01:45,46;'
        self.assertEqual(
            turn_first_datetime_string_into_time_format(dt4),
            datetime(2021, 2, 1, 22, 30))


if __name__ == '__main__':
    unittest.main()

