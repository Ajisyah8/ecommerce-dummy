FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        gettext-base \
        libldap2-dev \
        libjpeg62-turbo-dev \
        libpq-dev \
        libsasl2-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        postgresql-client \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY odoo/requirements.txt /tmp/odoo-requirements.txt
RUN pip install --no-cache-dir -r /tmp/odoo-requirements.txt

COPY docker/entrypoint.sh /usr/local/bin/project-odoo-entrypoint
COPY docker/migrate.sh /usr/local/bin/project-odoo-migrate
RUN chmod +x /usr/local/bin/project-odoo-entrypoint /usr/local/bin/project-odoo-migrate \
    && useradd --create-home --home-dir /var/lib/odoo --shell /usr/sbin/nologin odoo

USER odoo
WORKDIR /mnt/odoo
