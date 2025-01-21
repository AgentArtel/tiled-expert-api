FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "tiled_ai_expert_endpoint:app", "--host", "0.0.0.0", "--port", "8001"]
