import unittest
import psycopg
from psycopg.rows import dict_row
from .testconfig import dsn
from src.bf_psycopg.validator import Validator


class TestValidator(unittest.TestCase):
    def test_validator(self):
        with psycopg.connect(dsn, row_factory=dict_row) as conn:
            conn.execute('''
            drop table if exists accounts;
            create table accounts (
                account_id serial primary key,
                account_name varchar not null,
                max_users int not null default 0,
                constraint name_unique unique (account_name)
            );
            insert into accounts (account_name)
            values ('ACME Limited');
            ''')

            form = {
                'account_name': 'ACME Limited',
            }
            validator = Validator(conn, 'accounts')
            validator.validate_field(form, 'account_name')
            self.assertEqual(
                    'Duplicate constraint. Field must be unique.',
                    validator.validate_field(form, 'account_name'))


if __name__ == '__main__':
    unittest.main()
