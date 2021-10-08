import logging

import uvicorn
from controller.shared_objects import init_shared_objects
from fastapi import FastAPI
from routers.add_routes import initialize_routes

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

app = FastAPI()
initialize_routes(app)


@app.get("/health")
def health_check():
    return {"message": "App has initialised and is running"}


def main():
    uvicorn.run("app.backend.main:app", host='0.0.0.0', port=4557,
                reload=True, debug=True, workers=1, reload_dirs=["app/backend"],)


if __name__ == "__main__":
    main()
