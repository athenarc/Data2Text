import sqlite3

from app.backend.inference import InferenceController
from app.backend.process_query import (DifficultyNotImplemented,
                                       execute_query_with_added_sel_cols,
                                       query_results_to_totto)
from app.backend.sqlite_interface import SqliteController


class QueryResultsExplainer:
    def __init__(self, db_path, cfg):
        self.sqlite_controller = SqliteController(db_path)
        self.inference_controller = InferenceController(cfg)

    def explain_query_results(self, query: str) -> str:
        try:
            query_res_in_totto = query_results_to_totto(
                execute_query_with_added_sel_cols(self.sqlite_controller, query)
            )
        except sqlite3.OperationalError as e:
            return f"ERROR: {e}"
        except DifficultyNotImplemented as e:
            return f"ERROR, Difficulty not implemented: {e}"

        print(query_res_in_totto)
        nl_explanation = self.inference_controller.inference(query_res_in_totto)

        return nl_explanation
