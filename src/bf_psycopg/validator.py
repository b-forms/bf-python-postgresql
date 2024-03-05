import re
from . import TableInfo
from . import FormData
from .duplicate_detection import DuplicateDetection
from .error import ValidationFailure

class Validator:
    def __init__(self, conn, table_name):
        self.conn = conn
        self.table_name = table_name
        self.table_info = TableInfo(table_name)
        self.duplicate_detection = DuplicateDetection(conn, self.table_info)


    def validate_field(self, form, field_name):
        data = FormData(form)
        (column_name, row) = data.row(field_name)

        try:
            self.detect_duplicates(form, field_name, column_name, row)
        except ValidationFailure as failure:
            return str(failure)


    def detect_duplicates(self, form, field_name, column_name, row):
        for indexdef in self.table_info.unique_indices(self.conn):
            self.duplicate_detection.validate_field(self.conn, form, field_name, column_name, indexdef)
