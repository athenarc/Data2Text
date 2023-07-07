from typing import Dict, List

from databases import Database

from app.backend.db.DbInterface import DbException, DbInterface


class PostgresController(DbInterface):

    async def query_with_res_cols(self, conn_url: str, query: str):
        database = Database(conn_url)
        await database.connect()

        res_with_cols = await database.fetch_one(query=query)

        if res_with_cols is None:
            await database.disconnect()
            return None, None

        res = await database.fetch_all(query=query)

        res_list = [tuple(cell for cell in row[0:]) for row in res]
        cols = dict(res_with_cols._mapping)

        await database.disconnect()
        print(res_list, list(cols.keys()))
        return res_list, list(cols.keys())

    @staticmethod
    def find_db_name(conn_url: str):
        return conn_url.split('/')[-1]

    async def get_table_names(self, conn_url: str) -> List[str]:
        table_query = f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema != 'information_schema' AND table_name NOT LIKE 'pg%'
        """

        table_names, _ = await self.query_with_res_cols(conn_url, table_query)

        return [table[0] for table in table_names]

    async def get_table_cols(self, conn_url: str, table_name: str) -> List[str]:
        table_cols_query = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        """
        table_cols, _ = await self.query_with_res_cols(conn_url, table_cols_query)

        return [table_col[0] for table_col in table_cols]

    async def get_pks_of_table(self, conn_url: str, table_name: str) -> List[str]:
        return []

    async def preview_table(self, conn_url: str, table: str, limit: int = 10):
        res, desc = await self.query_with_res_cols(conn_url, f"SELECT * FROM {table} LIMIT {limit}")
        return {"table": table, "header": desc, "row": res}
