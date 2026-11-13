FROM python:3.15-slim@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928

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
