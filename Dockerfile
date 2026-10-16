FROM node:22-bookworm-slim AS node

FROM python:3.12-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 UV_LINK_MODE=copy
RUN apt-get update && apt-get install -y --no-install-recommends \
        git zip unzip tar nano vim-tiny curl ca-certificates procps less openssh-client \
        build-essential jq ripgrep tini \
    && rm -rf /var/lib/apt/lists/*

# Node + the Claude CLI. The real binary is hidden behind a shim that enforces usage limits.
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && npm install -g @anthropic-ai/claude-code \
    && ln -sf "$(readlink -f /usr/local/bin/claude)" /opt/claude-real \
    && rm /usr/local/bin/claude

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY backend ./backend
COPY frontend ./frontend
RUN install -m 755 backend/shim.py /usr/local/bin/claude \
    && chmod -R a+rX /app

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 3000
ENTRYPOINT ["tini", "--"]
CMD ["python", "-m", "backend.main"]
