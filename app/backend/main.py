import logging

import uvicorn
from fastapi import FastAPI

from app.backend.controller.shared_objects import cfg
from app.backend.routers.add_routes import initialize_routes

# logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

app = FastAPI(openapi_url=f"/{cfg.FASTAPI.API_ROOT}/openapi.json",
              docs_url=f"/{cfg.FASTAPI.API_ROOT}/docs",
              redoc_url=f"/{cfg.FASTAPI.API_ROOT}/redoc")
initialize_routes(app)


@app.get("/qr2t_back/health")
def health_check():
    return {"message": "App has initialised and is running"}


def main():
    uvicorn.run("app.backend.main:app",
                host=cfg.FASTAPI.HOST,
                port=cfg.FASTAPI.PORT,
                reload=cfg.FASTAPI.RELOAD,
                debug=cfg.FASTAPI.DEBUG,
                workers=cfg.FASTAPI.WORKERS,
                reload_dirs=["app/backend"])


if __name__ == "__main__":
    main()
