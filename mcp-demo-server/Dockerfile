FROM python:3.14-slim@sha256:fb83750094b46fd6b8adaa80f66e2302ecbe45d513f6cece637a841e1025b4ca

RUN useradd -m appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY mock_data ./mock_data

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["python", "main.py"]
