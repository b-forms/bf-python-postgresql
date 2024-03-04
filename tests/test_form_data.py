import unittest
from src.bf_psycopg import FormData


class TestFormData(unittest.TestCase):
    def test_fields(self):
        data = {
            'project_id': '5',
            'account_id': '30',
            'project_code': 'ABC1001',
        }
        form = FormData(data)
        fields = form.fields({'project_id', 'account_id', 'project_code'})
        self.assertEqual(data, fields)

        fields = form.fields({'project_id'})
        self.assertEqual({'project_id': '5'}, fields)


if __name__ == '__main__':
    unittest.main()
