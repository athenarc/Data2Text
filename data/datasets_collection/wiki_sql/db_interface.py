import json
import re
import sqlite3

import pandas as pd


class WikiSqlController:
    def __init__(self, db_path, tables_path):
        self.db_path = db_path

        self.table_info = []
        with open(tables_path) as file_in:
            for line in file_in:
                self.table_info.append(json.loads(line))

    def connect_and_query(self, query):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        cur.execute(query)
        res = cur.fetchall()
        con.close()

        return res

    def find_json_table(self, table_id):
        for table in self.table_info:
            if table['id'] == table_id:
                return table

    def find_col_names(self, table_id):
        return self.find_json_table(table_id)['header']

    def extract_col_names(self, query):
        sel_part = query.split("FROM")[0]
        col_inds = re.findall('col(\\d)', sel_part)
        col_names = self.find_col_names(self.extract_table_id(query))
        return tuple(map(lambda x: col_names[int(x)], col_inds))

    @staticmethod
    def extract_table_id(query):
        try:
            extracted_table_id = re.search('FROM\\stable_(\\w*)[\\s|;]', query).group(1)
            extracted_table_id = extracted_table_id.replace("_", "-")
        except AttributeError as e:
            raise AttributeError(f"TableId could not be extracted from {query}")

        return extracted_table_id

    @staticmethod
    def first_row_to_header(df):
        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header

        return df

    def query_with_col_names(self, query):
        res = self.connect_and_query(query)
        col_names = self.extract_col_names(query)
        res.insert(0, tuple(col_names))

        query_res_df = pd.DataFrame(res)
        return self.first_row_to_header(query_res_df)

    def select_all(self, table_id):
        sql_table_id = f"table_{table_id.replace('-', '_')}"
        content = self.connect_and_query(f"SELECT * FROM {sql_table_id};")
        col_names = self.find_col_names(table_id)

        content.insert(0, tuple(col_names))
        query_res_df = pd.DataFrame(content)

        return self.first_row_to_header(query_res_df)


if __name__ == '__main__':
    # Paths will work if working directory is the directory of this file
    WIKISQL_DB_PATH = "../../../storage/datasets/wiki_sql/raw/train.db"
    WIKISQL_JSON_PATH = "../../../storage/datasets/wiki_sql/raw/train.tables.jsonl"
    QUERIES_PATH = "../../../storage/datasets/wiki_sql/raw/train.jsonl"

    wiki_sql = WikiSqlController(WIKISQL_DB_PATH, WIKISQL_JSON_PATH)
    # print(wiki_sql.query_with_col_names("SELECT col1 FROM table_1_10007452_3;"))
    print(wiki_sql.extract_col_names("SELECT col1, col2 FROM table_1_10007452_3;", ))
