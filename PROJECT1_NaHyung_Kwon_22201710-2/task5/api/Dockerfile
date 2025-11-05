FROM python:3.13-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8080
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8080"]

