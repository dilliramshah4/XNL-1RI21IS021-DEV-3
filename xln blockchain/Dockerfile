# Use official Python image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy the script
COPY blockchain-logger.py /app/

# Install dependencies
RUN pip install web3 requests

# Set environment variables (default values, override in Kubernetes)
ENV GANACHE_RPC_URL=http://localhost:8545
ENV GANACHE_PRIVATE_KEY=""

# Run script
CMD ["python3", "blockchain-logger.py"]
