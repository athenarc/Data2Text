import json
import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from db_interface import WikiSqlController


@dataclass
class Annotation:
    table_id: str
    query: str
    table_name: str
    query_description: str
    results_description: str
    result: Any
    difficulty: int = 1

    def __post_init__(self):
        # Transform the result pd.DataFrame to string
        self.result = self.result.to_csv()


class Annotator:
    def __init__(self, db_path, table_info_path, queries_path, json_save_path):
        self.wiki_interface = WikiSqlController(db_path, table_info_path)
        self.query_suggestions = self.initialize_query_suggestions(queries_path)
        self.table_pool = self.initialize_table_pool(table_info_path)
        self.json_save_path = json_save_path
        try:
            with open(json_save_path, "r") as fp:
                self.annotations = json.load(fp)
        except FileNotFoundError:
            self.annotations = []

    def initialize_table_pool(self, table_info_path):
        tables = []
        with open(table_info_path) as file_in:
            for line in file_in:
                tables.append(json.loads(line))
        return [table['id'] for table in tables if self.keep_non_sports_table(table)]

    @staticmethod
    def keep_non_sports_table(table):
        SPORTS_WORDS = ["game", "manufacturer", "position", "winner", "driver", "captain",
                        "player", "pick", "round", "tournament", "club", "result", "crowd",
                        "goals", "points", "lane"]
        col_names_concatenated = " ".join(table['header']).lower()
        return not any(x in col_names_concatenated for x in SPORTS_WORDS)

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

    def execute_input_query(self, input_query):
        query_res = self.wiki_interface.query_with_col_names(input_query)

        return query_res

    def propose_table(self):
        table_id = random.choice(self.table_pool)
        full_table = self.wiki_interface.select_all(table_id)
        full_table.columns = [f"{ind}.{col}" for (ind, col) in enumerate(full_table.columns)]
        return table_id, full_table

    def get_query_suggestions(self, table_id):
        return self.query_suggestions[table_id]

    def save_annotations(self, annotation: Annotation):
        self.annotations.append(annotation.__dict__)
        with open(self.json_save_path, 'w') as fp:
            json.dump(self.annotations, fp)

    def get_annotations_numb(self):
        return len(self.annotations)
