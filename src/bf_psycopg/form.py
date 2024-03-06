import re
from dataclasses import dataclass


@dataclass
class FormData:
    '''
    Class for handling HTTP form data.

    Will only return fields that are acceptable.

    Will convert field names ending in '[i]' into multidimensional dicts,
    where i is an integer.

    Will optionally normalise form data against a normaliser.
    '''
    data: list = None
    

    def __init__(self, data):
        self.data = data


    def __post_init__(self):
        if self.data is None:
            self.data = {}


    def row(self, field_name):
        '''
        Resolve a field name to a column name and its row index.

        For form-records:

            'field_name' will resolve to:

                ('field_name', None)

        For form-tables:

            'field_name[123]' will resolve to:

                ('field_name', 123)
        '''
        m = re.match(r'(\w+)(\[(\d+)\])?', field_name)
        i = m.group(3)
        if i is not None:
            i = int(i)
        return m.group(1), i


    def fields(self, accept):
        '''
        Only return normalised form fields that are acceptable from the request form.
        '''

        # Strip fields and remove fields that are not in the accept list.
        form = self.data
        form = {k: form[k].strip() for k in form.keys() & accept}

        return form


    def rows(self, accept):
        rows = {}
        fields = {}

        # Get rows.
        for field_name in self.data:
            column_name, i = self.row(field_name)
            if column_name not in accept:
                continue

            field = self.data[field_name].strip()

            if i is not None:
                if i not in rows:
                    rows[i] = {}
                rows[i][column_name] = field
            else:
                fields[column_name] = field
        
        # Flatten.
        for column_name in fields:
            for i in rows:
                rows[i][column_name] = fields[column_name]

        return rows
