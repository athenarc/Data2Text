import sqlite3

import pandas as pd
from annotator import Annotation, Annotator
from termcolor import colored


def user_confirm_output(output):
    print()
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.width', 1_000):
        print(output)
    answer = ""
    while answer != "y" and answer != "n":
        answer = input(colored("> Is the above output expected (y/n): ", color="green"))
    print()
    return answer == "y"


class AnnotatorView:
    def __init__(self, db_path, table_info_path, queries_path, json_save_path):
        self.annotator = Annotator(db_path, table_info_path, queries_path, json_save_path)

        # Initial logging to make sure that the configuration is correct
        self.show_welcome_message()
        self.show_settings(db_path, table_info_path, queries_path, json_save_path)

    def annotation_loop(self):
        exit_annotation = False

        while not exit_annotation:
            # Step 1: Propose and accept a table
            print(colored("####### Step 1: Table Proposal #######", color='cyan'))
            while True:
                table_id, full_table = self.annotator.propose_table()
                sql_table_id = f"table_{table_id.replace('-', '_')}"
                if user_confirm_output(full_table):
                    break

            # Step 2: Ask the user to write a query
            print(colored("####### Step 2: Query Proposal #######", color='cyan'))
            self.show_query_suggestions(self.annotator.get_query_suggestions(table_id))
            while True:
                query = input("> Query (use col indexes and table_id): ")
                query = query.replace("table_id", sql_table_id)

                print(f"> Running query: {query}")
                try:
                    res = self.annotator.execute_input_query(query)
                except (AttributeError, SyntaxError, sqlite3.OperationalError):
                    print(colored("> Input query could not be parsed. Check the syntax and retry.\n", color='red'))
                    continue
                if user_confirm_output(res):
                    break

            # Step 3: Ask the user to describe the query
            print(colored("####### Step 3: Query Description #######", color='cyan'))
            while True:
                desc_query = input("> Query description: ")
                if user_confirm_output(desc_query):
                    break

            # Step 4: Ask the user to describe the results of the query
            print(colored("####### Step 4: Results Description #######", color='cyan'))
            while True:
                desc_results = input("> Results description: ")
                if user_confirm_output(desc_results):
                    break

            # Step 5: Create and save the annotation
            print(colored("####### Step 5: Save Annotation #######", color='cyan'))
            annotation = Annotation(table_id, query, desc_query, desc_results, res)
            self.show_annotation(table_id, query, desc_query, desc_results, res)
            self.annotator.save_annotations(annotation)

            # Step 6: Check if finished
            exit_msg = input(colored(f"Total annotations: {self.annotator.get_annotations_numb()}. "
                                     f"Would you like to exit? (y/n)", color='green'))
            exit_annotation = exit_msg == "y"

    @staticmethod
    def show_welcome_message():
        print(colored("\n"
                      "############################################\n"
                      "              WikiSQL Annotator             \n"
                      "############################################\n"
                      , color="green"))

    def show_settings(self, db_path, table_info_path, queries_path, json_save_path):
        print(colored("> Annotator configuration:", color='yellow'))
        print(colored(f"\t* Database: {db_path}", color='yellow'))
        print(colored(f"\t* Table info: {table_info_path}", color='yellow'))
        print(colored(f"\t* Queries: {queries_path}", color='yellow'))
        print(colored(f"\t* Annotation storage: {json_save_path}", color='yellow'))
        print(colored(f"\t* Annotations so far: {self.annotator.get_annotations_numb()}", color="cyan"))
        print()

    @staticmethod
    def show_annotation(table_id, query, desc_query, desc_results, res):
        print("> The following annotation will be stored:")
        print(f"\t* Table Id: {table_id}")
        print(f"\t* Query: {query}")
        print(f"\t* Query Description: {desc_query}")
        print(f"\t* Results Description: {desc_results}")
        print(f"\t* Result rows: {len(res)}")
        input("> Press enter to save...")

    @staticmethod
    def show_query_suggestions(suggestions):
        print("WikiSQL original queries:")
        for suggestion in suggestions:
            print(f"\t* {suggestion}")
        print()


if __name__ == '__main__':
    # Paths will work if working directory is the directory of this file
    WIKISQL_DB_PATH = "../../../storage/datasets/wiki_sql/raw/train.db"
    WIKISQL_JSON_PATH = "../../../storage/datasets/wiki_sql/raw/train.tables.jsonl"
    QUERIES_PATH = "../../../storage/datasets/wiki_sql/raw/train.jsonl"
    ANNOTATION_STORAGE_PATH = "../../../storage/datasets/wiki_sql/annotations/train.json"
    annotator = AnnotatorView(WIKISQL_DB_PATH, WIKISQL_JSON_PATH, QUERIES_PATH, ANNOTATION_STORAGE_PATH)
    annotator.annotation_loop()
