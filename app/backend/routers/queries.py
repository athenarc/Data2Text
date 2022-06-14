from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.backend.controller.shared_objects import get_query_explainer

router = APIRouter()


class Query(BaseModel):
    conn_url: str
    query: str
    nl_query: Optional[str] = ""


@router.post("/qr2t_back/explain_query")
async def explain_query(query: Query, query_explainer=Depends(get_query_explainer)):
    return {"explanation": await query_explainer.explain_query_results(query.conn_url, query.query, query.nl_query)}


@router.post("/qr2t_back/explain_query_placeholder")
async def explain_query_placeholder(query: Query, query_explainer=Depends(get_query_explainer)):
    return {"explanation": "This is a placeholder verbalisation of the query"}
