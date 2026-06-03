FROM python:3.11-alpine

LABEL maintainer="awspracttical57"
LABEL description="Week 2 Mini Project - Devops Dashboard"
LABEL version="2.0"

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel
COPY app.py .

RUN adduser -D -u 1000 appuser
USER appuser

ENV PORT=8000
EXPOSE 8000

CMD ["python3", "app.py"]