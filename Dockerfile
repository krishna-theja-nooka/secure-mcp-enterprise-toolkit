FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TOOLKIT_HOME=/data
WORKDIR /app
COPY requirements.lock pyproject.toml ./
RUN python -m pip install --no-cache-dir -r requirements.lock
COPY toolkit ./toolkit
RUN python -m pip install --no-deps --no-build-isolation . \
    && useradd --uid 10001 --create-home toolkit \
    && mkdir /data && chown toolkit:toolkit /data
USER toolkit
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"
CMD ["python", "-m", "uvicorn", "toolkit.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
