From python:3.11 AS builder

WORKDIR /app
COPY app.py .

FROM python:3.11-slim AS production

WORKDIR /app

COPY --from=builder /app/app.py .

ENV PORT=8000

CMD ["python3","app.py"]
