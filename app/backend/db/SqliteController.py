import sqlite3
from typing import List

from databases import Database

from app.backend.db.DbInterface import DbException, DbInterface


class SqliteController(DbInterface):

    async def query_with_res_cols(self, conn_url, query):
        database = Database(conn_url)
        await database.connect()

        one_row = await database.fetch_one(query=query)
        res = await database.fetch_all(query=query)
        res_with_cols = dict(one_row._mapping)

        desc = [col_name for col_name in res_with_cols.keys()]

        await database.disconnect()

        return res, desc

    async def get_table_names(self, conn_url) -> List[str]:
        candidate_tables, _ = await self.query_with_res_cols(conn_url,
                                                             "SELECT name FROM sqlite_master WHERE type='table';")
        # Many tables do not have a meaningful name but instead an id eg. table_12_42
        # We cannot use our model on them since the table name is important information
        return [table[0] for table in candidate_tables if "table_" not in table[0] and table[0] != 'sqlite_master']

    async def get_table_cols(self, conn_url, table_name: str) -> List[str]:
        table_info, _ = self.query_with_res_cols(conn_url, f'PRAGMA table_info({table_name});')
        table_cols = [table_col[1] for table_col in table_info]

        return table_cols

    async def get_pks_of_table(self, conn_url, table_name: str) -> List[str]:
        pks_of_table_query = f"""
                SELECT l.name
                FROM pragma_table_info('books') AS l
                WHERE l.pk = 1;
                """
        table_pks = await self.query_with_res_cols(conn_url, pks_of_table_query)
        return list(table_pks[0][0])

    async def preview_table(self, conn_url, table: str, limit: int = 10):
        rows, cols = await self.query_with_res_cols(conn_url, f"SELECT * FROM {table} LIMIT {limit}")
        return {"table": table, "header": cols, "row": rows}
