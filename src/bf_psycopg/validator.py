import re
#import validators
from psycopg.rows import dict_row
from psycopg import sql
from . import TableInfo
from . import FormData

# from app.tables import Schema     TODO remove
# import psyqlepg                   TODO remove


class Where:
    # TODO Remove or replace this?
    def __init__(self, name=None, value=None):
        self.params = []
        self.args = []
        if (name):
            self.append(name, value)


    def append(self, name, value=None):

        if isinstance(name, sql.Composable):
            self.params.append(name)
        else:
            self.params.append(sql.SQL('{} = %s').format(sql.Identifier(name)))
            self.args.append(value)
        return self


    def clause(self):
        if not self.params:
            return sql.SQL('true').format()

        return sql.SQL('{params}').format(
            params=sql.SQL(f' {self.op()} ').join(self.params))


    def as_string(self, context):
        return self.clause().as_string(context)


    def op(self):
        return 'and'


class WhereOr:
    def op(self):
        return 'or'


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
            where = Where()
            for column_name in indexdef:
                field = form[column_name]
                if field is None:
                    return # Cannot search for duplicates if field is missing.
                where.append(column_name, field)

            # Exclude existing record from duplicate search if the primary key
            # is in the form data. This will allow editing of a record to exclude
            # duplicate matches against itself.
            if (type(primary_key) is str):
                if primary_key in form:
                    pk_field = form[primary_key]
                    # TODO need where clause to exclude (!=)

            # Search.
            query = '''
                select count(*)
                from {table_name}
                where {where}
            '''
            query = sql.SQL(query).format(
                    table_name=sql.Identifier(self.table_name),
                    where=where.clause())
            cur.execute(query, where.args)
            if (cur.fetchone()['count']):
                return 'Duplicate constraint. Field must be unique.'
