import json
import random
from collections import defaultdict

import pandas as pd
from db_interface import WikiSqlController


def user_confirm_output(output):
    print()
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.width', 1_000):
        print(output)
    answer = ""
    while answer != "yes" and answer != "no":
        answer = input("> Is the above output expected (yes/no): ")

    return answer == "yes"


class Annotator:
    def __init__(self, db_path, table_info_path, queries_path, json_save_path):
        self.wiki_interface = WikiSqlController(db_path, table_info_path)
        self.query_suggestions = self.initialize_query_suggestions(queries_path)
        self.table_pool = self.initialize_table_pool(table_info_path)
        self.json_save_path = json_save_path

        with open(json_save_path, "r") as fp:
            self.annotations = json.load(fp)

    @staticmethod
    def initialize_query_suggestions(queries_path):
        queries = []
        with open(queries_path) as file_in:
            for line in file_in:
                queries.append(json.loads(line))

        query_suggestions = defaultdict(list)
        for query in queries:
            query_suggestions[query['table_id']].append(query['question'])

        return query_suggestions

    @staticmethod
    def initialize_table_pool(table_info_path):
        tables = []
        with open(table_info_path) as file_in:
            for line in file_in:
                tables.append(json.loads(line))

        return [table['id'] for table in tables]

    def execute_input_query(self, input_query):
        query_res = self.wiki_interface.query_with_col_names(input_query)

        return query_res

    def propose_table(self):
        table_id = random.choice(self.table_pool)
        full_table = self.wiki_interface.select_all(table_id)

        return table_id, full_table

    def save_annotations(self, table_id, query, desc, result_df):
        annotation = {
            'table_id': table_id,
            'query': query,
            'description': desc,
            'result': result_df.to_csv()
        }
        self.annotations.append(annotation)
        with open(self.json_save_path, 'w') as fp:
            json.dump(self.annotations, fp)

    def annotation_loop(self):
        exit_annotation = False
        while not exit_annotation:
            # Step 1: Propose and accept a table
            while True:
                table_id, full_table = self.propose_table()
                sql_table_id = f"table_{table_id.replace('-', '_')}"
                if user_confirm_output(full_table):
                    break

            # Step 2: Ask the user to write a query
            while True:
                query = input("> Query (use col indexes and table_id): ")
                query = query.replace("table_id", sql_table_id)

                print(query)
                res = self.execute_input_query(query)
                if user_confirm_output(res):
                    break

            # Step 3: Ask the user to describe the query
            while True:
                desc = input("> Query description: ")
                if user_confirm_output(desc):
                    break

            # Step 4: Save the annotation
            self.save_annotations(table_id, query, desc, res)

            print("> Annotation saved.")
            print()


if __name__ == '__main__':
    # Paths will work if working directory is the directory of this file
    WIKISQL_DB_PATH = "../../../storage/datasets/wiki_sql/raw/train.db"
    WIKISQL_JSON_PATH = "../../../storage/datasets/wiki_sql/raw/train.tables.jsonl"
    QUERIES_PATH = "../../../storage/datasets/wiki_sql/raw/train.jsonl"
    ANNOTATION_STORAGE_PATH = "../../../storage/datasets/wiki_sql/annotations/train.json"
    annotator = Annotator(WIKISQL_DB_PATH, WIKISQL_JSON_PATH, QUERIES_PATH, ANNOTATION_STORAGE_PATH)
    annotator.annotation_loop()
