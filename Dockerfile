FROM python:3.13-slim as base

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install --no-install-recommends -y \
  build-essential \
  make \
  curl \
  cron \
  procps \
  git \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install --no-cache -U pip setuptools git+https://github.com/celery/django-celery-beat.git \
    && rm -rf /root/.cache/pip \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && touch /var/log/cron.log

COPY ./pyproject.toml ./poetry.loc[k] /opt/api/

WORKDIR /opt/project/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-cache --no-ansi --no-interaction --only main \
    && poetry cache clear pypi --all

COPY ./entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh
ENTRYPOINT ["/opt/entrypoint.sh"]

FROM base as local

RUN poetry install --no-root --no-cache --no-ansi --no-interaction --with dev \
    && poetry cache clear pypi --all

FROM base as live

COPY ./project /opt/project