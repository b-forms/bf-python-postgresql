import re
from dataclasses import dataclass


@dataclass
class FormData:
    '''
    Class for handling HTTP form data.

    Will only return fields that are acceptabled.

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
        Resolve a field name to a column name and its row.

        For form-records:

            'field_name' will resolve to:

                ('field_name', None)

        For form-tables:

            'field_name[123]' will resolve to:

                ('field_name', '123')
        '''
        m = re.match(r'(\w+)(\[(\w+)\])?', field_name)
        return (m.group(1), m.group(3))


    def fields(self, accept):
        '''
        Only return normalised form fields that are acceptable from the request form.
        '''

        # Strip fields and remove fields that are not in the accept list.
        form = self.data
        form = {k: form[k].strip() for k in form.keys() & accept}

        return form
