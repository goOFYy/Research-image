FROM ghcr.io/goofyy/research-base-image:base-2

RUN apt-get update && \
    apt-get install -y wget && \
    wget http://archive.ubuntu.com/ubuntu/pool/main/c/curl/curl_7.68.0-1ubuntu2.6_amd64.deb && \
    wget http://archive.ubuntu.com/ubuntu/pool/main/v/vim/vim_8.1.2269-1ubuntu5_amd64.deb && \
    dpkg -i curl_7.68.0-1ubuntu2.6_amd64.deb vim_8.1.2269-1ubuntu5_amd64.deb || apt-get install -f -y && \
    rm -f curl_7.68.0-1ubuntu2.6_amd64.deb vim_8.1.2269-1ubuntu5_amd64.deb && \
    rm -rf /var/lib/apt/lists/*

