from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.backend.controller.shared_objects import get_query_explainer

router = APIRouter()


class Query(BaseModel):
    query: str


@router.post("/explain_query")
def explain_query(query: Query, query_explainer=Depends(get_query_explainer)):
    return {"explanation": query_explainer.explain_query_results(query.query)}
