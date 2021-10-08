from fastapi import APIRouter

from app.backend.controller.shared_objects import query_explainer

router = APIRouter()


@router.get("/tables")
def available_tables():
    return {"tables": query_explainer.sqlite_controller.get_table_names()}


@router.get("/tables/{table_name}")
async def table_preview(table_name: str):
    return {"table_sample": query_explainer.sqlite_controller.preview_table(table_name)}
