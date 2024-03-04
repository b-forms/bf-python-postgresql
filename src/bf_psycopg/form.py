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


    def fields(self, accept):
        '''
        Only return normalised form fields that are acceptable from the request form.
        '''

        # Strip fields and remove fields that are not in the accept list.
        form = self.data
        form = {k: form[k].strip() for k in form.keys() & accept}

        return form
