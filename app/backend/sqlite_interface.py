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

    def get_table_cols(self, table_name: str) -> List[str]:
        table_info, _ = self.connect_and_query_with_desc(f'PRAGMA table_info({table_name});')
        table_cols = [table_col[1] for table_col in table_info]

        return table_cols


if __name__ == '__main__':
    sqlite_con = SqliteController("../../storage/datasets/wiki_sql/raw/train.db")
    table_cols = sqlite_con.get_table_cols('titanic')
    print(table_cols)
