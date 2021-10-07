FROM python:3.8-slim

WORKDIR frontend/

COPY . .
RUN pip install -r requirements.txt

RUN chmod +x ./startup.sh
ENTRYPOINT ["/bin/bash", "./startup.sh"]

# Build
# docker build -t d2t-front:latest .

# Run
# docker run -p 8501:8501 048f82d40346
