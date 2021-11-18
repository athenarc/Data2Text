from app.backend.controller.arg_parsing import get_model_config
from app.backend.controller.results_explainer import QueryResultsExplainer

cfg = get_model_config(name="FastAPI Data2Text Endpoint")
query_explainer = QueryResultsExplainer(cfg)


def get_cfg():
    return cfg


def get_query_explainer():
    return query_explainer
