# This dockerfile creates the backend image (app/backend/). However, it needs modules like
# modeling, utils, etc. so I have moved it to the root of the project.
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN pip3 install torch==1.9.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

COPY app/backend/requirements.txt .
RUN pip install -r requirements.txt

COPY app/backend/ app/backend/
COPY modeling/ modeling/
COPY solver/ solver/
COPY utils/ utils/

CMD ["python", "-m", "app.backend.main", "--config_file", "app/backend/configs/prod.yaml"]

# Build must be run from project root directory
# docker build -t d2t-back:latest -f app/backend/Dockerfile .

# Run
# docker run -v /home/mikexydas/PycharmProjects/Data2Text/storage:/app/storage -p 4557:4557 e9f44746992f
