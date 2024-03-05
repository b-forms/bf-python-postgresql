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


if __name__ == '__main__':
    unittest.main()
