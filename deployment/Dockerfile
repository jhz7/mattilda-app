# Use official Python 3.12 slim image (optimized for size)
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Set environment variables to buffer logs for better Docker logging
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for PostgreSQL and performance
RUN apt-get update && apt-get install -y \
  gcc \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*


# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set non-root user for security
RUN useradd -m botuser
USER botuser

# Copy application code
COPY --chown=botuser . .

# Expose FastAPI default port
EXPOSE 8000

# Run FastAPI app using Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
