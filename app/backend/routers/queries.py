from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.backend.controller.shared_objects import get_query_explainer
from app.backend.db.database_router import pick_database_interface

router = APIRouter()


class Query(BaseModel):
    conn_url: str
    query: str
    nl_query: Optional[str] = ""


@router.post("/qr2t_back/explain_query")
async def explain_query(query: Query, query_explainer=Depends(get_query_explainer)):
    pick_database_interface(query.conn_url, query_explainer)
    return {"explanation": await query_explainer.explain_query_results(query.conn_url, query.query, query.nl_query)}
