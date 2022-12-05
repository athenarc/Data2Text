from typing import Dict, List

from databases import Database

from app.backend.db.DbInterface import DbException, DbInterface


class MySqlController(DbInterface):

    async def query_with_res_cols(self, conn_url: str, query: str):
        database = Database(conn_url)
        await database.connect()

        one_row = await database.fetch_one(query=query)
        res = await database.fetch_all(query=query)
        res_with_cols = dict(one_row._mapping)

        desc = [col_name for col_name in res_with_cols.keys()]

        await database.disconnect()
        return res, desc

    @staticmethod
    def find_db_name(conn_url: str):
        return conn_url.split('/')[-1]

    async def get_table_names(self, conn_url: str) -> List[str]:
        table_query = f"""
        SELECT table_name
        FROM INFORMATION_SCHEMA.TABLES
        WHERE table_schema = \'{self.find_db_name(conn_url)}\';
        """

        table_names, _ = await self.query_with_res_cols(conn_url, table_query)

        return [table[0] for table in table_names]

    async def get_table_cols(self, conn_url: str, table_name: str) -> List[str]:
        table_cols_query = f"""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = \'{self.find_db_name(conn_url)}\' AND TABLE_NAME = \'{table_name}\';
        """
        table_cols, _ = await self.query_with_res_cols(conn_url, table_cols_query)

        return [table_col[0] for table_col in table_cols]

    async def get_pks_of_table(self, conn_url: str, table_name: str) -> List[str]:
        pks_of_table_query = f"""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{self.find_db_name(conn_url)}'
          AND TABLE_NAME = '{table_name}'
          AND COLUMN_KEY = 'PRI';
        """
        pks, _ = await self.query_with_res_cols(conn_url, pks_of_table_query)

        return [pk[0] for pk in pks]

    async def preview_table(self, conn_url: str, table: str, limit: int = 10):
        res, desc = await self.query_with_res_cols(conn_url, f"SELECT * FROM {table} LIMIT {limit}")
        return {"table": table, "header": desc, "row": res}
