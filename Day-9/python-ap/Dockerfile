# Use official Python slim image — smaller than full python
FROM python:3.11-slim

# Set metadata
LABEL maintainer="awspractical57"
LABEL description="DevOps journey Python API"

# Set working directory
WORKDIR /app

# Set environment variable
ENV PORT=8000

# Copy application code
COPY app.py .

# Expose the port
EXPOSE 8000

# Run the application
CMD ["python3", "app.py"]
