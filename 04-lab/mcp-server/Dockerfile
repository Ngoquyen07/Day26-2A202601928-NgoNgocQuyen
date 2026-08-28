# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies. This project is a single-file app, not an
# installable Python package.
RUN pip install --no-cache-dir "fastmcp>=2.12.4" "httpx>=0.28.1" "mcp[cli]>=1.16.0" "uvicorn>=0.27.0"

# Copy application code
COPY weather.py ./

# Default local HTTP port; Cloud Run can override it with PORT.
EXPOSE 8085

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "weather.py"]
