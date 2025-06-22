# Stage 1: Base build stage
FROM python:3.13-slim AS builder

LABEL maintainer="conduit"

# Create the conduit directory
RUN mkdir /conduit

# Set the working directory
WORKDIR /conduit

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies first for caching benefit
RUN pip install --upgrade pip
COPY requirements.txt /conduit/
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.13-slim

RUN useradd -m -r conduituser && \
   mkdir /conduit && \
   chown -R conduituser /conduit

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set the working directory
WORKDIR /conduit

# Copy application code
COPY --chown=conduituser:conduituser . .

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER conduituser

# Expose the conduitlication port
EXPOSE 8000

# Make entry file executable
RUN chmod +x  /conduit/entrypoint.prod.sh

# Start the conduitlication using Gunicorn
CMD ["/conduit/entrypoint.prod.sh"]
