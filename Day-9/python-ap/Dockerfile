# Use official Python slim image — smaller than full python
FROM python:3.11-alpine

# Set metadata
LABEL maintainer="awspractical57"
LABEL description="DevOps journey Python API"

# Set working directory
WORKDIR /app

# Set environment variable
ENV PORT=8000

# Upgrade pip package to fix known vulnerbilities
RUN pip install --upgrade pip wheel setuptools

# Copy application code
COPY app.py .


# Create non-root user
RUN adduser -D -u 1000 appuser
USER appuser

# Expose the port
EXPOSE 8000

# Run the application
CMD ["python3", "app.py"]
