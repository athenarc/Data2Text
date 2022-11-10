from fastapi import APIRouter, Depends

from app.backend.controller.shared_objects import get_query_explainer
from app.backend.db.database_router import pick_database_interface

router = APIRouter()


@router.get("/qr2t_back/tables", tags=["DB Info"])
async def available_tables(url_conn: str, query_explainer=Depends(get_query_explainer)):
    pick_database_interface(url_conn, query_explainer)
    return {"tables": await query_explainer.db_controller.get_table_names(url_conn)}


@router.get("/qr2t_back/tables/{table_name}", tags=["DB Info"])
async def table_preview(url_conn: str, table_name: str, query_explainer=Depends(get_query_explainer)):
    pick_database_interface(url_conn, query_explainer)
    return {"table_sample": await query_explainer.db_controller.preview_table(url_conn, table_name)}
