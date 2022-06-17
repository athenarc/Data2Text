import logging

from app.backend.controller.results_explainer import QueryResultsExplainer
from app.backend.db.MySqlController import MySqlController
from app.backend.db.SqliteController import SqliteController


def pick_database_interface(conn_url: str, query_explainer: QueryResultsExplainer):
    if "mysql" in conn_url:
        query_explainer.set_db_controller(MySqlController())
    elif "sqlite" in conn_url:
        query_explainer.set_db_controller(SqliteController())
    else:
        logging.error("Connection url does not use a known database (mysql, sqlite)")
