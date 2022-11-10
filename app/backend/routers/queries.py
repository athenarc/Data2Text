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

    class Config:
        schema_extra = {
            "example": {
                "conn_url": "postgresql+asyncpg://user:password@postgres_host:port/cordis",
                "query": "SELECT count(*) FROM projects",
                "nl_query": "Show me the number of projects"
            }
        }


@router.post("/qr2t_back/verbalise_query", tags=["QR2T"])
async def explain_query(query: Query, query_explainer=Depends(get_query_explainer)):
    """
    **Verbalise the results of a query**
    Currently supporting Postgres, MySQL, sqlite

    - **conn_url**: The connection string of the database (needed for re-executing the query after we process it)
    - **query**: The query in SQL
    - **nl_query (Optional)**: The query in natural language

    **Returns** a string which is the verbalisation of the results of the given query
    """
    pick_database_interface(query.conn_url, query_explainer)
    return {"explanation": await query_explainer.explain_query_results(query.conn_url, query.query, query.nl_query)}
