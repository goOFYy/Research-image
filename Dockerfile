FROM ghcr.io/goofyy/research-base-image:base-1

# Set working directory
WORKDIR /app

# Copy package.json to the image
COPY package.json .

# Install Node.js and npm
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js dependencies
RUN npm install
