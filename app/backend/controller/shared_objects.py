from app.backend.controller.arg_parsing import get_model_config
from app.backend.controller.results_explainer import QueryResultsExplainer

cfg = None
query_explainer = None


def init_shared_objects():
    global cfg, query_explainer
    # Shared singleton objects. Kinda of an anti-pattern. Should be fixed.
    cfg = get_model_config(name="FastAPI Data2Text Endpoint")
    query_explainer = QueryResultsExplainer("storage/app_data/tables.db", cfg)
