FROM python:3.8-slim

WORKDIR frontend/

COPY . .
RUN pip install -r requirements.txt

RUN chmod +x ./startup.sh

EXPOSE 8501

ENTRYPOINT ["/bin/bash", "./startup.sh", "config/prod.yaml"]
#CMD streamlit run streamlit.py

# Build
# docker build -t d2t-front:latest .

# Run
# docker run -p 8501:8501 048f82d40346
