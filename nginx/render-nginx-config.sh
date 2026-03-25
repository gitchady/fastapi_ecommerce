#!/bin/sh
set -eu

template_dir="/etc/nginx/custom-templates"
target="/etc/nginx/conf.d/default.conf"
cert_dir="/etc/letsencrypt/live/${NGINX_SERVER_NAME}"
fullchain="${cert_dir}/fullchain.pem"
privkey="${cert_dir}/privkey.pem"

template="${template_dir}/http-only.conf.tpl"
if [ -f "$fullchain" ] && [ -f "$privkey" ]; then
    template="${template_dir}/https.conf.tpl"
fi

export APP_PORT APP_UPSTREAM_HOST NGINX_CLIENT_MAX_BODY_SIZE NGINX_SERVER_NAME
envsubst '${APP_PORT} ${APP_UPSTREAM_HOST} ${NGINX_CLIENT_MAX_BODY_SIZE} ${NGINX_SERVER_NAME}' < "$template" > "$target"
