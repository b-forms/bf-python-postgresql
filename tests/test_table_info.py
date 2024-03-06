import unittest
import psycopg
from psycopg.rows import dict_row
from .testconfig import dsn
from src.bf_psycopg.table import TableInfo


class TestTableInfo(unittest.TestCase):
    def test_unique_indices(self):
        with psycopg.connect(dsn, row_factory=dict_row) as conn:
            conn.execute('''
            drop table if exists unique_test;
            create table unique_test (
                id serial primary key,
                composite_a int not null,
                composite_b int not null,
                constraint composite_a_b_unique unique (composite_a, composite_b)
            );
            ''')
            info = TableInfo('unique_test')
            unique_indices = info.unique_indices(conn)

            self.assertEqual([
                ('composite_a', 'composite_b'),
                ('id', ),
            ], unique_indices)
            self.assertEqual('id', info.primary_key(conn))


    def test_composite_primary_key(self):
        with psycopg.connect(dsn, row_factory=dict_row) as conn:
            conn.execute('''
            drop table if exists composite_pk_test;
            create table composite_pk_test (
                composite_a int not null,
                composite_b int not null,
                number int not null,
                constraint composite_a_b_pkey primary key (composite_a, composite_b)
            );
            ''')
            info = TableInfo('composite_pk_test')
            unique_indices = info.unique_indices(conn)

            self.assertEqual([
                ('composite_a', 'composite_b'),
            ], unique_indices)
            self.assertEqual(('composite_a', 'composite_b'), info.primary_key(conn))


if __name__ == '__main__':
    unittest.main()
