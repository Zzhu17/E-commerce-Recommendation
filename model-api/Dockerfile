FROM python:3.11-slim
RUN groupadd --system app && useradd --system --gid app --uid 10001 --home /app app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN chown -R app:app /app
USER app
EXPOSE 8000
ENV MODEL_VERSION=v2026.01
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
