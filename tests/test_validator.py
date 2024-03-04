import unittest
import psycopg
from psycopg.rows import dict_row
from .testconfig import dsn


class TestValidator(unittest.TestCase):
    def test_validator(self):
        with psycopg.connect(dsn, row_factory=dict_row) as conn:
            pass


if __name__ == '__main__':
    unittest.main()
