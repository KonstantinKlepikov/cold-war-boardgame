FROM python:3.8.12

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y git curl && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./app /app/
WORKDIR /app/
ENV PYTHONPATH=/app/

# Allow installing dev dependencies to run tests
RUN bash -c "poetry install --no-root"

ENTRYPOINT ["uvicorn"]
CMD ["app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]