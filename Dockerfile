# Use the official Python 3.12 slim image as the base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Poetry and Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to the latest version and suppress root user warning
RUN pip install --upgrade pip --root-user-action=ignore

# Install Poetry with a specific version for consistency
RUN pip install poetry==1.8.3 --root-user-action=ignore

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock /app/

# Configure Poetry to not create virtual environments and install main dependencies
RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi

# Copy the application code
COPY . /app

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]