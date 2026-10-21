#!/bin/sh
set -eu

: "${HOST:?Set HOST to the Render Postgres internal hostname}"
: "${USER:?Set USER to the Render Postgres username}"
: "${PASSWORD:?Set PASSWORD to the Render Postgres password}"
: "${ODOO_ADMIN_PASSWD:?Set ODOO_ADMIN_PASSWD as a Render secret}"

ODOO_DATABASE="${ODOO_DATABASE:-resbook_db}"
ODOO_INIT="${ODOO_INIT:-base,resource_booking}"
ODOO_WITHOUT_DEMO="${ODOO_WITHOUT_DEMO:-False}"
PORT="${PORT:-10000}"
PGPORT="${PGPORT:-5432}"

umask 077
odoo_config="$(mktemp /tmp/odoo-render.XXXXXX.conf)"
cat > "$odoo_config" <<EOF
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
data_dir = /var/lib/odoo
admin_passwd = $ODOO_ADMIN_PASSWD
db_host = $HOST
db_port = $PGPORT
db_user = $USER
db_password = $PASSWORD
db_name = $ODOO_DATABASE
http_interface = 0.0.0.0
http_port = $PORT
proxy_mode = True
EOF

export ODOO_RC="$odoo_config"
exec /entrypoint.sh "$@" -c "$odoo_config" -d "$ODOO_DATABASE" -i "$ODOO_INIT" --without-demo="$ODOO_WITHOUT_DEMO"
