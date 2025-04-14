FROM python:3.11-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml setup.py README.md uv.lock ./
COPY structa/ ./structa/

RUN uv pip install --system build
RUN uv build --wheel
RUN mkdir -p /app/wheels
RUN mv dist/*.whl /app/wheels/

FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

RUN useradd --create-home structa_user

# Switch to the non-root user
WORKDIR /home/structa_user
USER structa_user

# Copy wheels
COPY --from=builder --chown=structa_user:structa_user /app/wheels /home/structa_user/wheels

# Create a virtual environment, install pip into it, then install the package
RUN uv venv /home/structa_user/venv && \
    /home/structa_user/venv/bin/python -m ensurepip --upgrade && \
    /home/structa_user/venv/bin/python -m pip install --upgrade pip && \
    /home/structa_user/venv/bin/python -m pip install /home/structa_user/wheels/*.whl && \
    rm -rf /home/structa_user/wheels

# Set the PATH to include the virtual environment's bin directory
ENV PATH="/home/structa_user/venv/bin:${PATH}"

# Set the entrypoint to the structa command
ENTRYPOINT ["structa"]
CMD ["--help"]
