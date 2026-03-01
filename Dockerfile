FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir fastapi uvicorn pytest pydantic requests

EXPOSE 8000
CMD ["uvicorn", "arviva_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
