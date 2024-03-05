from psycopg import sql
from psycopg.rows import dict_row
from .error import ValidationFailure


class DuplicateDetection:
    def __init__(self, conn, table_info):
        self.conn = conn
        self.table_info = table_info


    def validate_field(self, conn, form, field_name, column_name, indexdef):
        primary_key = self.table_info.primary_key(self.conn)

        cur = self.conn.cursor()
        cur.row_factory = dict_row
        result = {}

        # Check if the unique key applies to this column.
        if column_name not in indexdef:
            return # Does not apply to this index.

        # Look for duplicates.
        args = []
        where = []
        for unique_column in indexdef:
            if unique_column not in form:
                return # Cannot search for duplicates if field is missing.
                # TODO is this the best way to handle this condition?

            where.append(sql.SQL('{} = %s').format(
                                  sql.Identifier(column_name)))
            args.append(form[unique_column])

        # Exclude existing record from duplicate search if the primary key
        # is in the form data. This will allow editing of a record to exclude
        # duplicate matches against itself.
        if (type(primary_key) is str):
            if primary_key in form:
                where.append(sql.SQL('{} != %s').format(
                                     sql.Identifier(primary_key)))
                args.append(form[primary_key])
        else:
            pass # TODO handle composite primary keys.

        # Search.
        query = '''
            select count(*)
            from {table_name}
            where {where}
        '''
        query = sql.SQL(query).format(
                table_name=sql.Identifier(self.table_info.table_name),
                where=sql.SQL(' and ').join(where))
        cur.execute(query, args)

        if (cur.fetchone()['count']):
            raise ValidationFailure('Duplicate constraint. Field must be unique.')
