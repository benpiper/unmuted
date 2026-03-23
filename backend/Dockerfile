FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install ffmpeg which is required for video sequence extraction
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency mappings
COPY pyproject.toml ./

# Install dependencies using uv into the system environment
RUN uv pip install --system -r pyproject.toml

# Copy the rest of the application
COPY . .

# Expose backend port
EXPOSE 8000

# Start Uvicorn server on all interfaces
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
