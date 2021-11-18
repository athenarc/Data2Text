from fastapi import APIRouter, Depends

from app.backend.controller.shared_objects import get_query_explainer

router = APIRouter()


@router.get("/tables")
def available_tables(query_explainer=Depends(get_query_explainer)):
    return {"tables": query_explainer.db_controller.get_table_names()}


@router.get("/tables/{table_name}")
async def table_preview(table_name: str, query_explainer=Depends(get_query_explainer)):
    return {"table_sample": query_explainer.db_controller.preview_table(table_name)}
