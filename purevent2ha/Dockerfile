ARG BUILD_FROM=ghcr.io/home-assistant/python-base:3.11
FROM ${BUILD_FROM}

# Install base packages
RUN apk add --no-cache \
    git \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    openssh-client \
    udev \
    gcc \
    libc-dev

# Install Python packages
COPY rootfs/requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy app and daemon
COPY rootfs/app /app
COPY rootfs/usr/local/bin /usr/local/bin
COPY rootfs/etc/purevent2ha /etc/purevent2ha

# Make scripts executable
RUN chmod +x /usr/local/bin/*.sh

# Set working directory
WORKDIR /app

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run the app
CMD ["/usr/local/bin/startup.sh"]
