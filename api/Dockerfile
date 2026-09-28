FROM python:3.12-slim

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

# Copy dependency files and install first to leverage caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ .

# Change ownership to the non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (metadata only)
EXPOSE 8000

CMD ["python", "server.py"]
