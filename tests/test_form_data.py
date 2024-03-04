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

        # Test that only acceptable fields are returned.
        fields = form.fields({'project_id'})
        self.assertEqual({'project_id': '5'}, fields)


    def test_multidimensional(self):
        data = {
            'project_id[0]': '52',
            'account_id[0]': '30',
            'project_id[1]': '45',
            'account_id[1]': '20',
            'group_id': '500',
            'ignored_field': 'ignore_me',
        }
        form = FormData(data)
        fields = form.fields({'project_id', 'account_id', 'group_id'})
        self.assertEqual({
            'project_id': {
                0: '52',
                1: '45',
            },
            'account_id': {
                0: '30',
                1: '20',
            },
            'group_id': '500',
        }, fields)


if __name__ == '__main__':
    unittest.main()
