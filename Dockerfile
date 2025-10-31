FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Set working directory
WORKDIR /workspace

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip3 install -r requirements.txt

# Copy project files
COPY . .

# Set Python path
ENV PYTHONPATH=/workspace:$PYTHONPATH

# Default command
CMD ["/bin/bash"]
