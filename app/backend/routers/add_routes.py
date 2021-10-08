from app.backend.routers import queries, tables


def initialize_routes(app):
    app.include_router(queries.router)
    app.include_router(tables.router)


# !!!!!!!!!!!!!!!!!!!!!!!!
# Add config file input (with db path)
