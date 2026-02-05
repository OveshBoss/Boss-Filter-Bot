FROM python:3.9-slim

# ------------------ yeh line add karo ------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY repo /app

# Optional: upgrade pip (better practice)
RUN python -m pip install --upgrade pip

RUN if [ -f "/app/requirements.txt" ]; then pip install --no-cache-dir -r /app/requirements.txt; fi

# Baaki commands jo aapke pass hain (CMD, ENV etc.)
# Example:
# CMD ["python", "bot.py"]
