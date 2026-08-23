FROM python:3.11-slim

# Install system dependencies needed by proxsuite (OpenMP)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your project files
COPY . .

# Default command: run your script
CMD ["python", "RS_II_HW2_Ex3.py"]
