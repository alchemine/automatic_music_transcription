# Use the base image
FROM python:3.12-slim-bookworm

# Set the timezone to Asia/Seoul
ENV TZ Asia/Seoul

# Production(ENV=prd) or development(ENV=dev) or local(ENV=local) environment
ARG ENV=local
ENV ENV=$ENV

# Set project directory
ENV PROJECT_ROOT=/app
ENV PYTHONPATH=${PROJECT_ROOT}
WORKDIR ${PROJECT_ROOT}

# Install dependencies
COPY requirements.txt ${PROJECT_ROOT}/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy configuration files
COPY config/engine.yaml ${PROJECT_ROOT}/config/engine.yaml
COPY config/service.${ENV}.yaml ${PROJECT_ROOT}/config/service.yaml

# Copy source files
COPY src ${PROJECT_ROOT}/src

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Change ownership of the project directory
RUN chown -R appuser:appuser ${PROJECT_ROOT}

# Switch to non-root user
USER appuser