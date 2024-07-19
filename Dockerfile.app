# Use the official image as a base image
FROM stac-utils/stac-fastapi-pgstac

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.1.13

# Install system dependencies including GDAL and cmake
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    python3-dev \
    gdal-bin \
    libgdal-dev \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Set work directory
WORKDIR /app

# Copy the application code
COPY . .

# Install the Python dependencies
RUN python -m pip install -e .[server]
RUN pip install titiler.core titiler.pgstac