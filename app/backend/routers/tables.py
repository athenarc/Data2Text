from fastapi import APIRouter, Depends

from app.backend.controller.shared_objects import get_query_explainer

router = APIRouter()


@router.get("/qr2t_back/tables")
async def available_tables(url_conn: str, query_explainer=Depends(get_query_explainer)):
    return {"tables": await query_explainer.db_controller.get_table_names(url_conn)}


@router.get("/qr2t_back/tables/{table_name}")
async def table_preview(url_conn: str, table_name: str, query_explainer=Depends(get_query_explainer)):
    return {"table_sample": await query_explainer.db_controller.preview_table(url_conn, table_name)}
