import logging

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from app.backend.arg_parsing import get_model_config
from app.backend.query_results_explainer import QueryResultsExplainer

app = FastAPI()
cfg = get_model_config(name="FastAPI Data2Text Endpoint")
query_explainer = QueryResultsExplainer("storage/app_data/tables.db", cfg)

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


class Query(BaseModel):
    query: str


@app.get("/health")
def health_check():
    return {"message": "App has initialised and is running"}


@app.get("/tables")
def available_tables():
    return {"tables": query_explainer.sqlite_controller.get_table_names()}


@app.get("/tables/{table_name}")
async def table_preview(table_name: str):
    return {"table_sample": query_explainer.sqlite_controller.preview_table(table_name)}


@app.post("/explain_query")
def explain_query(query: Query):
    return {"explanation": query_explainer.explain_query_results(query.query)}


def main():
    uvicorn.run("app.backend.api:app", host='0.0.0.0', port=4557,
                reload=True, debug=True, workers=3, reload_dirs=["app/backend"],)


if __name__ == "__main__":
    main()
