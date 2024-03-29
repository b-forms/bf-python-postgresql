from psycopg.rows import namedtuple_row


class TableInfo:
    '''
    Information schema for a table.
    '''

    def __init__(self, table_name):
        self.table_name = table_name


    def primary_key(self, conn):
        '''
        Retreive the primary key. This is either a string, or a tuple
        if the primary key is a composite key.
        '''

        cur = conn.cursor()
        cur.row_factory = namedtuple_row

        # https://wiki.postgresql.org/wiki/Retrieve_primary_key_columns
        query = '''
            select json_agg(a.attname) as attname
            from pg_index i
            join pg_attribute a on (a.attrelid = i.indrelid and a.attnum = any(i.indkey))
            where i.indrelid = %s::regclass
                and i.indisprimary
            group by i.indexrelid;
        '''
        cur.execute(query, [self.table_name])

        # TODO composite primary keys.
        att = cur.fetchone()
        if not att.attname:
            return None
        if len(att.attname) == 1:
            return att.attname[0]
        return tuple(att.attname)


    def unique_indices(self, conn):
        '''
        Return unique keys.
        '''

        cur = conn.cursor()
        cur.row_factory = namedtuple_row

        # The indexdef is an array of column names on the unique index.
        # The relname is the name of the unique index.
        #
        # https://www.postgresql.org/docs/current/functions-info.html
        query = '''
            select json_agg(pg_catalog.pg_get_indexdef(a.attrelid, a.attnum, true)) indexdef
            from pg_catalog.pg_attribute a
            join pg_class idx on idx.oid = a.attrelid
            join pg_index pgi on pgi.indexrelid = idx.oid
            join pg_namespace insp on insp.oid = idx.relnamespace
            join pg_class tbl on tbl.oid = pgi.indrelid
            join pg_namespace tnsp on tnsp.oid = tbl.relnamespace
            where a.attnum > 0
                and not a.attisdropped
                and tnsp.nspname = 'public'
                and pgi.indisunique
                and tbl.relname = %s
            group by idx.relname
        '''
        cur.execute(query, [self.table_name])

        indices = []
        while (att := cur.fetchone()):
            indices.append(tuple(att.indexdef))

        return indices
