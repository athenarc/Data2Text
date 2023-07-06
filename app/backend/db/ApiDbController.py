from typing import List
import httpx

from app.backend.db.DbInterface import DbInterface


class ApiDbController(DbInterface):
    def __init__(self):
        self.database_name = 'cordis'

    async def query_with_res_cols(self, conn_url: str, query: str):
        data = {
                  "query": query,
                  "database": self.database_name
                }
        r = httpx.post(f'{conn_url}/sql/', data=data).json()

        return r['data'], r['columns']

    @staticmethod
    def find_db_name(conn_url: str):
        return conn_url.split('/')[-1]

    async def get_table_names(self, conn_url: str) -> List[str]:
        r = httpx.get(f'{conn_url}/schema/{self.database_name}/').json()

        return r['tables']

    async def get_table_cols(self, conn_url: str, table_name: str) -> List[str]:
        r = httpx.get(f'{conn_url}/schema/{self.database_name}/').json()
        column_ids = r['table'][table_name]

        return [r['tables'][column_id].split('.')[-1] for column_id in column_ids]

    async def get_pks_of_table(self, conn_url: str, table_name: str) -> List[str]:
        return []

    async def preview_table(self, conn_url: str, table: str, limit: int = 10):
        res, desc = await self.query_with_res_cols(conn_url, f"SELECT * FROM {table} LIMIT {limit}")
        return {"table": table, "header": desc, "row": res}
