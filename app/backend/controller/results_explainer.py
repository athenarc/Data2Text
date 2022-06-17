import logging
from typing import Optional

from app.backend.controller.inference import InferenceController
from app.backend.db.DbInterface import DbException, DbInterface
from app.backend.db.MySqlController import MySqlController
from app.backend.db.SqliteController import SqliteController
from app.backend.processing.process_query.difficulty_check import \
    DifficultyNotImplemented
from app.backend.processing.process_query.query_pipeline import \
    execute_transformed_query
from app.backend.processing.process_query_results import query_results_to_totto


class QueryResultsExplainer:
    def __init__(self, cfg):
        # self.db_controller: DbInterface = MySqlController(cfg.DB.CREDENTIALS)  # Could be sqlite, MySQL currently
        self.db_controller: Optional[DbInterface] = None
        self.inference_controller = InferenceController(cfg)

    def set_db_controller(self, db_interface: DbInterface):
        self.db_controller = db_interface

    async def explain_query_results(self, conn_url: str, query: str, nl_query: Optional[str] = "") -> str:
        try:
            query_res_in_totto = query_results_to_totto(
                await execute_transformed_query(conn_url, self.db_controller, query),
                nl_query
            )
        except DbException as e:
            return f"DB ERROR: {e}"
        except DifficultyNotImplemented as e:
            return f"ERROR, Difficulty not implemented: {e}"

        logging.debug(query_res_in_totto)
        nl_explanation = self.inference_controller.inference(query_res_in_totto)

        return nl_explanation
