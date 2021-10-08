from app.backend.controller.arg_parsing import get_model_config
from app.backend.controller.results_explainer import QueryResultsExplainer

cfg = get_model_config(name="FastAPI Data2Text Endpoint")
query_explainer = QueryResultsExplainer(cfg)
