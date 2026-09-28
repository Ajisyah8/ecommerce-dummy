#!/bin/sh
set -eu

envsubst < /mnt/config/odoo.conf > /tmp/odoo-migrate.conf

database_name="${POSTGRES_DB}"
modules="${ODOO_UPDATE_MODULES:-ecommerce_custom}"

until pg_isready -h db -p 5432 -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null 2>&1; do
    sleep 2
done

set -- python /mnt/odoo/odoo-bin \
    --config=/tmp/odoo-migrate.conf \
    --database="${database_name}" \
    --stop-after-init

if [ -n "${ODOO_INIT_MODULES:-}" ]; then
    set -- "$@" --init="${ODOO_INIT_MODULES}"
else
    set -- "$@" --update="${modules}"
fi

exec "$@"
