import json
import random
from collections import defaultdict

from db_interface import WikiSqlController


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
        full_table.columns = [f"{ind}.{col}" for (ind, col) in enumerate(full_table.columns)]
        return table_id, full_table

    def save_annotations(self, table_id, query, desc_query, desc_results, result_df):
        annotation = {
            'table_id': table_id,
            'query': query,
            'query_description': desc_query,
            'results_description': desc_results,
            'result': result_df.to_csv()
        }
        self.annotations.append(annotation)
        with open(self.json_save_path, 'w') as fp:
            json.dump(self.annotations, fp)

    def get_annotations_numb(self):
        return len(self.annotations)
