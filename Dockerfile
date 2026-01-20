FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV BOLTZ_USE_CUE_OPS=0

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python-is-python3 \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

# Install deps that may pull torch
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Install Boltz
RUN python -m pip install --no-cache-dir \
    git+https://github.com/jwohlwend/boltz.git@cb04aeccdd480fd4db707f0bbafde538397fa2ac

# FORCE torch + lightning LAST (NO deps)
RUN python -m pip uninstall -y torch torchvision torchaudio && \
    python -m pip install --no-cache-dir --no-deps torch==2.9.1 && \
    python -m pip install --no-cache-dir --no-deps pytorch-lightning==2.5.0 && \
    python -m pip install --no-cache-dir --no-deps torchmetrics==1.8.2

# Sanity check (Docker-safe)
RUN python -c "import torch, pytorch_lightning; \
print('Torch:', torch.__version__); \
print('Lightning:', pytorch_lightning.__version__); \
assert torch.__version__.startswith('2.9.1'); \
assert pytorch_lightning.__version__ == '2.5.0'; \
print('ENV MATCHES VM (semver) ✅')"

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
