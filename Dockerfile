FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --upgrade pip

# Устанавливаем зависимости напрямую
RUN pip install fastapi uvicorn sqlalchemy asyncpg pydantic

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
