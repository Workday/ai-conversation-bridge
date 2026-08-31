FROM python:3.14-slim@sha256:cae66f2ef0ec51a9891263eeee7f987dacf0a9879e8aa9353d5606e0530619a5

RUN useradd -m appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY main.py .

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Listen address is fixed at 8080 (Cloud Run default). $PORT in Config is for
# `python main.py` only; do not pass gcloud --port other than 8080.

# One worker with multiple threads: I/O-bound orchestration shares in-memory
# conversation state. Multiple workers would fragment STATE_BACKEND=memory.
# Timeout above ORCHESTRATOR_TIMEOUT (default 240) so typed failures return first.
CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "300", "main:app"]
