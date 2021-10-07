import sqlite3
from typing import List


class SqliteController:
    def __init__(self, db_path):
        self.db_path = db_path

    def connect_and_query_with_desc(self, query):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        cur.execute(query)
        res = cur.fetchall()
        desc = [d[0] for d in cur.description]
        con.close()

        return res, desc

    def get_table_names(self) -> List[str]:
        candidate_tables, _ = self.connect_and_query_with_desc("SELECT name FROM sqlite_master WHERE type='table';")
        # Many tables do not have a meaningful name but instead an id eg. table_12_42
        # We cannot use our model on them since the table name is important information
        return [table[0] for table in candidate_tables if "table_" not in table[0] and table[0] != 'sqlite_master']

    def get_table_cols(self, table_name: str) -> List[str]:
        table_info, _ = self.connect_and_query_with_desc(f'PRAGMA table_info({table_name});')
        table_cols = [table_col[1] for table_col in table_info]

        return table_cols

    def preview_table(self, table):
        rows, cols = self.connect_and_query_with_desc(f"SELECT * FROM {table} LIMIT 10")
        return {"table": table, "header": cols, "row": rows}


if __name__ == '__main__':
    sqlite_con = SqliteController("../../../storage/datasets/wiki_sql/raw/train.db")
    # table_cols_debug = sqlite_con.get_table_cols('Titanic')
    print(sqlite_con.get_table_names())
