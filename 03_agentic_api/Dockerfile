# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy your dependency management files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to install packages globally inside the container (since it's already isolated)
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-root

# Copy the rest of your application code
COPY . .

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Command to start the FastAPI server
CMD ["uvicorn", "03_agentic_api.app.main:app", "--host", "0.0.0.0", "--port", "8080"]