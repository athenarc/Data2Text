from fastapi import APIRouter
from pydantic import BaseModel

from app.backend.controller.shared_objects import query_explainer

router = APIRouter()


class Query(BaseModel):
    query: str


@router.post("/explain_query")
def explain_query(query: Query):
    return {"explanation": query_explainer.explain_query_results(query.query)}
