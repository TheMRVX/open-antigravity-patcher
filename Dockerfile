FROM python:3.12-slim

LABEL org.opencontainers.image.title="Open AG Patcher" \
      org.opencontainers.image.description="Open-source region lock bypass and patcher for Antigravity 2.0, IDE, CLI, and VS Code" \
      org.opencontainers.image.url="https://github.com/TheMRVX/open-antigravity-patcher" \
      org.opencontainers.image.source="https://github.com/TheMRVX/open-antigravity-patcher" \
      org.opencontainers.image.licenses="GPL-3.0"

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY main.py .
COPY patcher/ ./patcher/
COPY version.txt .
COPY README.md .
COPY LICENSE .

ENTRYPOINT ["python", "main.py"]
