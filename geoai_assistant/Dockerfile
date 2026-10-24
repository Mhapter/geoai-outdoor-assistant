FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt torch

COPY . .

ENV GEOAI_MODEL_ID="Qwen/Qwen2.5-3B-Instruct"
ENV GEOAI_LOAD_SLM="1"

EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
