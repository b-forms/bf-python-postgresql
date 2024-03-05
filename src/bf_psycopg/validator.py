import re
from psycopg.rows import dict_row
from psycopg import sql
from . import TableInfo
from . import FormData

class Validator:
    def __init__(self, conn, table_name):
        self.table_name = table_name
        self.table_info = TableInfo(table_name)
        self.conn = conn


    def validate_field(self, form, field_name):
        data = FormData(form)
        (column_name, row) = data.row(field_name)

        result = self.detect_duplicates(form, field_name, column_name, row)
        if result:
            return result


    def detect_duplicates(self, form, field_name, column_name, row):
        primary_key = self.table_info.primary_key(self.conn)

        cur = self.conn.cursor()
        cur.row_factory = dict_row
        result = {}

        # For each unique key.
        for indexdef in self.table_info.unique_indices(self.conn):

            # Check if the unique key applies to this column.
            if column_name not in indexdef:
                continue # Does not apply to this index.

            # Look for duplicates.
            where = []
            for unique_column in indexdef:
                if unique_column not in form:
                    return # Cannot search for duplicates if field is missing.
                    # TODO is this the best way to handle this condition?

                where.append(sql.SQL('{column_name} = {field}').format(
                                      column_name=sql.Identifier(column_name),
                                      field=form[unique_column]))

            # Exclude existing record from duplicate search if the primary key
            # is in the form data. This will allow editing of a record to exclude
            # duplicate matches against itself.
            if (type(primary_key) is str):
                if primary_key in form:
                    where.append(sql.SQL('{primary_key} != {field}').format(
                                         primary_key=sql.Identifier(primary_key),
                                         field=form[primary_key]))
            else:
                pass # TODO handle composite primary keys.

            # Search.
            query = '''
                select count(*)
                from {table_name}
                where {where}
            '''
            query = sql.SQL(query).format(
                    table_name=sql.Identifier(self.table_name),
                    where=sql.SQL(' and ').join(where))
            cur.execute(query)

            if (cur.fetchone()['count']):
                return 'Duplicate constraint. Field must be unique.'
