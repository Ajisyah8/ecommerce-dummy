#!/bin/sh
set -eu

envsubst < /mnt/config/odoo.conf > /tmp/odoo.conf

exec python /mnt/odoo/odoo-bin \
  --config=/tmp/odoo.conf \
  --http-port="${ODOO_HTTP_PORT}"
